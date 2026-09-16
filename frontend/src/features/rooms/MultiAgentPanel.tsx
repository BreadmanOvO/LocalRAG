import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { LoaderCircle, UsersRound } from "lucide-react";
import { api, type MultiAgentExecution } from "../../shared/api/client";

export function MultiAgentPanel({ roomId }: { roomId: string }) {
  const [goal, setGoal] = useState("");
  const [result, setResult] = useState<MultiAgentExecution | null>(null);
  const queryClient = useQueryClient();
  const roomEvents = useQuery({ queryKey: ["events", roomId], queryFn: () => api.events(roomId), enabled: Boolean(roomId) });
  const selectedArchitecture = roomEvents.data?.items.find((event) => event.event_type === "room_architecture_selected")?.payload.architecture;
  const execute = useMutation({
    mutationFn: () => api.executeMultiAgent(roomId, goal.trim(), (selectedArchitecture === "direct" || selectedArchitecture === "hierarchical" || selectedArchitecture === "swarm" || selectedArchitecture === "adversarial" || selectedArchitecture === "heterogeneous" || selectedArchitecture === "graph" ? selectedArchitecture : "auto"), 3),
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

  return <section className="coordination-panel">
    <div className="coordination-heading"><span className="section-icon compact"><UsersRound aria-hidden="true" size={17} /></span><div><h2>召集项目组</h2><p>为当前任务补充需要协作处理的目标。</p></div></div>
    <div className="coordination-controls">
      <textarea aria-label="协作目标" className="composer-textarea" rows={2} value={goal} onChange={(event) => setGoal(event.target.value)} placeholder="例如：请分别核验方案可行性、证据完整性和实施风险" />
      <button type="button" className="primary-button" onClick={() => execute.mutate()} disabled={execute.isPending || !goal.trim()}>{execute.isPending ? <LoaderCircle aria-hidden="true" size={16} className="spin" /> : <UsersRound aria-hidden="true" size={16} />}{execute.isPending ? "正在组织" : "开始协作"}</button>
    </div>
    {execute.isError && <p className="error-text" role="alert">项目组未能启动：{execute.error.message}</p>}
    {result && <div className="coordination-result"><p>{result.final}</p><div className="coordination-result-meta"><span>{result.turns.length} 次成员发言</span>{result.turns.filter((turn) => turn.model).map((turn) => <span key={`${turn.agent_id}-${turn.sequence}`}>{turn.agent_id} · {turn.model}</span>)}</div></div>}
  </section>;
}
