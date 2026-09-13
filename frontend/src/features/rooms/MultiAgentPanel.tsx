import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { api, type MultiAgentExecution } from "../../shared/api/client";

const architectures = [
  ["hierarchical", "分层协作"],
  ["swarm", "共享汇总（实验）"],
  ["adversarial", "对抗审查"],
  ["direct", "单 Agent"],
] as const;

export function MultiAgentPanel({ roomId }: { roomId: string }) {
  const [goal, setGoal] = useState("");
  const [architecture, setArchitecture] = useState<(typeof architectures)[number][0]>("hierarchical");
  const [result, setResult] = useState<MultiAgentExecution | null>(null);
  const queryClient = useQueryClient();
  const execute = useMutation({
    mutationFn: () => api.executeMultiAgent(roomId, goal.trim(), architecture, 3),
    onSuccess: (value) => {
      setResult(value);
      setGoal("");
    },
    onSettled: () => {
      void queryClient.invalidateQueries({ queryKey: ["messages", roomId] });
      void queryClient.invalidateQueries({ queryKey: ["events", roomId] });
      void queryClient.invalidateQueries({ queryKey: ["members", roomId] });
    },
  });

  return <article className="panel multi-agent-panel">
    <div className="panel-heading"><h2>多 Agent 执行</h2><span className="muted">结果会写入当前群聊</span></div>
    <div className="multi-agent-controls">
      <select aria-label="协作架构" value={architecture} onChange={(event) => setArchitecture(event.target.value as typeof architecture)}>
        {architectures.map(([value, label]) => <option key={value} value={value}>{label}</option>)}
      </select>
      <textarea aria-label="任务目标" className="composer-textarea" rows={2} value={goal} onChange={(event) => setGoal(event.target.value)} placeholder="交给团队一个需要协作的目标…" />
      <button type="button" className="primary-button" onClick={() => execute.mutate()} disabled={execute.isPending || !goal.trim()}>{execute.isPending ? "执行中…" : "启动团队"}</button>
    </div>
    {execute.isError && <p className="error-text">团队执行失败：{execute.error.message}</p>}
    {result && <div className="multi-agent-result"><p><b>最终答复</b></p><p>{result.final}</p><small>{result.architecture} · {result.turns.length} 次发言 · run {result.run_id}</small></div>}
  </article>;
}
