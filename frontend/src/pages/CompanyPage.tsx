import { FormEvent, useEffect, useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  BadgeCheck,
  Bot,
  Check,
  CircleAlert,
  Cpu,
  Copy,
  Eye,
  KeyRound,
  LoaderCircle,
  Paintbrush,
  RefreshCw,
  Route,
  Save,
  SlidersHorizontal,
  Trash2,
  UsersRound,
} from "lucide-react";
import type { components } from "../shared/api/schema";
import { themes, useTheme, type ThemeId, type ThemeRole } from "../app/theme";
import { api, type AgentBindingMode, type CompatibleAgentConfig } from "../shared/api/client";

type Profile = components["schemas"]["ModelProfileResponse"];
type Agent = components["schemas"]["AgentConfigResponse"] & Partial<AgentRoutingFields>;
type DiscoveredModel = components["schemas"]["DiscoveredModelResponse"];
type ProfileForm = components["schemas"]["ModelProfileRequest"];

type AgentRoutingFields = {
  model_binding_mode: AgentBindingMode;
  auto_tier: string;
  auto_modalities: string[];
  auto_scenarios: string[];
  auto_capabilities: string[];
};

type AgentForm = CompatibleAgentConfig & AgentRoutingFields;
type BindingSelection = AgentRoutingFields & { model_profile: string };
type BindingAgent = Agent & { presetRole: ThemeRole | null; persisted: boolean };

type Option = { value: string; label: string };

const tierOptions: Option[] = [
  { value: "economy", label: "基础" },
  { value: "standard", label: "标准" },
  { value: "advanced", label: "高级" },
  { value: "expert", label: "专家" },
];
const modalityOptions: Option[] = [
  { value: "text", label: "文本" },
  { value: "image", label: "图像" },
  { value: "audio", label: "音频" },
  { value: "video", label: "视频" },
  { value: "document", label: "文档" },
  { value: "table", label: "表格" },
];
const scenarioOptions: Option[] = [
  { value: "research", label: "研究检索" },
  { value: "analysis", label: "分析推演" },
  { value: "engineering", label: "工程实现" },
  { value: "review", label: "审查核验" },
  { value: "writing", label: "报告撰写" },
  { value: "vision", label: "图片理解" },
];
const capabilityOptions: Option[] = [
  { value: "reasoning", label: "复杂推理" },
  { value: "coding", label: "代码" },
  { value: "rag", label: "知识检索" },
  { value: "review", label: "审查核验" },
  { value: "writing", label: "内容撰写" },
  { value: "ocr", label: "OCR" },
  { value: "visual_grounding", label: "视觉定位" },
  { value: "tool_use", label: "工具调用" },
  { value: "summarization", label: "长文归纳" },
];

const presetCapabilities: Record<string, string[]> = {
  chairperson: ["reasoning", "review"],
  executive_assistant: ["reasoning", "tool_use", "summarization"],
  strategy_lead: ["reasoning", "rag", "review"],
  technology_lead: ["reasoning", "coding", "review"],
  project_manager: ["reasoning", "tool_use", "summarization"],
  architect: ["reasoning", "coding", "review"],
  engineer: ["coding", "tool_use", "reasoning"],
  researcher: ["rag", "reasoning", "summarization"],
  data_analyst: ["reasoning", "tool_use", "summarization"],
  reviewer: ["review", "reasoning", "rag"],
  report_writer: ["summarization", "writing", "rag"],
  emperor: ["reasoning", "review"],
  grand_secretary: ["reasoning", "summarization", "tool_use"],
  chief_eunuch: ["tool_use", "summarization", "reasoning"],
  minister_personnel: ["reasoning", "review", "tool_use"],
  minister_revenue: ["reasoning", "tool_use", "summarization"],
  minister_rites: ["writing", "summarization", "review"],
  minister_war: ["reasoning", "tool_use", "review"],
  minister_justice: ["review", "reasoning", "rag"],
  minister_works: ["coding", "reasoning", "tool_use"],
  censor: ["review", "rag", "reasoning"],
  academician: ["rag", "writing", "summarization"],
};

const emptyProfile: ProfileForm = {
  profile_id: "",
  display_name: "",
  provider: "",
  base_url: "",
  model: "",
  api_key_env: "",
  api_key: "",
  capabilities: [],
  modalities: ["text"],
  scenarios: [],
  tier: "standard",
  max_concurrency: 4,
  enabled: false,
  clear_api_key: false,
};
const emptyAgents: Agent[] = [];

