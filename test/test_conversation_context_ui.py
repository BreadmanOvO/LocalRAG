from __future__ import annotations

import ast
import unittest
from pathlib import Path
from types import TracebackType
from types import SimpleNamespace
from typing import Callable, Literal, cast, get_type_hints
from unittest import mock

from agent.context.models import ConversationSummary, SummaryFinding
from agent.context.store import ConversationSummarySnapshot
from agent.research.presentation import (
    ConversationContextFindingView,
    ConversationContextSummaryView,
    ConversationContextView,
    build_conversation_context_view,
)


ROOT = Path(__file__).resolve().parents[1]


def _snapshot(
    *,
    tokens_before: int = 1000,
    tokens_after: int = 400,
    messages_before: int = 12,
    messages_after: int = 5,
) -> ConversationSummarySnapshot:
    return ConversationSummarySnapshot(
        session_id="session-ui",
        revision=3,
        summary=ConversationSummary(
            goal="完成 v1.6 发布",
            user_constraints=("保留证据引用",),
            confirmed_findings=(
                SummaryFinding(
                    claim="会话压缩已接入",
                    evidence_ids=("e-1", "e-2"),
                ),
            ),
            decisions=("使用结构化摘要",),
            unresolved_questions=("是否启用本地模型",),
            failed_attempts=("首次主模型调用失败",),
            referenced_source_ids=("source-1",),
        ),
        covered_message_ids=("id:m1", "id:m2"),
        tokens_before=tokens_before,
        tokens_after=tokens_after,
        messages_before=messages_before,
        messages_after=messages_after,
        summary_model="Qwen3-4B-LoRA",
        compression_reason="trigger_threshold",
        fallback_reason="primary_timeout",
        created_at="2026-07-28T00:00:00+00:00",
        updated_at="2026-07-28T00:01:00+00:00",
    )


class ConversationContextViewTests(unittest.TestCase):
    def test_typed_dict_contract_is_exact(self) -> None:
        self.assertIs(
            get_type_hints(build_conversation_context_view)["return"],
            ConversationContextView,
        )
        self.assertEqual(
            get_type_hints(ConversationContextFindingView),
            {
                "claim": str,
                "evidence_ids": tuple[str, ...],
            },
        )
        self.assertEqual(
            set(get_type_hints(ConversationContextSummaryView)),
            {
                "goal",
                "user_constraints",
                "confirmed_findings",
                "decisions",
                "unresolved_questions",
                "failed_attempts",
                "referenced_source_ids",
            },
        )
        self.assertEqual(
            set(get_type_hints(ConversationContextView)),
            {
                "available",
                "status",
                "revision",
                "compression_count",
                "tokens_before",
                "tokens_after",
                "token_reduction",
                "token_reduction_ratio",
                "messages_before",
                "messages_after",
                "retained_messages",
                "summary_model",
                "fallback_reason",
                "summary",
            },
        )

    def test_empty_view_has_exact_stable_contract(self) -> None:
        self.assertEqual(
            build_conversation_context_view(None, 0),
            {
                "available": False,
                "status": "",
                "revision": 0,
                "compression_count": 0,
                "tokens_before": 0,
                "tokens_after": 0,
                "token_reduction": 0,
                "token_reduction_ratio": 0.0,
                "messages_before": 0,
                "messages_after": 0,
                "retained_messages": 0,
                "summary_model": "",
                "fallback_reason": "",
                "summary": {
                    "goal": "",
                    "user_constraints": (),
                    "confirmed_findings": (),
                    "decisions": (),
                    "unresolved_questions": (),
                    "failed_attempts": (),
                    "referenced_source_ids": (),
                },
            },
        )

    def test_snapshot_view_expands_every_summary_field_and_uses_event_count(self) -> None:
        view = build_conversation_context_view(_snapshot(), 7)

        self.assertEqual(
            view,
            {
                "available": True,
                "status": "已压缩",
                "revision": 3,
                "compression_count": 7,
                "tokens_before": 1000,
                "tokens_after": 400,
                "token_reduction": 600,
                "token_reduction_ratio": 0.6,
                "messages_before": 12,
                "messages_after": 5,
                "retained_messages": 5,
                "summary_model": "Qwen3-4B-LoRA",
                "fallback_reason": "primary_timeout",
                "summary": {
                    "goal": "完成 v1.6 发布",
                    "user_constraints": ("保留证据引用",),
                    "confirmed_findings": (
                        {
                            "claim": "会话压缩已接入",
                            "evidence_ids": ("e-1", "e-2"),
                        },
                    ),
                    "decisions": ("使用结构化摘要",),
                    "unresolved_questions": ("是否启用本地模型",),
                    "failed_attempts": ("首次主模型调用失败",),
                    "referenced_source_ids": ("source-1",),
                },
            },
        )
        self.assertNotIn("ConversationSummary", repr(view))

    def test_token_reduction_is_clamped_for_anomalous_and_zero_observations(self) -> None:
        anomalous = build_conversation_context_view(
            _snapshot(tokens_before=10, tokens_after=20),
            1,
        )
        zero = build_conversation_context_view(
            _snapshot(tokens_before=0, tokens_after=0),
            1,
        )

        self.assertEqual(anomalous["token_reduction"], 0)
        self.assertEqual(anomalous["token_reduction_ratio"], 0.0)
        self.assertEqual(zero["token_reduction"], 0)
        self.assertEqual(zero["token_reduction_ratio"], 0.0)

    def test_inputs_are_strict(self) -> None:
        builder = mock.Mock(wraps=build_conversation_context_view)
        invalid_snapshots: tuple[object, ...] = ({}, SimpleNamespace())
        for invalid_snapshot in invalid_snapshots:
            with self.subTest(snapshot=invalid_snapshot):
                with self.assertRaises(TypeError):
                    builder(invalid_snapshot, 0)

        invalid_counts: tuple[tuple[object, type[Exception]], ...] = (
            (True, TypeError),
            (1.5, TypeError),
            (-1, ValueError),
        )
        for invalid_count, error in invalid_counts:
            with self.subTest(event_count=invalid_count):
                with self.assertRaises(error):
                    builder(None, invalid_count)


