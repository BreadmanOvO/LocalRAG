"""Executable cloud multi-agent orchestration with frozen model bindings."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict, dataclass, field, replace
from threading import BoundedSemaphore, RLock
from typing import Callable, Mapping, Sequence
from uuid import uuid4

from langchain_core.messages import HumanMessage, SystemMessage
from .team_scheduler import ModelCircuitBreaker, TeamStepScheduler, transient_error
from .team_plan import build_team_plan
from .error_details import serialize_exception

from agent_platform.integrations.multi_agent_config import (
    CloudAgentClient,
    CloudAgentSpec,
    CloudModelProfile,
    load_cloud_team_config,
    profile_matches_requirements,
    tier_rank,
)


ARCHITECTURES = {"direct", "hierarchical", "swarm", "adversarial", "heterogeneous", "graph"}
from agent_platform.personas.themes import THEME_LEADERS, THEME_ROLES, THEME_COORDINATORS, ROLE_RESPONSIBILITIES


@dataclass(frozen=True)
class TaskModelRequirements:
    """Requirements inferred from this run's goal, not from a role card."""

    capabilities: tuple[str, ...] = ()
    modalities: tuple[str, ...] = ()
    scenarios: tuple[str, ...] = ()


def _merged_values(*values: Sequence[str]) -> tuple[str, ...]:
    """Merge case-insensitively while retaining the first useful UI label."""
    merged: list[str] = []
    seen: set[str] = set()
    for group in values:
        for raw_value in group:
            value = str(raw_value or "").strip()
            normalized = value.casefold()
            if value and normalized not in seen:
                seen.add(normalized)
                merged.append(value)
    return tuple(merged)


def infer_task_model_requirements(
    goal: str,
    *,
    required_capabilities: Sequence[str] = (),
) -> TaskModelRequirements:
    """Extract deterministic modality signals and merge router requirements.

    This intentionally does not guess a model. It only turns explicit input
    formats into hard requirements so automatic routing can fail safely.
    """
    normalized = str(goal or "").casefold()
    capabilities = list(required_capabilities)
    modalities: list[str] = []
    scenarios: list[str] = []
    if any(token in normalized for token in ("图片", "图像", "截图", "image", "photo", "视觉")):
        capabilities.append("vision")
        modalities.append("image")
        scenarios.append("image-understanding")
    if any(token in normalized for token in ("表格", "table", "spreadsheet", "excel", "xlsx", "csv")):
        capabilities.append("table")
        modalities.append("table")
        scenarios.append("table-analysis")
    if any(token in normalized for token in ("pdf", "文档")):
        capabilities.append("document")
        modalities.append("pdf")
        scenarios.append("document-reading")
    return TaskModelRequirements(
        capabilities=_merged_values(capabilities),
        modalities=_merged_values(modalities),
        scenarios=_merged_values(scenarios),
    )


class ModelRoutingError(RuntimeError):
    """A safe-to-return error when an automatic model choice is impossible."""

    def __init__(self, agent_id: str, message: str, *, requirements: Mapping[str, object] | None = None) -> None:
        super().__init__(message)
        self.agent_id = agent_id
        self.requirements = dict(requirements or {})

    def public_details(self) -> dict[str, object]:
        return {"agent_id": self.agent_id, "requirements": self.requirements}


@dataclass(frozen=True)
class AgentModelBinding:
    """One immutable Agent-to-model selection for an individual team run."""

    agent_id: str
    display_name: str
    model: str
    model_profile: str
    selection_mode: str
    selection_reason: str
    spec: CloudAgentSpec = field(repr=False)

    def public(self) -> dict[str, str]:
        return {
            "agent_id": self.agent_id,
            "display_name": self.display_name,
            "model": self.model,
            "model_profile": self.model_profile,
            "selection_mode": self.selection_mode,
            "selection_reason": self.selection_reason,
        }


