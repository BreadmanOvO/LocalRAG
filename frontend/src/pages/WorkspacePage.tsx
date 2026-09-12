import { FormEvent, useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { api } from "../shared/api/client";

export function WorkspacePage() {
  const navigate = useNavigate();
  const [spaceId, setSpaceId] = useState("space-demo");
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const health = useQuery({ queryKey: ["health"], queryFn: api.health });
  const create = useMutation({ mutationFn: () => api.assistantMessage(spaceId, content, title), onSuccess: (result) => navigate(`/rooms/${result.room.room_id}`) });
  const submit = (event: FormEvent) => { event.preventDefault(); if (content.trim()) create.mutate(); };

  return (
    <section className="page workspace-page">
      <header className="page-header">
        <div><p className="eyebrow">统一入口</p><h1>今天要推进什么？</h1><p className="subtitle">总助理负责判断任务边界，Runtime 负责执行和追踪。</p></div>
        <span className={health.isSuccess ? "health-pill ready" : "health-pill"}>{health.isSuccess ? "运行正常" : "检查 API"}</span>
      </header>
      <div className="hero-grid">
        <article className="panel composer-panel">
          <div className="panel-heading"><div><p className="eyebrow">新建房间</p><h2>从一个目标开始</h2></div><span className="panel-icon">✦</span></div>
          <form onSubmit={submit} className="room-form">
            <label>空间标识<input value={spaceId} onChange={(e) => setSpaceId(e.target.value)} required /></label>
            <label>任务标题（可选）<input value={title} onChange={(e) => setTitle(e.target.value)} placeholder="不填则从目标自动生成" /></label>
            <label>告诉总助理你的目标<textarea className="composer-textarea" value={content} onChange={(e) => setContent(e.target.value)} placeholder="例如：比较两篇方案并指出证据缺口" required rows={5} /></label>
            <button className="primary-button" disabled={create.isPending || !content.trim()}>{create.isPending ? "正在保存…" : "开始任务 →"}</button>
            {create.isError && <p className="error-text">{create.error.message}</p>}
          </form>
        </article>
        <article className="panel principle-panel"><p className="eyebrow">运行原则</p><h2>工具可插拔，状态可追溯</h2><p>RAG、文件分析和多 Agent 协作都通过统一 Runtime 接入。页面只展示状态，不在浏览器里复制调度逻辑。</p><div className="principle-list"><span>01</span><b>一个入口</b><span>02</span><b>需要分工时再组群</b><span>03</span><b>每一步都可回放</b></div></article>
      </div>
    </section>
  );
}