class _FakeContainer:
    def __init__(self, streamlit: _FakeStreamlit | None = None) -> None:
        self._streamlit = streamlit

    def __enter__(self) -> _FakeContainer:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> Literal[False]:
        return False

    def metric(self, label: str, value: object) -> None:
        assert self._streamlit is not None
        self._streamlit.metrics.append((label, value))


class _FakeStreamlit:
    def __init__(self) -> None:
        self.expanders: list[tuple[str, bool]] = []
        self.captions: list[str] = []
        self.errors: list[str] = []
        self.metrics: list[tuple[str, object]] = []
        self.json_payloads: list[dict[str, object]] = []
        self.button_calls = 0

    def expander(self, label: str, *, expanded: bool) -> _FakeContainer:
        self.expanders.append((label, expanded))
        return _FakeContainer(self)

    def columns(self, count: int) -> tuple[_FakeContainer, ...]:
        return tuple(_FakeContainer(self) for _ in range(count))

    def caption(self, text: str) -> None:
        self.captions.append(text)

    def error(self, text: str) -> None:
        self.errors.append(text)

    def json(self, payload: dict[str, object]) -> None:
        self.json_payloads.append(payload)

    def button(self, *args, **kwargs):
        self.button_calls += 1
        return False


def _load_render_function(
    fake_st: _FakeStreamlit,
) -> Callable[[object], None]:
    source = (ROOT / "app_qa.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    function = next(
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef)
        and node.name == "_render_conversation_context"
    )
    module = ast.Module(body=[function], type_ignores=[])
    ast.fix_missing_locations(module)
    namespace = {
        "st": fake_st,
        "build_conversation_context_view": build_conversation_context_view,
        "logger": mock.Mock(),
    }
    exec(compile(module, str(ROOT / "app_qa.py"), "exec"), namespace)
    return cast(
        "Callable[[object], None]",
        namespace["_render_conversation_context"],
    )