@dataclass(frozen=True)
class TeamModelSnapshot:
    """Immutable model choices for the lifetime of a room team."""

    bindings: tuple[AgentModelBinding, ...]

    def by_agent_id(self) -> dict[str, AgentModelBinding]:
        return {binding.agent_id: binding for binding in self.bindings}

    def public(self) -> list[dict[str, str]]:
        return [binding.public() for binding in self.bindings]

    def persistent(self) -> list[dict]:
        result = []
        for binding in self.bindings:
            spec = asdict(binding.spec)
            spec.pop("api_key", None)
            result.append({**binding.public(), "spec": spec})
        return result

    def merge(self, *snapshots: "TeamModelSnapshot") -> "TeamModelSnapshot":
        """Add newly participating Agents without replacing existing bindings."""
        merged = list(self.bindings)
        seen = {binding.agent_id for binding in merged}
        for snapshot in snapshots:
            for binding in snapshot.bindings:
                if binding.agent_id not in seen:
                    merged.append(binding)
                    seen.add(binding.agent_id)
        return TeamModelSnapshot(tuple(merged))


@dataclass(frozen=True)
class AgentTurn:
    agent_id: str
    display_name: str
    responsibility: str
    prompt: str
    content: str
    sequence: int
    model: str
    model_profile: str
    selection_mode: str
    selection_reason: str
    duration_ms: int = 0
    is_final: bool = False


@dataclass(frozen=True)
class TeamRunResult:
    architecture: str
    status: str
    turns: tuple[AgentTurn, ...]
    final: str


Invoker = Callable[[CloudAgentSpec, Sequence[object]], str]