type SettingsTab = "personas" | "models" | "appearance";

function agentForm(agent: Agent): AgentForm {
  const mode = agent.model_binding_mode ?? (agent.model_profile ? "fixed" : "auto");
  return {
    agent_id: agent.agent_id,
    display_name: agent.display_name,
    responsibility: agent.responsibility,
    model_profile: agent.model_profile,
    tier: agent.tier || "standard",
    capabilities: agent.capabilities ?? [],
    modalities: agent.modalities ?? ["text"],
    system_prompt: agent.system_prompt,
    enabled: agent.enabled,
    model_binding_mode: mode,
    auto_tier: agent.auto_tier || agent.tier || "standard",
    auto_modalities: agent.auto_modalities ?? agent.modalities ?? ["text"],
    auto_scenarios: agent.auto_scenarios ?? [],
    auto_capabilities: agent.auto_capabilities ?? agent.capabilities ?? [],
  };
}

function presetAgent(role: ThemeRole): Agent {
  const capabilities = presetCapabilities[role.id] ?? ["reasoning"];
  return {
    agent_id: role.id,
    display_name: role.title,
    responsibility: role.responsibility,
    model_profile: "",
    tier: "standard",
    capabilities,
    modalities: ["text"],
    system_prompt: `你是${role.department}的${role.title}。${role.responsibility}。交付时说明依据、结论和待确认事项。`,
    enabled: true,
    ready: false,
    readiness_issues: ["尚未配置模型"],
    model_binding_mode: "auto",
    auto_tier: "standard",
    auto_modalities: ["text"],
    auto_scenarios: [],
    auto_capabilities: capabilities,
  };
}

function toggleValue(values: string[], value: string) {
  return values.includes(value) ? values.filter((item) => item !== value) : [...values, value];
}

function PresetPicker({ label, options, value, onChange }: { label: string; options: Option[]; value: string[]; onChange: (next: string[]) => void }) {
  return <fieldset className="preset-picker">
    <legend>{label}</legend>
    <div className="preset-options">
      {options.map((option) => <label className={value.includes(option.value) ? "preset-option selected" : "preset-option"} key={option.value}>
        <input type="checkbox" checked={value.includes(option.value)} onChange={() => onChange(toggleValue(value, option.value))} />
        <span>{option.label}</span>
      </label>)}
    </div>
  </fieldset>;
}

function SettingTabs({ active, onChange }: { active: SettingsTab; onChange: (tab: SettingsTab) => void }) {
  const tabs: Array<{ id: SettingsTab; label: string; icon: typeof UsersRound }> = [
    { id: "personas", label: "人设设置", icon: UsersRound },
    { id: "models", label: "模型设置", icon: Cpu },
    { id: "appearance", label: "页面设置", icon: Paintbrush },
  ];
  return <div className="settings-tabs" role="tablist" aria-label="设置分类">
    {tabs.map((tab) => {
      const Icon = tab.icon;
      return <button type="button" role="tab" aria-selected={active === tab.id} className={active === tab.id ? "settings-tab active" : "settings-tab"} key={tab.id} onClick={() => onChange(tab.id)}>
        <Icon aria-hidden="true" size={16} />{tab.label}
      </button>;
    })}
  </div>;
}

function ThemeSwitch({ selected, onSelect }: { selected: ThemeId; onSelect: (theme: ThemeId) => void }) {
  const themeCards: Array<{ id: ThemeId; title: string; description: string }> = [
    { id: "company", title: "公司", description: "董事长办公室和正式部门的协作表达" },
    { id: "emperor", title: "当皇上", description: "御前、内阁和六部的古代称谓表达" },
  ];
  return <div className="theme-settings-grid">
    {themeCards.map((card) => <button key={card.id} type="button" onClick={() => onSelect(card.id)} className={selected === card.id ? `theme-setting-card ${card.id} active` : `theme-setting-card ${card.id}`} aria-pressed={selected === card.id}>
      <span className="theme-setting-title">{card.title}{selected === card.id && <Check aria-label="当前主题" size={17} />}</span>
      <span>{card.description}</span>
    </button>)}
  </div>;
}