class ConversationContextRenderTests(unittest.TestCase):
    def test_empty_snapshot_renders_read_only_empty_state(self) -> None:
        fake_st = _FakeStreamlit()
        render = _load_render_function(fake_st)
        agent = mock.Mock()
        agent.get_conversation_context.return_value = None
        agent.context_middleware = None

        render(agent)

        self.assertEqual(fake_st.expanders, [("会话压缩状态", False)])
        self.assertIn("尚未触发会话压缩", fake_st.captions)
        self.assertEqual(fake_st.metrics, [])
        self.assertEqual(fake_st.json_payloads, [])
        self.assertEqual(fake_st.button_calls, 0)

    def test_snapshot_renders_four_metrics_event_count_and_json_copy(self) -> None:
        fake_st = _FakeStreamlit()
        render = _load_render_function(fake_st)
        snapshot = _snapshot()
        store = mock.Mock()
        store.list_events.return_value = (object(), object(), object(), object())
        agent = mock.Mock()
        agent.session_id = "session-ui"
        agent.get_conversation_context.return_value = snapshot
        agent.context_middleware.store = store

        render(agent)

        self.assertEqual(fake_st.expanders, [("会话压缩状态", True)])
        self.assertEqual(
            fake_st.metrics,
            [
                ("Revision", 3),
                ("压缩次数", 4),
                ("Token 降幅", "600 (60.0%)"),
                ("保留消息", 5),
            ],
        )
        store.list_events.assert_called_once_with("session-ui")
        self.assertEqual(len(fake_st.json_payloads), 1)
        payload = fake_st.json_payloads[0]
        user_constraints = payload["user_constraints"]
        confirmed_findings = payload["confirmed_findings"]
        self.assertIsInstance(user_constraints, list)
        self.assertIsInstance(confirmed_findings, list)
        assert isinstance(confirmed_findings, list)
        first_finding = confirmed_findings[0]
        self.assertIsInstance(first_finding, dict)
        assert isinstance(first_finding, dict)
        self.assertIsInstance(first_finding["evidence_ids"], list)
        self.assertNotIn("ConversationSummary", repr(payload))
        self.assertEqual(fake_st.button_calls, 0)

    def test_event_read_failure_is_visible_and_does_not_crash(self) -> None:
        fake_st = _FakeStreamlit()
        render = _load_render_function(fake_st)
        agent = mock.Mock()
        agent.session_id = "session-ui"
        agent.get_conversation_context.return_value = _snapshot()
        agent.context_middleware.store.list_events.side_effect = RuntimeError("db down")

        render(agent)

        self.assertEqual(len(fake_st.errors), 1)
        self.assertEqual(
            fake_st.errors[0],
            "压缩次数读取失败，已使用 revision",
        )
        self.assertEqual(dict(fake_st.metrics)["压缩次数"], 3)

    def test_snapshot_read_failure_is_unavailable_with_zero_metrics(self) -> None:
        fake_st = _FakeStreamlit()
        render = _load_render_function(fake_st)
        agent = mock.Mock()
        agent.get_conversation_context.side_effect = RuntimeError("db down")

        render(agent)

        self.assertEqual(fake_st.expanders, [("会话压缩状态", False)])
        self.assertEqual(fake_st.errors, ["会话压缩状态读取失败"])
        self.assertEqual(fake_st.metrics, [])
        self.assertIn("尚未触发会话压缩", fake_st.captions)

    def test_render_is_immediately_after_research_plan_before_chat_divider(self) -> None:
        source = (ROOT / "app_qa.py").read_text(encoding="utf-8")
        research_call = source.index("research_action = _render_research_plan(")
        context_call = source.index("_render_conversation_context(agent)", research_call)
        divider = source.index("st.divider()", context_call)
        chat_loop = source.index(
            'for message in st.session_state["message"]:',
            divider,
        )

        self.assertLess(research_call, context_call)
        self.assertIn(
            "    research_identity_error,\n)\n_render_conversation_context(agent)",
            source[research_call:context_call + len("_render_conversation_context(agent)")],
        )
        self.assertLess(context_call, divider)
        self.assertLess(divider, chat_loop)


if __name__ == "__main__":
    unittest.main()
