import { FormEvent, useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import type { components } from "../shared/api/schema";
import { api } from "../shared/api/client";

type Profile = components["schemas"]["ModelProfileResponse"];
type Agent = components["schemas"]["AgentConfigResponse"];
type DiscoveredModel = components["schemas"]["DiscoveredModelResponse"];
type ProfileForm = components["schemas"]["ModelProfileRequest"];
type AgentForm = components["schemas"]["AgentConfigRequest"];

const emptyProfile: ProfileForm = { profile_id: "", display_name: "", provider: "", base_url: "", model: "", api_key_env: "", api_key: "", capabilities: [], modalities: ["text"], scenarios: [], tier: "standard", max_concurrency: 4, enabled: false, clear_api_key: false };
const emptyAgent: AgentForm = { agent_id: "", display_name: "", responsibility: "", model_profile: "", tier: "standard", capabilities: [], modalities: ["text"], system_prompt: "", enabled: false };
const csv = (value: string) => value.split(",").map((item) => item.trim()).filter(Boolean);

export function CompanyPage() {
  const queryClient = useQueryClient();
  const roles = useQuery({ queryKey: ["roles"], queryFn: api.roles });
  const catalog = useQuery({ queryKey: ["model-catalog"], queryFn: api.modelCatalog });
  const profiles = catalog.data?.profiles ?? [];
  const agents = catalog.data?.agents ?? [];
  const [profile, setProfile] = useState<ProfileForm>(emptyProfile);
  const [agent, setAgent] = useState<AgentForm>(emptyAgent);
  const [discovered, setDiscovered] = useState<DiscoveredModel[]>([]);
  const refresh = (data: unknown) => queryClient.setQueryData(["model-catalog"], data);
  const saveProfile = useMutation({ mutationFn: () => api.saveModelProfile(profile.profile_id, profile), onSuccess: refresh });
  const saveAgent = useMutation({ mutationFn: () => api.saveAgentConfig(agent.agent_id, agent), onSuccess: refresh });
  const deleteProfile = useMutation({ mutationFn: (id: string) => api.deleteModelProfile(id), onSuccess: refresh });
  const deleteAgent = useMutation({ mutationFn: (id: string) => api.deleteAgentConfig(id), onSuccess: refresh });
  const discover = useMutation({ mutationFn: () => api.discoverModels(profile.base_url, profile.api_key, profile.profile_id), onSuccess: (data) => setDiscovered(data.items) });
  const readyProfileCount = useMemo(() => profiles.filter((item) => item.ready).length, [profiles]);
  const submitProfile = (event: FormEvent) => { event.preventDefault(); if (profile.profile_id.trim()) saveProfile.mutate(); };
  const submitAgent = (event: FormEvent) => { event.preventDefault(); if (agent.agent_id.trim()) saveAgent.mutate(); };
  const editProfile = (item: Profile) => setProfile({ ...emptyProfile, ...item, api_key: "", clear_api_key: false });
  const editAgent = (item: Agent) => setAgent({ ...emptyAgent, ...item });
  const changeProfile = (next: ProfileForm) => { setProfile(next); setDiscovered([]); };
  const useRole = (role: components["schemas"]["RoleResponse"]) => setAgent({
    ...emptyAgent,
    agent_id: role.role_id.replace(/^role-/, "").replace(/-/g, "_"),
    display_name: role.name,
    responsibility: role.responsibilities.join("、"),
    capabilities: role.capabilities,
    modalities: role.capabilities.some((item) => ["vision", "ocr", "visual_grounding"].includes(item)) ? ["text", "image"] : ["text"],
    system_prompt: `你是${role.department}的${role.name}。负责${role.responsibilities.join("、")}。交付时说明依据、结论和未解决问题。`,
  });
  return <section className="page">
    <header className="page-header"><div><p className="eyebrow">公司设置</p><h1>角色、模型与人设</h1><p className="subtitle">模型目录和 Agent 身份都可以在这里维护。保存后写入本机 JSON；正在运行的任务继续使用启动时快照。</p></div></header>
    <div className="panel-heading"><div><p className="eyebrow">岗位模板</p><h2>从公司角色创建 Agent</h2></div><span className="muted">{roles.data?.items.length ?? 0} 个预设，也可完全自定义</span></div>
    <div className="role-grid">{roles.data?.items.map((role) => <article className="panel role-card" key={role.role_id}><p className="eyebrow">{role.department}</p><h2>{role.name}</h2><p className="muted">职责：{role.responsibilities.join("、")}</p><p className="muted">能力：{role.capabilities.join(" · ")}</p><button type="button" className="ghost-button" onClick={() => useRole(role)}>用于新 Agent</button></article>)}</div>
    <article className="panel model-settings"><div className="panel-heading"><div><p className="eyebrow">模型目录</p><h2>新增或编辑模型</h2></div><span className="muted">{readyProfileCount}/{profiles.length} 个模型可执行</span></div>
      <p className="muted">可以先只填 Profile ID，之后再补提供商、兼容 URL、模型和 Key。URL 支持 OpenAI-compatible 的基础地址或直接填写 `/models` 地址。</p>
      <form className="model-editor" onSubmit={submitProfile}><div className="model-form-grid">
        <label>Profile ID<input value={profile.profile_id} onChange={(e) => changeProfile({ ...profile, profile_id: e.target.value })} placeholder="例如 vl-reviewer" required /></label><label>显示名称<input value={profile.display_name} onChange={(e) => setProfile({ ...profile, display_name: e.target.value })} placeholder="视觉审查模型" /></label><label>提供商<input value={profile.provider} onChange={(e) => changeProfile({ ...profile, provider: e.target.value })} placeholder="可先留空" /></label><label>OpenAI 兼容 URL<input value={profile.base_url} onChange={(e) => changeProfile({ ...profile, base_url: e.target.value })} placeholder="https://.../v1" /></label><label>API Key<input type="password" value={profile.api_key} onChange={(e) => setProfile({ ...profile, api_key: e.target.value, clear_api_key: false })} placeholder={profile.profile_id ? "留空表示保留已保存 Key" : "仅写入本机配置"} autoComplete="new-password" /></label><label>模型名称<select value={profile.model} onChange={(e) => setProfile({ ...profile, model: e.target.value })}><option value="">先获取模型列表</option>{discovered.map((item) => <option key={item.id} value={item.id}>{item.id}{item.owned_by ? ` (${item.owned_by})` : ""}</option>)}</select></label><label>模型等级<input value={profile.tier} onChange={(e) => setProfile({ ...profile, tier: e.target.value })} placeholder="lead / specialist / critic" /></label><label>支持模态<input value={(profile.modalities ?? []).join(",")} onChange={(e) => setProfile({ ...profile, modalities: csv(e.target.value) })} placeholder="text,image,pdf,table" /></label><label>适合场景<input value={(profile.scenarios ?? []).join(",")} onChange={(e) => setProfile({ ...profile, scenarios: csv(e.target.value) })} placeholder="图片理解,图表审查" /></label><label>能力标签<input value={(profile.capabilities ?? []).join(",")} onChange={(e) => setProfile({ ...profile, capabilities: csv(e.target.value) })} placeholder="reasoning,ocr,rag" /></label><label>最大并发<input type="number" min={1} value={profile.max_concurrency} onChange={(e) => setProfile({ ...profile, max_concurrency: Number(e.target.value) || 1 })} /></label><label className="check-field"><input type="checkbox" checked={profile.enabled} onChange={(e) => setProfile({ ...profile, enabled: e.target.checked })} />允许运行新任务</label>
      </div><div className="settings-actions"><button type="button" className="ghost-button" onClick={() => discover.mutate()} disabled={!profile.base_url || discover.isPending}>{discover.isPending ? "获取中…" : "一键获取模型"}</button>{profile.profile_id && <button type="button" className="ghost-button" onClick={() => setProfile(emptyProfile)}>清空表单</button>}{profile.profile_id && <button type="button" className="ghost-button danger-button" onClick={() => setProfile({ ...profile, api_key: "", clear_api_key: true })}>清除已存 Key</button>}<button className="primary-button" disabled={saveProfile.isPending}>保存模型</button></div></form>
      {discover.isError && <p className="error-text">模型发现失败：{discover.error.message}</p>}{deleteProfile.isError && <p className="error-text">模型删除失败：{deleteProfile.error.message}</p>}{discovered.length > 0 && <p className="muted">已发现 {discovered.length} 个模型，选择模型名称后保存即可。</p>}{saveProfile.isError && <p className="error-text">模型保存失败：{saveProfile.error.message}</p>}
      {profiles.map((item) => <div className="model-row" key={item.profile_id}><div><b>{item.display_name || item.profile_id}</b><p className="muted">{item.provider || "未设置提供商"} · {item.model || "未选择模型"} · {item.tier || "standard"}</p><small className="muted">模态：{(item.modalities ?? []).join("、")}；场景：{(item.scenarios ?? []).join("、") || "未定义"}；{item.has_api_key ? "已配置 Key" : "未配置 Key"}；{item.ready ? "可执行" : `未就绪：${(item.readiness_issues ?? []).join("、")}`}</small></div><div className="settings-actions"><button className="ghost-button" onClick={() => editProfile(item)}>编辑</button><button className="ghost-button danger-button" onClick={() => deleteProfile.mutate(item.profile_id)} disabled={deleteProfile.isPending}>删除</button></div></div>)}
    </article>
    <article className="panel model-settings"><div className="panel-heading"><div><p className="eyebrow">Agent 身份</p><h2>新增或编辑 Agent</h2></div><span className="muted">{agents.length} 个身份</span></div>
      <form className="model-editor" onSubmit={submitAgent}><div className="model-form-grid"><label>Agent ID<input value={agent.agent_id} onChange={(e) => setAgent({ ...agent, agent_id: e.target.value })} placeholder="例如 visual_reviewer" required /></label><label>显示名称<input value={agent.display_name} onChange={(e) => setAgent({ ...agent, display_name: e.target.value })} placeholder="图片审查员" /></label><label>绑定模型<select value={agent.model_profile} onChange={(e) => setAgent({ ...agent, model_profile: e.target.value })}><option value="">暂不绑定</option>{profiles.map((item) => <option key={item.profile_id} value={item.profile_id}>{item.display_name || item.profile_id}</option>)}</select></label><label>Agent 等级<input value={agent.tier} onChange={(e) => setAgent({ ...agent, tier: e.target.value })} placeholder="lead / specialist / critic" /></label><label>支持模态<input value={(agent.modalities ?? []).join(",")} onChange={(e) => setAgent({ ...agent, modalities: csv(e.target.value) })} placeholder="text,image" /></label><label>能力标签<input value={(agent.capabilities ?? []).join(",")} onChange={(e) => setAgent({ ...agent, capabilities: csv(e.target.value) })} placeholder="research,review" /></label><label>职责<input value={agent.responsibility} onChange={(e) => setAgent({ ...agent, responsibility: e.target.value })} placeholder="负责什么任务" /></label><label className="wide-field">人设提示词<textarea value={agent.system_prompt} onChange={(e) => setAgent({ ...agent, system_prompt: e.target.value })} placeholder="这个 Agent 如何工作、如何表达和如何交付" rows={3} /></label><label className="check-field"><input type="checkbox" checked={agent.enabled} onChange={(e) => setAgent({ ...agent, enabled: e.target.checked })} />允许参与新任务</label></div><div className="settings-actions"><button type="button" className="ghost-button" onClick={() => setAgent(emptyAgent)}>清空表单</button><button className="primary-button" disabled={saveAgent.isPending}>保存 Agent</button></div></form>
      {saveAgent.isError && <p className="error-text">Agent 保存失败：{saveAgent.error.message}</p>}{deleteAgent.isError && <p className="error-text">Agent 删除失败：{deleteAgent.error.message}</p>}{agents.map((item) => <div className="model-row" key={item.agent_id}><div><b>{item.display_name || item.agent_id}</b><p className="muted">{item.agent_id} · {item.model_profile || "未绑定模型"} · {item.tier || "standard"}</p><small className="muted">{item.ready ? "可执行" : `未就绪：${(item.readiness_issues ?? []).join("、")}`}</small></div><div className="settings-actions"><button className="ghost-button" onClick={() => editAgent(item)}>编辑</button><button className="ghost-button danger-button" onClick={() => deleteAgent.mutate(item.agent_id)} disabled={deleteAgent.isPending}>删除</button></div></div>)}
    </article>
  </section>;
}