export function CompanyPage() {
  const queryClient = useQueryClient();
  const { theme, definition, setTheme } = useTheme();
  const [activeTab, setActiveTab] = useState<SettingsTab>("personas");
  const catalog = useQuery({ queryKey: ["model-catalog"], queryFn: api.modelCatalog });
  const profiles = catalog.data?.profiles ?? [];
  const agents = (catalog.data?.agents ?? emptyAgents) as Agent[];
  const [profile, setProfile] = useState<ProfileForm>(emptyProfile);
  const [profileEditorOpen, setProfileEditorOpen] = useState(false);
  const [editingProfileId, setEditingProfileId] = useState<string | null>(null);
  const [discovered, setDiscovered] = useState<DiscoveredModel[]>([]);
  const [agentDrafts, setAgentDrafts] = useState<Record<string, AgentForm>>({});
  const [selectedAgents, setSelectedAgents] = useState<string[]>([]);
  const [bulkBinding, setBulkBinding] = useState<BindingSelection>({ model_binding_mode: "auto", model_profile: "", auto_tier: "standard", auto_modalities: ["text"], auto_scenarios: [], auto_capabilities: [] });
  const [customPersonaOpen, setCustomPersonaOpen] = useState(false);
  const [customPersona, setCustomPersona] = useState({ persona_id: "", role_id: "custom", display_name: "", system_prompt: "", tone: "" });
  const savePersona = useMutation({ mutationFn: () => api.savePersona(customPersona), onSuccess: () => { setCustomPersonaOpen(false); setCustomPersona({ persona_id: "", role_id: "custom", display_name: "", system_prompt: "", tone: "" }); } });
  const discover = useMutation({
    mutationFn: () => api.discoverModels(profile.base_url, profile.api_key, profile.profile_id),
    onSuccess: (data) => setDiscovered(data.items),
  });
  const clearDiscoveryState = () => {
    discover.reset();
    setDiscovered([]);
  };

  const bindingAgents = useMemo<BindingAgent[]>(() => {
    const configured = new Map(agents.map((agent) => [agent.agent_id, agent]));
    const presetRoles = definition?.roles ?? [];
    const presetIds = new Set(presetRoles.map((role) => role.id));
    const themed = presetRoles.map((role) => {
      const persisted = configured.get(role.id);
      return { ...(persisted ?? presetAgent(role)), presetRole: role, persisted: Boolean(persisted) };
    });
    const supplemental = agents
      .filter((agent) => !presetIds.has(agent.agent_id)
        && !Object.values(themes).some((item) => item.roles.some((role) => role.id === agent.agent_id))
        && !["chairperson", "emperor", "assistant", "researcher", "reviewer"].includes(agent.agent_id))
      .map((agent) => ({ ...agent, presetRole: null, persisted: true }));
    return [...themed, ...supplemental];
  }, [agents, definition]);

  useEffect(() => {
    if (!bindingAgents.length) return;
    setAgentDrafts((current) => {
      const next = { ...current };
      let changed = false;
      bindingAgents.forEach((agent) => {
        if (!next[agent.agent_id]) {
          next[agent.agent_id] = agentForm(agent);
          changed = true;
        }
      });
      return changed ? next : current;
    });
  }, [bindingAgents]);

  const refresh = (data: unknown) => queryClient.setQueryData(["model-catalog"], data);
  const saveProfile = useMutation({
    mutationFn: () => api.saveModelProfile(profile.profile_id, profile),
    onSuccess: (data) => { refresh(data); setProfileEditorOpen(false); setEditingProfileId(null); setProfile(emptyProfile); clearDiscoveryState(); },
  });
  const deleteProfile = useMutation({
    mutationFn: (profileId: string) => api.deleteModelProfile(profileId),
    onSuccess: refresh,
  });
  const verifyProfile = useMutation({ mutationFn: api.verifyModelProfile });
  const cloneProfile = useMutation({
    mutationFn: api.cloneModelProfile,
    onMutate: clearDiscoveryState,
    onSuccess: (data) => {
      if (!data) return;
      refresh(data.catalog);
      const cloned = data.catalog.profiles.find((item) => item.profile_id === data.profile_id);
      if (!cloned) return;
      clearDiscoveryState();
      setEditingProfileId(data.profile_id);
      setProfileEditorOpen(true);
      setProfile({ ...emptyProfile, ...cloned, api_key: "", clear_api_key: false });
      window.scrollTo({ top: 0, behavior: "smooth" });
    },
  });
  const saveAgent = useMutation({
    mutationFn: ({ agentId, body }: { agentId: string; body: AgentForm }) => api.saveAgentConfig(agentId, body),
    onSuccess: refresh,
  });
  const applyBulkBinding = useMutation({
    mutationFn: async (agentIds: string[]) => {
      const results = await Promise.all(agentIds.map((agentId) => {
        const draft = agentDrafts[agentId];
        if (!draft) throw new Error("找不到待更新的 Agent 配置");
        const next: AgentForm = {
          ...draft,
          model_binding_mode: bulkBinding.model_binding_mode,
          model_profile: bulkBinding.model_binding_mode === "fixed" ? bulkBinding.model_profile : "",
          auto_tier: bulkBinding.auto_tier,
          auto_modalities: bulkBinding.auto_modalities,
          auto_scenarios: bulkBinding.auto_scenarios,
          auto_capabilities: bulkBinding.auto_capabilities,
        };
        return api.saveAgentConfig(agentId, next);
      }));
      return results[results.length - 1];
    },
    onSuccess: (data) => {
      if (data) refresh(data);
      setAgentDrafts((current) => {
        const next = { ...current };
        selectedAgents.forEach((agentId) => {
          const draft = next[agentId];
          if (!draft) return;
          next[agentId] = {
            ...draft,
            model_binding_mode: bulkBinding.model_binding_mode,
            model_profile: bulkBinding.model_binding_mode === "fixed" ? bulkBinding.model_profile : "",
            auto_tier: bulkBinding.auto_tier,
            auto_modalities: bulkBinding.auto_modalities,
            auto_scenarios: bulkBinding.auto_scenarios,
            auto_capabilities: bulkBinding.auto_capabilities,
          };
        });
        return next;
      });
      setSelectedAgents([]);
    },
  });
  const readyProfileCount = useMemo(() => profiles.filter((item) => item.ready).length, [profiles]);
  const saveCurrentProfile = (event: FormEvent) => {
    event.preventDefault();
    if (profile.profile_id.trim()) saveProfile.mutate();
  };
  const editProfile = (item: Profile) => {
    clearDiscoveryState();
    setEditingProfileId(item.profile_id);
    setProfileEditorOpen(true);
    setProfile({ ...emptyProfile, ...item, api_key: "", clear_api_key: false });
  };
  const resetProfile = () => {
    clearDiscoveryState();
    setEditingProfileId(null);
    setProfileEditorOpen(true);
    setProfile(emptyProfile);
  };
  const updateProfile = (next: ProfileForm, clearDiscovery = false) => {
    setProfile(next);
    if (clearDiscovery) clearDiscoveryState();
  };
  const updateDraft = (agentId: string, updater: (draft: AgentForm) => AgentForm) => {
    setAgentDrafts((current) => ({ ...current, [agentId]: updater(current[agentId] ?? agentForm(bindingAgents.find((item) => item.agent_id === agentId)!)) }));
  };
  const toggleSelected = (agentId: string) => setSelectedAgents((current) => current.includes(agentId) ? current.filter((item) => item !== agentId) : [...current, agentId]);
  const canApplyBulk = selectedAgents.length > 0 && (bulkBinding.model_binding_mode === "auto" || Boolean(bulkBinding.model_profile));

  return <section className="page settings-page">
    <header className="product-page-header settings-page-header">
      <span className="section-icon"><SlidersHorizontal aria-hidden="true" size={18} /></span>
      <div>
        <p className="eyebrow">{definition?.setupLabel ?? "公司设置"}</p>
        <h1>{definition?.setupLabel ?? "公司设置"}</h1>
        <p className="subtitle">管理团队人设、模型能力和页面主题。</p>
      </div>
    </header>
    <SettingTabs active={activeTab} onChange={setActiveTab} />

    {activeTab === "personas" && <div className="settings-content">
      <section className="settings-section">
        <div className="section-heading"><div><p className="eyebrow">{theme === "emperor" ? "皇上由你担任，旨意交由总管太监传达" : "董事长由你担任，任务交由董事长助理传达"}</p><h2>{definition?.name ?? "公司"}角色</h2></div><span className="status-label"><BadgeCheck aria-hidden="true" size={15} />固定预设</span></div>
        <div className="role-grid">
          {(definition?.roles ?? []).map((role) => <article className="role-card" key={role.id}>
            <div className="role-card-head"><span className="role-initial">{role.title.slice(0, 1)}</span><div><p>{role.department}</p><h3>{role.title}</h3></div></div>
            <p>{role.responsibility}</p><small>{role.focus}</small>
          </article>)}
        </div>
      </section>

      <section className="custom-persona-notice" aria-label="添加自定义人设">
        <div><span className="section-icon compact"><Bot aria-hidden="true" size={17} /></span><div><h2>添加自定义人设</h2><p>在当前主题下增加一个角色，参与任务协作。</p></div></div>
        <button type="button" className="ghost-button" onClick={() => setCustomPersonaOpen((open) => !open)}>{customPersonaOpen ? "收起" : "添加角色"}</button>
      </section>
      {customPersonaOpen && <form className="custom-persona-form" onSubmit={(event) => { event.preventDefault(); savePersona.mutate(); }}><label>角色 ID<input required value={customPersona.persona_id} onChange={(event) => setCustomPersona({ ...customPersona, persona_id: event.target.value })} placeholder="例如 domain-expert" /></label><label>角色名称<input required value={customPersona.display_name} onChange={(event) => setCustomPersona({ ...customPersona, display_name: event.target.value })} placeholder="例如 行业专家" /></label><label>职责描述<input value={customPersona.tone} onChange={(event) => setCustomPersona({ ...customPersona, tone: event.target.value })} placeholder="例如 负责业务判断和方案建议" /></label><label className="wide-field">系统提示词<textarea required value={customPersona.system_prompt} onChange={(event) => setCustomPersona({ ...customPersona, system_prompt: event.target.value })} placeholder="描述这个角色如何工作、如何交付" /></label><button className="primary-button" disabled={savePersona.isPending}>{savePersona.isPending ? "保存中" : "保存自定义角色"}</button>{savePersona.isError && <p className="error-text">保存失败：{savePersona.error.message}</p>}</form>}

      <section className="settings-section agent-binding-section">
        <div className="section-heading"><div><p className="eyebrow">模型绑定</p><h2>Agent 模型</h2></div><span className="muted">一次房间组建后，已选模型保持不变。</span></div>
        {catalog.isError && <p className="error-text" role="alert">无法读取模型目录：{catalog.error.message}</p>}
        {bindingAgents.length === 0 && !catalog.isLoading && <p className="empty-state">还没有可配置的 Agent。请先在模型设置中完成可用模型配置。</p>}
        {bindingAgents.length > 0 && <div className="batch-binding" aria-label="批量模型绑定">
          <div><b>批量设置</b><p>已选择 {selectedAgents.length} 个 Agent</p></div>
          <div className="binding-mode-control" role="radiogroup" aria-label="批量绑定方式">
            <label><input type="radio" checked={bulkBinding.model_binding_mode === "fixed"} onChange={() => setBulkBinding((current) => ({ ...current, model_binding_mode: "fixed" }))} />固定模型</label>
            <label><input type="radio" checked={bulkBinding.model_binding_mode === "auto"} onChange={() => setBulkBinding((current) => ({ ...current, model_binding_mode: "auto" }))} />自动路由</label>
          </div>
          {bulkBinding.model_binding_mode === "fixed" ? <label className="compact-field">模型<select value={bulkBinding.model_profile ?? ""} onChange={(event) => setBulkBinding((current) => ({ ...current, model_profile: event.target.value }))}><option value="">选择模型</option>{profiles.map((item) => <option key={item.profile_id} value={item.profile_id}>{item.display_name || item.profile_id}{item.ready ? "" : "（待验证）"}</option>)}</select></label> : <div className="batch-routing-fields"><label className="compact-field">最低等级<select value={bulkBinding.auto_tier} onChange={(event) => setBulkBinding((current) => ({ ...current, auto_tier: event.target.value }))}>{tierOptions.map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}</select></label><PresetPicker label="模态" options={modalityOptions} value={bulkBinding.auto_modalities} onChange={(value) => setBulkBinding((current) => ({ ...current, auto_modalities: value }))} /></div>}
          <button type="button" className="primary-button" onClick={() => applyBulkBinding.mutate(selectedAgents)} disabled={!canApplyBulk || applyBulkBinding.isPending}>{applyBulkBinding.isPending ? <LoaderCircle className="spin" aria-hidden="true" size={16} /> : <Save aria-hidden="true" size={16} />}{applyBulkBinding.isPending ? "保存中" : "应用到所选"}</button>
          {applyBulkBinding.isError && <p className="error-text" role="alert">批量更新失败：{applyBulkBinding.error.message}</p>}
        </div>}
        <div className="agent-binding-grid">
          {bindingAgents.map((agent) => {
            const draft = agentDrafts[agent.agent_id] ?? agentForm(agent);
            const isFixed = draft.model_binding_mode === "fixed";
            return <article className="agent-binding-card" key={agent.agent_id}>
              <div className="agent-card-title"><label className="agent-select"><input type="checkbox" checked={selectedAgents.includes(agent.agent_id)} onChange={() => toggleSelected(agent.agent_id)} aria-label={`选择 ${agent.display_name || agent.agent_id}`} /><span /></label><div><h3>{agent.display_name || agent.agent_id}</h3><p>{agent.presetRole?.department ?? "已配置身份"} · {agent.responsibility || "未设置职责"}</p></div></div>
              <div className="binding-mode-control" role="radiogroup" aria-label={`${agent.display_name || agent.agent_id} 的模型绑定方式`}>
                <label><input type="radio" checked={isFixed} onChange={() => updateDraft(agent.agent_id, (current) => ({ ...current, model_binding_mode: "fixed" }))} />固定模型</label>
                <label><input type="radio" checked={!isFixed} onChange={() => updateDraft(agent.agent_id, (current) => ({ ...current, model_binding_mode: "auto", model_profile: "" }))} />自动路由</label>
              </div>
              {isFixed ? <label className="binding-field">绑定模型<select value={draft.model_profile} onChange={(event) => updateDraft(agent.agent_id, (current) => ({ ...current, model_profile: event.target.value }))}><option value="">选择模型</option>{profiles.map((item) => <option key={item.profile_id} value={item.profile_id}>{item.display_name || item.profile_id}{item.ready ? "" : "（待验证）"}</option>)}</select></label> : <div className="route-constraints"><div className="route-copy"><Route aria-hidden="true" size={16} /><span>按约束选择合适模型；没有候选时会明确提示。</span></div><label className="binding-field">最低等级<select value={draft.auto_tier} onChange={(event) => updateDraft(agent.agent_id, (current) => ({ ...current, auto_tier: event.target.value }))}>{tierOptions.map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}</select></label><PresetPicker label="所需模态" options={modalityOptions} value={draft.auto_modalities} onChange={(value) => updateDraft(agent.agent_id, (current) => ({ ...current, auto_modalities: value }))} /><PresetPicker label="适用场景" options={scenarioOptions} value={draft.auto_scenarios} onChange={(value) => updateDraft(agent.agent_id, (current) => ({ ...current, auto_scenarios: value }))} /><PresetPicker label="能力要求" options={capabilityOptions} value={draft.auto_capabilities} onChange={(value) => updateDraft(agent.agent_id, (current) => ({ ...current, auto_capabilities: value }))} /></div>}
              <div className="agent-card-footer"><span className={agent.ready ? "model-ready" : "model-pending"}>{agent.ready ? "可参与新任务" : agent.persisted ? "待完善配置" : "等待首次绑定"}</span><button type="button" className="ghost-button" onClick={() => saveAgent.mutate({ agentId: agent.agent_id, body: draft })} disabled={saveAgent.isPending || (isFixed && !draft.model_profile)}>{saveAgent.isPending ? <LoaderCircle className="spin" aria-hidden="true" size={15} /> : <Save aria-hidden="true" size={15} />}{agent.persisted ? "保存绑定" : "创建并绑定"}</button></div>
            </article>;
          })}
        </div>
        {saveAgent.isError && <p className="error-text" role="alert">Agent 绑定保存失败：{saveAgent.error.message}</p>}
      </section>
    </div>}

    {activeTab === "models" && <div className="settings-content">
      <section className="settings-section">
        <div className="section-heading"><div><p className="eyebrow">模型目录</p><h2>通用模型</h2></div><div className="section-heading-actions"><span className="muted">{readyProfileCount}/{profiles.length} 个可执行</span><button type="button" className="primary-button" onClick={resetProfile}><Cpu aria-hidden="true" size={16} />新增模型</button></div></div>
        {profileEditorOpen && <div className="model-editor-wrap"><div className="model-editor-title"><div><p className="eyebrow">{editingProfileId ? "编辑模型" : "新增模型"}</p><h3>{editingProfileId ? `编辑 ${editingProfileId}` : "创建模型配置"}</h3></div><button type="button" className="ghost-button" onClick={() => { setProfileEditorOpen(false); setEditingProfileId(null); clearDiscoveryState(); }}>取消</button></div><form className="model-editor" onSubmit={saveCurrentProfile}>
          <div className="model-form-grid">
            <label>Profile ID<input value={profile.profile_id} disabled={Boolean(editingProfileId)} onChange={(event) => updateProfile({ ...profile, profile_id: event.target.value }, true)} placeholder="例如 glm52" pattern="[A-Za-z0-9_\-]+" maxLength={100} title="请填写英文、数字、短横线或下划线，例如 glm52；模型名称请填在下方。" required /><small className="field-hint">{editingProfileId ? "已配置模型的唯一标识不可修改。" : "内部唯一标识，例如 glm52。模型名称请填入下方。"}</small></label>
            <label>显示名称<input value={profile.display_name} onChange={(event) => setProfile({ ...profile, display_name: event.target.value })} placeholder="例如 视觉审查模型" /></label>
            <label>提供商<input value={profile.provider} onChange={(event) => updateProfile({ ...profile, provider: event.target.value }, true)} placeholder="例如 ModelScope" /></label>
            <label>OpenAI 兼容 URL<input value={profile.base_url} onChange={(event) => updateProfile({ ...profile, base_url: event.target.value }, true)} placeholder="https://provider.example/v1" inputMode="url" /></label>
            <label>API Key<input type="password" value={profile.api_key} onChange={(event) => updateProfile({ ...profile, api_key: event.target.value, clear_api_key: false }, true)} placeholder={profile.profile_id ? "留空表示保留已保存 Key" : "仅写入本机配置"} autoComplete="new-password" /></label>
            <label>环境变量名 <em>可选</em><input value={profile.api_key_env} onChange={(event) => setProfile({ ...profile, api_key_env: event.target.value })} placeholder="例如 DASHSCOPE_API_KEY" /></label>
            <label>模型名称<input value={profile.model} onChange={(event) => setProfile({ ...profile, model: event.target.value })} placeholder="可从下方选择，也可直接手填" /></label>
            {discovered.length > 0 && <label>接口模型列表<select value={discovered.some((item) => item.id === profile.model) ? profile.model : ""} onChange={(event) => { const value = event.target.value; if (value) setProfile((current) => ({ ...current, model: value })); }}><option value="">选择已发现模型</option>{discovered.map((item) => <option key={item.id} value={item.id}>{item.id}{item.owned_by ? ` · ${item.owned_by}` : ""}</option>)}</select><small className="field-hint">选择后会填入上方“模型名称”，仍可继续修改。</small></label>}
            <label>模型等级<select value={profile.tier} onChange={(event) => setProfile({ ...profile, tier: event.target.value })}>{tierOptions.map((option) => <option value={option.value} key={option.value}>{option.label}</option>)}</select></label>
            <label>最大并发<input type="number" min={1} max={64} value={profile.max_concurrency} onChange={(event) => setProfile({ ...profile, max_concurrency: Number(event.target.value) || 1 })} /></label>
            <label className="check-field"><input type="checkbox" checked={profile.enabled} onChange={(event) => setProfile({ ...profile, enabled: event.target.checked })} />允许用于新任务</label>
            <div className="wide-field"><PresetPicker label="支持模态" options={modalityOptions} value={profile.modalities ?? []} onChange={(value) => setProfile({ ...profile, modalities: value })} /></div>
            <div className="wide-field"><PresetPicker label="适用场景" options={scenarioOptions} value={profile.scenarios ?? []} onChange={(value) => setProfile({ ...profile, scenarios: value })} /></div>
            <div className="wide-field"><PresetPicker label="能力标签" options={capabilityOptions} value={profile.capabilities ?? []} onChange={(value) => setProfile({ ...profile, capabilities: value })} /></div>
          </div>
          <div className="settings-actions">
            <button type="button" className="ghost-button" onClick={() => discover.mutate()} disabled={!profile.base_url || discover.isPending}>{discover.isPending ? <LoaderCircle aria-hidden="true" size={16} className="spin" /> : <RefreshCw aria-hidden="true" size={16} />}{discover.isPending ? "正在获取" : "获取模型"}</button>
            <button type="button" className="ghost-button" onClick={resetProfile} disabled={!profile.profile_id}>清空表单</button>
            {profile.profile_id && <button type="button" className="ghost-button danger-button" onClick={() => setProfile({ ...profile, api_key: "", clear_api_key: true })}><KeyRound aria-hidden="true" size={15} />清除已存 Key</button>}
            <button className="primary-button" disabled={saveProfile.isPending}>{saveProfile.isPending ? <LoaderCircle aria-hidden="true" size={16} className="spin" /> : <Save aria-hidden="true" size={16} />}{saveProfile.isPending ? "保存中" : "保存模型"}</button>
          </div>
        </form></div>}
        {!profileEditorOpen && profiles.length === 0 && !catalog.isLoading && <p className="empty-state">还没有模型。点击“新增模型”开始配置。</p>}
        {discover.isError && <p className="error-text" role="alert"><CircleAlert aria-hidden="true" size={15} />模型发现失败：{discover.error.message}。请确认 URL 是可从当前环境访问的公网供应商地址（不要填写 localhost 或内网地址）；复制模型后如果改了 URL，需要重新填写对应 API Key。发现失败不影响手填模型名称并保存为待验证。</p>}
        {saveProfile.isError && <p className="error-text" role="alert">模型保存失败：{saveProfile.error.message}</p>}
        {deleteProfile.isError && <p className="error-text" role="alert">模型删除失败：{deleteProfile.error.message}</p>}
        {verifyProfile.isSuccess && <p className="success-text" role="status">{verifyProfile.data.message}</p>}
        {verifyProfile.isError && <p className="error-text" role="alert">{verifyProfile.error.message}</p>}
        {discovered.length > 0 && <p className="discovery-summary"><Eye aria-hidden="true" size={15} />已获取 {discovered.length} 个模型。选择或手填模型名称后保存。</p>}
      </section>
      <section className="settings-section model-list-section">
        <div className="section-heading"><div><p className="eyebrow">已配置</p><h2>模型列表</h2></div></div>
        <div className="configured-model-list">
          {profiles.map((item) => <article className="configured-model" key={item.profile_id}>
            <div className="configured-model-title"><span className="model-glyph"><Cpu aria-hidden="true" size={17} /></span><div><h3>{item.display_name || item.profile_id}</h3><p>{item.provider || "未设置提供商"} · {item.model || "未选择模型"}</p></div></div>
            <div className="model-tags"><span>{tierOptions.find((option) => option.value === item.tier)?.label ?? item.tier}</span>{(item.modalities ?? []).slice(0, 3).map((modality) => <span key={modality}>{modalityOptions.find((option) => option.value === modality)?.label ?? modality}</span>)}</div>
            <div className="configured-model-meta"><span className={item.ready ? "model-ready" : "model-pending"}>{item.ready ? "已就绪" : "待验证"}</span><span>{item.enabled ? "已启用" : "未启用"}</span><span>{item.has_api_key ? "Key 已配置" : "未配置 Key"}</span><span>并发 {item.max_concurrency}</span></div>
            {!item.ready && item.readiness_issues.length > 0 && <p className="model-issues">{item.readiness_issues.join("；")}</p>}
            <div className="configured-model-actions"><button type="button" className="ghost-button" onClick={() => editProfile(item)}>编辑并处理</button><button type="button" className="ghost-button" onClick={() => cloneProfile.mutate(item.profile_id)} disabled={cloneProfile.isPending}><Copy aria-hidden="true" size={15} />复制</button>{item.provider && item.model && item.has_api_key && <button type="button" className="ghost-button" onClick={() => verifyProfile.mutate(item.profile_id)} disabled={verifyProfile.isPending}>{verifyProfile.isPending ? "验证中" : "验证连接"}</button>}<button type="button" className="ghost-button danger-button" onClick={() => deleteProfile.mutate(item.profile_id)} disabled={deleteProfile.isPending}><Trash2 aria-hidden="true" size={15} />删除</button></div>
          </article>)}
        </div>
        {cloneProfile.isError && <p className="error-text" role="alert">复制模型失败：{cloneProfile.error.message}</p>}
      </section>
    </div>}

    {activeTab === "appearance" && <div className="settings-content">
      <section className="settings-section page-settings-section">
        <div className="section-heading"><div><p className="eyebrow">主题</p><h2>页面风格</h2></div></div>
        <ThemeSwitch selected={theme ?? "company"} onSelect={setTheme} />
        <p className="appearance-note">这里切换整套角色包装。新增单个角色请在人设设置中操作；创建一整套全新角色体系属于主题设置。</p>
        <div className="custom-persona-notice theme-persona-action"><div><span className="section-icon compact"><Paintbrush aria-hidden="true" size={17} /></span><div><h2>创建新的人设体系</h2><p>自定义主题名称、角色集合和称谓映射。</p></div></div><button type="button" className="ghost-button" disabled title="整套人设体系编辑将在后续版本开放">待开发</button></div>
      </section>
    </div>}
  </section>;
}
