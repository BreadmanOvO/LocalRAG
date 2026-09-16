import { FormEvent, useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { ArrowRight, LoaderCircle, Sparkles } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { rememberRoomTheme, useTheme } from "../app/theme";
import { api } from "../shared/api/client";
import { stableSpaceId } from "../shared/space";

export function WorkspacePage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { definition, theme } = useTheme();
  const [spaceId] = useState(stableSpaceId);
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [architecture, setArchitecture] = useState<"auto" | "direct" | "hierarchical" | "swarm" | "adversarial" | "heterogeneous" | "graph">("auto");
  const create = useMutation({
    mutationFn: () => api.assistantMessage(spaceId, content.trim(), title.trim(), theme ?? undefined, architecture),
    onSuccess: (result) => {
      void queryClient.invalidateQueries({ queryKey: ["rooms"] });
      if (theme) rememberRoomTheme(result.room.room_id, theme);
      navigate(`/rooms/${result.room.room_id}`);
    },
  });
  const submit = (event: FormEvent) => {
    event.preventDefault();
    if (content.trim()) create.mutate();
  };

  return <section className="page workspace-page">
    <header className="product-page-header">
      <span className="section-icon"><Sparkles aria-hidden="true" size={18} /></span>
      <div>
        <p className="eyebrow">新任务</p>
        <h1>{definition?.taskHeading ?? "下达新任务"}</h1>
        <p className="subtitle">交代目标，随后在专属房间查看进度、协作和结果。</p>
      </div>
    </header>
    <form className="task-composer" onSubmit={submit}>
      <label>
        <span>任务标题 <em>可选</em></span>
        <input value={title} onChange={(event) => setTitle(event.target.value)} placeholder="例如：梳理 BEVFormer 的训练数据和设计取舍" maxLength={120} />
      </label>
      <label className="task-instruction-field">
        <span>{definition?.taskAction ?? "下达任务"}</span>
        <textarea className="composer-textarea" value={content} onChange={(event) => setContent(event.target.value)} placeholder={definition?.taskPlaceholder ?? "说明目标、已知信息和你期待的交付结果"} required rows={7} />
      </label>
      <div className="task-submit-row">
        <p>系统会为这项任务分配独立房间。</p>
        <label className="task-mode-select">协作模式<select value={architecture} onChange={(event) => setArchitecture(event.target.value as typeof architecture)}><option value="auto">自动路由（推荐）</option><option value="direct">直接处理</option><option value="hierarchical">分层协作</option><option value="swarm">蜂群协作</option><option value="adversarial">对抗协作</option><option value="heterogeneous">异构协作</option><option value="graph">图式协作</option></select></label>
        <button className="primary-button" disabled={create.isPending || !content.trim()}>
          {create.isPending ? <LoaderCircle aria-hidden="true" size={16} className="spin" /> : <ArrowRight aria-hidden="true" size={16} />}
          {create.isPending ? "正在创建" : definition?.taskAction ?? "下达任务"}
        </button>
      </div>
      {create.isError && <p className="error-text" role="alert">创建任务失败：{create.error.message}</p>}
    </form>
  </section>;
}