class CloudTeamRuntime:
    """Run bounded team strategies with immutable room-level model bindings."""

    def __init__(
        self,
        agents: Mapping[str, CloudAgentSpec],
        profiles: Mapping[str, CloudModelProfile] | None = None,
        *,
        invoker: Invoker | None = None,
    ) -> None:
        enabled = {key: value for key, value in agents.items() if value.enabled}
        if not enabled:
            raise RuntimeError("No enabled cloud agents are configured")
        self.agents = enabled
        self._configured_agent_ids = set(agents)
        self._profiles = dict(profiles or self._profiles_from_agents(enabled))
        self._clients: dict[tuple[str, str, str, str, str], CloudAgentClient] = {}
        self._invoker = invoker or self._invoke_client
        self._semaphores: dict[tuple[str, str, str], BoundedSemaphore] = {}
        self._configuration_lock = RLock()
        self._circuit = ModelCircuitBreaker()

    @classmethod
    def from_config(cls, path=None, *, environ=None) -> "CloudTeamRuntime":
        configuration = load_cloud_team_config(path, environ=environ)
        return cls(configuration.agents, profiles=configuration.profiles)

    def restore_bindings(self, saved: list[dict]) -> TeamModelSnapshot:
        bindings = []
        for item in saved:
            original = dict(item["spec"])
            current = self.agents.get(item["agent_id"])
            profile = self._profiles.get(item["model_profile"])
            source = profile or current
            if source is None or not source.api_key or (source.provider, source.base_url, source.model) != (original["provider"], original["base_url"], original["model"]):
                raise ModelRoutingError(item["agent_id"], "房间原模型已变更或不可用，请恢复原模型配置或新建房间")
            original["api_key"] = source.api_key
            for key in ("capabilities", "modalities", "scenarios", "auto_capabilities", "auto_modalities", "auto_scenarios"):
                original[key] = tuple(original.get(key, ()))
            bindings.append(AgentModelBinding(**{key: item[key] for key in ("agent_id", "display_name", "model", "model_profile", "selection_mode", "selection_reason")}, spec=CloudAgentSpec(**original)))
        return TeamModelSnapshot(tuple(bindings))

    @staticmethod
    def _profiles_from_agents(agents: Mapping[str, CloudAgentSpec]) -> dict[str, CloudModelProfile]:
        """Keep direct, programmatic runtime construction backwards compatible."""
        profiles: dict[str, CloudModelProfile] = {}
        for spec in agents.values():
            if not spec.model:
                continue
            profile_id = spec.model_profile or f"__agent__{spec.agent_id}"
            profiles.setdefault(
                profile_id,
                CloudModelProfile(
                    profile_id=profile_id,
                    display_name=profile_id,
                    provider=spec.provider,
                    base_url=spec.base_url,
                    model=spec.model,
                    api_key_env=spec.api_key_env,
                    api_key=spec.api_key,
                    capabilities=spec.capabilities,
                    modalities=spec.modalities,
                    max_concurrency=spec.max_concurrency,
                    scenarios=spec.scenarios,
                    tier=spec.tier,
                    enabled=spec.enabled,
                ),
            )
        return profiles

    @staticmethod
    def _model_key(spec: CloudAgentSpec) -> tuple[str, str, str]:
        return spec.provider, spec.base_url, spec.model

    @staticmethod
    def _client_key(spec: CloudAgentSpec) -> tuple[str, str, str, str, str]:
        return spec.agent_id, spec.model_profile, spec.provider, spec.base_url, spec.model

    def _invoke_client(self, spec: CloudAgentSpec, messages: Sequence[object]) -> str:
        key = self._client_key(spec)
        with self._configuration_lock:
            client = self._clients.get(key)
            if client is None:
                client = CloudAgentClient(spec)
                self._clients[key] = client
        return client.invoke(messages)  # type: ignore[arg-type]

    def _stream_client(self, spec: CloudAgentSpec, messages: Sequence[object]):
        key = self._client_key(spec)
        with self._configuration_lock:
            client = self._clients.get(key)
            if client is None:
                client = CloudAgentClient(spec)
                self._clients[key] = client
        yield from client.stream(messages)  # type: ignore[arg-type]

    def _semaphore_for(self, spec: CloudAgentSpec) -> BoundedSemaphore:
        key = self._model_key(spec)
        with self._configuration_lock:
            semaphore = self._semaphores.get(key)
            if semaphore is None:
                semaphore = BoundedSemaphore(spec.max_concurrency)
                self._semaphores[key] = semaphore
            return semaphore

    def _agent(self, agents: Mapping[str, CloudAgentSpec], preferred: str, fallback: str | None = None) -> CloudAgentSpec:
        if preferred in agents:
            return agents[preferred]
        if fallback and fallback in agents:
            return agents[fallback]
        return next(iter(agents.values()))

    def _execution_agent_ids(
        self,
        agents: Mapping[str, CloudAgentSpec],
        *,
        architecture: str,
        max_agents: int,
        persona_theme: str | None = None,
        required_capabilities: Sequence[str] = (),
    ) -> tuple[str, ...]:
        chair = agents[THEME_LEADERS[persona_theme]] if persona_theme else self._agent(agents, "chairperson", "assistant")
        if architecture == "direct":
            return (chair.agent_id,)
        members = [spec for spec in agents.values() if spec.agent_id != chair.agent_id]
        required = {str(value).strip().casefold() for value in required_capabilities if str(value).strip()}
        if required:
            members.sort(key=lambda spec: (-len(required.intersection({item.casefold() for item in spec.capabilities})), list(agents).index(spec.agent_id)))
        members = members[:max_agents - 1]
        if persona_theme and architecture == "hierarchical":
            coordinator = THEME_COORDINATORS[persona_theme]
            if coordinator not in agents:
                raise ModelRoutingError(coordinator, f"分层协作需要启用并配置{THEME_ROLES[persona_theme][coordinator]}")
            candidates = [spec for spec in agents.values() if spec.agent_id not in {chair.agent_id, coordinator}]
            if required:
                candidates.sort(key=lambda spec: (-len(required.intersection({item.casefold() for item in spec.capabilities})), list(agents).index(spec.agent_id)))
            members = [agents[coordinator], *candidates][:max_agents - 1]
        if architecture in {"swarm", "graph", "heterogeneous"}:
            return tuple([spec.agent_id for spec in members] + [chair.agent_id])
        researcher = members[0] if members else chair
        reviewer = members[1] if len(members) > 1 else chair
        candidates = (researcher.agent_id, reviewer.agent_id, chair.agent_id)
        return tuple(dict.fromkeys(candidates))

    @staticmethod
    def _is_ready_profile(profile: CloudModelProfile) -> bool:
        return bool(profile.enabled and profile.provider and profile.base_url and profile.model and profile.api_key)

    @staticmethod
    def _requirements_for(
        spec: CloudAgentSpec,
        task_requirements: TaskModelRequirements,
    ) -> dict[str, object]:
        return {
            "tier": spec.auto_tier,
            "capabilities": list(_merged_values(spec.auto_capabilities, task_requirements.capabilities)),
            "modalities": list(_merged_values(spec.auto_modalities, task_requirements.modalities)),
            "scenarios": list(_merged_values(spec.auto_scenarios, task_requirements.scenarios)),
        }

    @staticmethod
    def _candidate_sort_key(profile: CloudModelProfile, required_tier: str) -> tuple[int, int, int, str]:
        rank = tier_rank(profile.tier)
        normalized_rank = rank if rank is not None else -1
        required_rank = tier_rank(required_tier)
        tier_preference = normalized_rank - required_rank if required_rank is not None and normalized_rank >= required_rank else -normalized_rank
        return tier_preference, -profile.max_concurrency, -len(profile.capabilities), profile.profile_id

    @staticmethod
    def _with_profile(
        spec: CloudAgentSpec,
        profile: CloudModelProfile,
        *,
        preserve_agent_overrides: bool = False,
    ) -> CloudAgentSpec:
        return replace(
            spec,
            provider=spec.provider if preserve_agent_overrides and spec.provider else profile.provider,
            base_url=spec.base_url if preserve_agent_overrides and spec.base_url else profile.base_url,
            model=spec.model if preserve_agent_overrides and spec.model else profile.model,
            api_key_env=spec.api_key_env if preserve_agent_overrides and spec.api_key_env else profile.api_key_env,
            api_key=spec.api_key if preserve_agent_overrides and spec.api_key else profile.api_key,
            capabilities=spec.capabilities if preserve_agent_overrides and spec.capabilities else profile.capabilities,
            modalities=spec.modalities if preserve_agent_overrides and spec.modalities else profile.modalities,
            max_concurrency=spec.max_concurrency if preserve_agent_overrides and spec.max_concurrency else profile.max_concurrency,
            scenarios=spec.scenarios if preserve_agent_overrides and spec.scenarios else profile.scenarios,
            model_profile=profile.profile_id,
        )

    def _route_agent(
        self,
        spec: CloudAgentSpec,
        profiles: Mapping[str, CloudModelProfile],
        task_requirements: TaskModelRequirements,
    ) -> AgentModelBinding:
        if spec.model_binding_mode == "fixed":
            if spec.model_profile:
                profile = profiles.get(spec.model_profile)
                if profile is None:
                    raise ModelRoutingError(spec.agent_id, f"固定模型不存在：{spec.model_profile}")
                if not self._is_ready_profile(profile):
                    raise ModelRoutingError(spec.agent_id, f"固定模型尚未就绪：{spec.model_profile}")
                selected = self._with_profile(spec, profile, preserve_agent_overrides=True)
                reason = f"固定绑定：{profile.display_name}（{selected.model}）"
            else:
                if not all((spec.provider, spec.base_url, spec.model, spec.api_key)):
                    raise ModelRoutingError(spec.agent_id, "固定模型尚未完成配置")
                selected = spec
                reason = f"固定绑定：直接配置（{spec.model}）"
            return AgentModelBinding(
                agent_id=spec.agent_id,
                display_name=spec.display_name,
                model=selected.model,
                model_profile=selected.model_profile,
                selection_mode="fixed",
                selection_reason=reason,
                spec=selected,
            )

        requirements = self._requirements_for(spec, task_requirements)
        candidates = [
            profile
            for profile in profiles.values()
            if self._is_ready_profile(profile)
            and profile_matches_requirements(
                profile,
                tier=str(requirements["tier"]),
                capabilities=requirements["capabilities"],  # type: ignore[arg-type]
                modalities=requirements["modalities"],  # type: ignore[arg-type]
                scenarios=requirements["scenarios"],  # type: ignore[arg-type]
            )
        ]
        if not candidates:
            raise ModelRoutingError(
                spec.agent_id,
                f"没有符合自动路由条件的已就绪模型：{spec.display_name}",
                requirements=requirements,
            )
        candidates.sort(key=lambda profile: self._candidate_sort_key(profile, str(requirements["tier"])))
        selected_profile = candidates[0]
        selected = self._with_profile(spec, selected_profile)
        filters = []
        for label, value in (("tier", requirements["tier"]), ("capabilities", requirements["capabilities"]), ("modalities", requirements["modalities"]), ("scenarios", requirements["scenarios"])):
            if value:
                rendered = ",".join(value) if isinstance(value, list) else str(value)
                filters.append(f"{label}={rendered}")
        condition = "；".join(filters) or "无额外约束"
        ranked_candidates = " > ".join(
            f"{index}.{profile.display_name}（{profile.model}，tier={profile.tier}，并发={profile.max_concurrency}）"
            for index, profile in enumerate(candidates[:5], start=1)
        )
        if len(candidates) > 5:
            ranked_candidates += f" > 其余 {len(candidates) - 5} 个候选"
        reason = (
            f"自动路由：{len(candidates)} 个候选，最终合并条件 {condition}；"
            f"候选排序：{ranked_candidates}；"
            f"选择第 1 名 {selected_profile.display_name}（{selected_profile.model}）"
        )
        return AgentModelBinding(
            agent_id=spec.agent_id,
            display_name=spec.display_name,
            model=selected.model,
            model_profile=selected_profile.profile_id,
            selection_mode="auto",
            selection_reason=reason,
            spec=selected,
        )

    def freeze_model_bindings(
        self,
        *,
        architecture: str = "hierarchical",
        max_agents: int = 3,
        goal: str = "",
        required_capabilities: Sequence[str] = (),
        existing_snapshot: TeamModelSnapshot | None = None,
        persona_theme: str | None = None,
    ) -> TeamModelSnapshot:
        """Resolve participating Agents while preserving an existing room snapshot.

        A room can start another run or add a new role later, but an Agent that
        has already joined the room keeps its original model.  New roles are
        resolved once when they first participate.  This prevents automatic
        routing from silently changing a role between follow-up turns.
        """
        with self._configuration_lock:
            run_agents = dict(self.agents)
            profiles = dict(self._profiles)
        previous = existing_snapshot or TeamModelSnapshot(())
        previous_by_id = previous.by_agent_id()
        # Keep a role's original spec even if the current settings page has
        # since changed or disabled it.  Settings apply to new rooms.
        effective_agents = dict(run_agents)
        for agent_id, binding in previous_by_id.items():
            effective_agents[agent_id] = binding.spec
        if persona_theme:
            roles = THEME_ROLES[persona_theme]
            if not self._configured_agent_ids.intersection(roles):
                # Older local configs predate persona roles. Use the same
                # automatic defaults shown on the settings cards, without
                # modifying the user's file or re-enabling disabled roles.
                for key, name in roles.items():
                    effective_agents[key] = CloudAgentSpec(key, name, ROLE_RESPONSIBILITIES.get(key, name),
                        "", "", "", "", "", model_binding_mode="auto")
            effective_agents = {key: replace(spec, display_name=roles[key],
                responsibility=ROLE_RESPONSIBILITIES.get(key, spec.responsibility),
                system_prompt=f"{spec.system_prompt}\n本主题职责（旧设置与此冲突时以此为准）：你是{roles[key]}。用户是{'皇上' if persona_theme == 'emperor' else '董事长'}。{ROLE_RESPONSIBILITIES.get(key, spec.responsibility)}。按本职工作，不伪造未执行的工具或检索。") for key, spec in effective_agents.items() if key in roles}
            leader = THEME_LEADERS[persona_theme]
            if leader not in effective_agents:
                raise ModelRoutingError(leader, f"请先在人设设置中启用并配置{roles[leader]}，再发起任务")
        task_requirements = infer_task_model_requirements(
            goal,
            required_capabilities=required_capabilities,
        )
        self.validate("model binding snapshot", architecture, max_agents, agents=effective_agents)
        agent_ids = self._execution_agent_ids(effective_agents, architecture=architecture, max_agents=max_agents, persona_theme=persona_theme, required_capabilities=task_requirements.capabilities)
        newly_resolved: list[AgentModelBinding] = []
        for agent_id in agent_ids:
            existing = previous_by_id.get(agent_id)
            if existing is not None:
                self._validate_existing_binding(existing, task_requirements)
                continue
            newly_resolved.append(self._route_agent(effective_agents[agent_id], profiles, task_requirements))
        return previous.merge(TeamModelSnapshot(tuple(newly_resolved)))

    @staticmethod
    def _validate_existing_binding(binding: AgentModelBinding, task_requirements: TaskModelRequirements) -> None:
        """Reject a new hard modality requirement instead of switching models."""
        if binding.selection_mode != "auto":
            return
        spec = binding.spec
        profile = CloudModelProfile(
            profile_id=binding.model_profile or f"__room__{binding.agent_id}",
            display_name=binding.display_name,
            provider=spec.provider,
            base_url=spec.base_url,
            model=spec.model,
            api_key_env=spec.api_key_env,
            api_key=spec.api_key,
            capabilities=spec.capabilities,
            modalities=spec.modalities,
            max_concurrency=spec.max_concurrency,
            scenarios=spec.scenarios,
            tier=spec.tier,
            enabled=True,
        )
        if profile_matches_requirements(
            profile,
            capabilities=task_requirements.capabilities,
            modalities=task_requirements.modalities,
            scenarios=task_requirements.scenarios,
        ):
            return
        raise ModelRoutingError(
            binding.agent_id,
            f"房间已固定 {binding.display_name} 的模型（{binding.model}），不满足本次任务新增要求；请新建房间重新路由",
            requirements={
                "model_profile": binding.model_profile,
                "model": binding.model,
                "capabilities": list(task_requirements.capabilities),
                "modalities": list(task_requirements.modalities),
                "scenarios": list(task_requirements.scenarios),
            },
        )

    def model_settings(self) -> dict[str, list[dict[str, object]]]:
        """Return redacted role bindings and selectable model choices."""
        with self._configuration_lock:
            agents = dict(self.agents)
        choices: dict[tuple[str, str, str], dict[str, object]] = {}
        for spec in agents.values():
            if not spec.model:
                continue
            key = self._model_key(spec)
            choices.setdefault(key, {
                "source_agent_id": spec.agent_id,
                "model_profile": spec.model_profile,
                "provider": spec.provider,
                "base_url": spec.base_url,
                "model": spec.model,
                "capabilities": list(spec.capabilities),
                "modalities": list(spec.modalities),
                "max_concurrency": spec.max_concurrency,
            })
        bindings = [{
            "agent_id": spec.agent_id,
            "display_name": spec.display_name,
            "responsibility": spec.responsibility,
            "tier": spec.tier,
            "model_binding_mode": spec.model_binding_mode,
            "model_profile": spec.model_profile,
            "provider": spec.provider,
            "model": spec.model,
            "capabilities": list(spec.capabilities),
            "modalities": list(spec.modalities),
            "max_concurrency": spec.max_concurrency,
            "auto_tier": spec.auto_tier,
            "auto_capabilities": list(spec.auto_capabilities),
            "auto_modalities": list(spec.auto_modalities),
            "auto_scenarios": list(spec.auto_scenarios),
        } for spec in agents.values()]
        return {"agents": bindings, "models": list(choices.values())}

    def update_model_binding(self, agent_id: str, *, source_agent_id: str, tier: str | None = None) -> dict[str, object]:
        """Legacy in-memory rebinding; active snapshots remain unaffected."""
        with self._configuration_lock:
            current = self.agents.get(agent_id)
            source = self.agents.get(source_agent_id)
            if current is None or source is None:
                raise KeyError("unknown agent binding")
            updated = replace(
                current,
                provider=source.provider,
                base_url=source.base_url,
                model=source.model,
                api_key_env=source.api_key_env,
                api_key=source.api_key,
                capabilities=source.capabilities,
                model_profile=source.model_profile,
                modalities=source.modalities,
                max_concurrency=source.max_concurrency,
                scenarios=source.scenarios,
                tier=(tier.strip() if isinstance(tier, str) and tier.strip() else current.tier),
                model_binding_mode="fixed",
                auto_tier="",
                auto_capabilities=(),
                auto_modalities=(),
                auto_scenarios=(),
            )
            self.agents[agent_id] = updated
        settings = self.model_settings()["agents"]
        return next(item for item in settings if item["agent_id"] == agent_id)

    def _turn(self, binding: AgentModelBinding, prompt: str, sequence: int, on_activity=None) -> AgentTurn:
        from time import monotonic
        spec = binding.spec
        stream_id = f"stream-{uuid4().hex}"
        details = {**binding.public(), "sequence": sequence, "responsibility": spec.responsibility, "stream_id": stream_id}
        emit = on_activity or (lambda event_type, payload: None)
        emit("step_queued", {**details, "input": prompt})
        messages = []
        if spec.system_prompt:
            messages.append(SystemMessage(content=spec.system_prompt))
        messages.append(HumanMessage(content=prompt))
        started = monotonic()
        try:
            with self._semaphore_for(spec):
                started = monotonic()
                emit("step_started", details)
                key = self._model_key(spec)
                probe = self._circuit.acquire(key)
                try:
                    if self._invoker == self._invoke_client:
                        chunks: list[str] = []
                        offset = 0
                        for token_index, delta in enumerate(self._stream_client(spec, messages)):
                            chunks.append(delta)
                            offset += len(delta)
                            emit("step_output_delta", {**details, "delta": delta, "token_index": token_index, "offset": offset})
                        content = "".join(chunks)
                    else:
                        content = self._invoker(spec, messages)
                except Exception as exc:
                    if transient_error(exc) or probe:
                        self._circuit.failure(key, probe)
                    raise
                else:
                    self._circuit.success(key, probe)
            if not isinstance(content, str) or not content.strip():
                raise RuntimeError(f"Cloud agent returned an empty response: {spec.agent_id}")
        except Exception as exc:
            emit("step_failed", {**details, **serialize_exception(exc, phase="model_call", agent_id=spec.agent_id, agent_name=spec.display_name, provider=spec.provider, model=spec.model), "duration_ms": int((monotonic() - started) * 1000)})
            raise
        return AgentTurn(
            agent_id=spec.agent_id,
            display_name=spec.display_name,
            responsibility=spec.responsibility,
            prompt=prompt,
            content=content,
            sequence=sequence,
            model=spec.model,
            model_profile=binding.model_profile,
            selection_mode=binding.selection_mode,
            selection_reason=binding.selection_reason,
            duration_ms=int((monotonic() - started) * 1000),
        )

    def _parallel_turns(self, requests: Sequence[tuple[AgentModelBinding, str, int]], *, on_activity=None, on_turn=None) -> list[AgentTurn]:
        """Run independent roles concurrently with isolated message lists."""
        if not requests:
            return []
        results: dict[int, AgentTurn] = {}
        failure = None
        with ThreadPoolExecutor(max_workers=len(requests), thread_name_prefix="localrag-agent") as pool:
            futures = {pool.submit(self._turn, binding, prompt, sequence, on_activity): sequence for binding, prompt, sequence in requests}
            for future in as_completed(futures):
                try:
                    turn = future.result()
                    results[turn.sequence] = turn
                    if on_turn:
                        on_turn(turn)
                except Exception as exc:
                    failure = failure or exc
        if failure:
            raise failure
        return [results[sequence] for _, _, sequence in sorted(requests, key=lambda item: item[2])]

    def validate(
        self,
        goal: str,
        architecture: str,
        max_agents: int,
        *,
        agents: Mapping[str, CloudAgentSpec] | None = None,
    ) -> None:
        configured_agents = self.agents if agents is None else agents
        if not isinstance(goal, str) or not goal.strip():
            raise ValueError("goal must not be empty")
        if architecture not in ARCHITECTURES:
            raise ValueError(f"unsupported architecture: {architecture}")
        if type(max_agents) is not int or max_agents < 1:
            raise ValueError("max_agents must be positive")
        if architecture != "direct" and (max_agents < 2 or len(configured_agents) < 2):
            raise ValueError("collaboration requires at least two enabled agents")
        if architecture == "adversarial" and (max_agents < 3 or len(configured_agents) < 3):
            raise ValueError("adversarial requires three independent agents")
        if architecture in {"graph", "heterogeneous"} and (max_agents < 3 or len(configured_agents) < 3):
            raise ValueError(f"{architecture} requires three enabled agents")

    def execute(
        self,
        goal: str,
        *,
        architecture: str = "hierarchical",
        max_agents: int = 3,
        context: str = "",
        required_capabilities: Sequence[str] = (),
        on_turn: Callable[[AgentTurn], None] | None = None,
        on_activity: Callable[[str, dict], None] | None = None,
        model_snapshot: TeamModelSnapshot | None = None,
        persona_theme: str | None = None,
        check_active: Callable[[], None] = lambda: None,
        completed_turns: Mapping[int, AgentTurn] | None = None,
    ) -> TeamRunResult:
        snapshot = model_snapshot or self.freeze_model_bindings(
            architecture=architecture,
            max_agents=max_agents,
            goal=goal,
            required_capabilities=required_capabilities,
            persona_theme=persona_theme,
        )
        run_bindings = snapshot.by_agent_id()
        # A room snapshot may contain more members than this run requested.
        # Select the current strategy's participants while sourcing every
        # selected model from the immutable room bindings.
        task_requirements = infer_task_model_requirements(goal, required_capabilities=required_capabilities)
        snapshot_agent_ids = self._execution_agent_ids(
            {agent_id: binding.spec for agent_id, binding in run_bindings.items()},
            architecture=architecture,
            max_agents=max_agents,
            persona_theme=persona_theme,
            required_capabilities=task_requirements.capabilities,
        )
        run_bindings = {agent_id: run_bindings[agent_id] for agent_id in snapshot_agent_ids}
        run_agents = {agent_id: binding.spec for agent_id, binding in run_bindings.items()}
        self.validate(goal, architecture, max_agents, agents=run_agents)
        normalized_goal = goal.strip()
        turns: list[AgentTurn] = []
        chair = run_agents[THEME_LEADERS[persona_theme]] if persona_theme else self._agent(run_agents, "chairperson", "assistant")
        chair_binding = run_bindings[chair.agent_id]
        members = [spec for spec in run_agents.values() if spec.agent_id != chair.agent_id]
        required = {value.casefold() for value in task_requirements.capabilities}
        if required:
            members.sort(key=lambda spec: -len(required.intersection({item.casefold() for item in spec.capabilities})))
        members = members[:max_agents - 1]
        researcher = members[0] if members else chair
        researcher_binding = run_bindings[researcher.agent_id]
        reviewer = members[1] if len(members) > 1 else None
        reviewer_binding = run_bindings[reviewer.agent_id] if reviewer is not None else None

        emit = on_activity or (lambda event_type, payload: None)
        emit("team_planned", {"architecture": architecture, "participants": [binding.public() for binding in run_bindings.values()],
            "selection": {"required_capabilities": list(task_requirements.capabilities), "reason": "按任务能力匹配角色；无匹配时按主题职责顺序兜底"}})

        steps = build_team_plan(architecture, run_bindings, chair_binding, members, normalized_goal, persona_theme, context)
        emit("team_plan_created", {"architecture": architecture, "steps": [
            {"sequence": s.sequence, "agent_id": s.agent_id, "title": s.title, "dependencies": list(s.dependencies), "is_final": s.final_output}
            for s in steps
        ]})
        scheduler = TeamStepScheduler(
            emit=emit,
            invoke=lambda agent_id, prompt, sequence: self._turn(run_bindings[agent_id], prompt, sequence, on_activity),
            on_turn=on_turn,
            check_active=check_active,
        )
        turns = scheduler.execute(steps, completed_turns=completed_turns)
        return TeamRunResult(architecture, "completed", tuple(turns), turns[-1].content)
