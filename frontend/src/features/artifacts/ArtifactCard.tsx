import { useState } from "react";
import { FileOutput } from "lucide-react";
import type { Artifact } from "../../shared/api/client";
import { formatDateTime } from "../../shared/time";

export function ArtifactCard({ artifacts, loading = false }: { artifacts: Artifact[]; loading?: boolean }) {
  const [expanded, setExpanded] = useState<string | null>(null);
  return <div className="artifact-card"><div className="panel-heading"><h2>任务产物</h2><span className="muted">{artifacts.length} 项</span></div>
    {loading && <p className="empty-state">正在整理产物…</p>}
    {!loading && artifacts.length === 0 && <p className="empty-state">完成的步骤会在这里生成可追溯产物。</p>}
    <div className="artifact-list">{artifacts.map((artifact) => { const open = expanded === artifact.artifact_id; return <article className="artifact-item" key={artifact.artifact_id}>
      <button type="button" className="artifact-item-toggle" onClick={() => setExpanded(open ? null : artifact.artifact_id)}><FileOutput size={16} /><span><b>{artifact.title}</b><small>{artifact.source_agent_name || artifact.source_agent_id || "任务成员"} · {formatDateTime(artifact.timestamp)}</small></span><em>{artifact.is_final ? "最终" : artifact.artifact_type}</em></button>
      {open && <div className="artifact-content"><pre>{artifact.content || "暂无文本内容"}</pre><small>事件 {artifact.source_event_id}{artifact.source_step_id ? ` · ${artifact.source_step_id}` : ""}</small></div>}
    </article>; })}</div>
  </div>;
}
