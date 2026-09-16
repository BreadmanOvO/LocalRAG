import { useCallback, useEffect, useMemo, useState } from "react";
import { Background, Controls, Handle, MarkerType, MiniMap, Position, ReactFlow, type Edge, type Node, type NodeMouseHandler, type NodeProps, type ReactFlowInstance } from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import { AlertTriangle, Bot, Clock, Pause, Play, Radio, StepBack, StepForward, X } from "lucide-react";
import type { Event } from "../../shared/api/client";
import { roomTheme, themes } from "../../app/theme";
import { architectureLabels, architectureStages, projectCollaboration, stateLabels, type TaskStep } from "./collaborationGraphModel";
import { formatDateTime } from "../../shared/time";
import "./CollaborationBoard.css";

type AgentNodeData = { step: TaskStep; title: string; initials: string };
const runStateLabels: Record<string, string> = { queued: "等待开始", running: "进行中", run_completed: "本轮完成", run_failed: "本轮失败", run_cancelled: "本轮已取消", run_paused: "本轮已暂停" };

function durationLabel(value: number | undefined): string {
  if (value === undefined) return "未记录";
  if (value < 1000) return `${value} ms`;
  const seconds = Math.round(value / 1000);
  return seconds < 60 ? `${seconds} 秒` : `${Math.floor(seconds / 60)} 分 ${seconds % 60} 秒`;
}

function AgentNode({ data, selected }: NodeProps<Node<AgentNodeData>>) {
  const { step, title, initials } = data;
  return <div className={`agent-flow-node state-${step.state} ${selected ? "selected" : ""}`}>
    <Handle type="target" position={Position.Top} />
    <div className="agent-flow-avatar" data-agent-id={step.agentId}><span>{initials}</span></div>
    <div className="agent-flow-copy"><strong>{title}</strong><span>{step.title}</span><small>{stateLabels[step.state]}{step.model ? ` · ${step.model}` : ""}</small></div>
    {step.state === "running" && <span className="agent-flow-pulse" aria-label="正在处理" />}
    <Handle type="source" position={Position.Bottom} />
  </div>;
}

const nodeTypes = { agent: AgentNode };

function depthByStep(steps: TaskStep[]): Map<number, number> {
  const depths = new Map<number, number>();
  for (const step of [...steps].sort((a, b) => a.sequence - b.sequence)) depths.set(step.sequence, step.dependencies.length ? Math.max(...step.dependencies.map((id) => depths.get(id) ?? 0)) + 1 : 0);
  return depths;
}

function positions(steps: TaskStep[], architecture: string): Map<number, { x: number; y: number }> {
  const result = new Map<number, { x: number; y: number }>();
  const depths = depthByStep(steps);
  const groups = new Map<number, TaskStep[]>();
  for (const step of steps) { const depth = depths.get(step.sequence) ?? 0; groups.set(depth, [...(groups.get(depth) ?? []), step]); }
  const maxWidth = Math.max(1, ...[...groups.values()].map((items) => items.length));
  for (const [depth, items] of groups) items.forEach((step, index) => {
    let x = (index - (items.length - 1) / 2) * 270;
    if (architecture === "adversarial" && depth > 0 && !step.isFinal) x = index % 2 === 0 ? -240 : 240;
    if (architecture === "heterogeneous" && items.length > 1) x = (index - (items.length - 1) / 2) * 320;
    if (architecture === "direct") x = 0;
    result.set(step.sequence, { x: x + maxWidth * 15, y: depth * 175 });
  });
  return result;
}

export function CollaborationGraph({ roomId, events, connected, focusSequence = null }: { roomId: string; events: Event[]; connected: boolean; focusSequence?: number | null }) {
  const runs = useMemo(() => [...new Set(events.map((event) => event.run_id).filter((id): id is string => typeof id === "string" && Boolean(id)))], [events]);
  const [selectedRun, setSelectedRun] = useState("");
  const [cursor, setCursor] = useState<number | null>(null);
  const [playing, setPlaying] = useState(false);
  const [selectedStepId, setSelectedStepId] = useState("");
  const [flowInstance, setFlowInstance] = useState<ReactFlowInstance<Node<AgentNodeData>, Edge> | null>(null);
  const runId = selectedRun || runs[runs.length - 1] || "";
  const runEvents = useMemo(() => runId ? events.filter((event) => event.run_id === runId) : [], [events, runId]);
  const count = cursor === null ? runEvents.length : Math.min(cursor, runEvents.length);
  const visibleEvents = runEvents.slice(0, count);
  const resumeFrom = visibleEvents.find((event) => event.event_type === "run_started")?.payload.resumed_from;
  const priorEvents = typeof resumeFrom === "string" ? events.filter((event) => event.run_id === resumeFrom) : [];
  const board = useMemo(() => projectCollaboration(visibleEvents, priorEvents), [visibleEvents, priorEvents]);
  const storedTheme = events.find((event) => event.event_type === "room_persona_selected")?.payload.persona_theme;
  const theme = storedTheme === "emperor" || storedTheme === "company" ? storedTheme : roomTheme(roomId) ?? "company";
  const roleTitles = useMemo(() => new Map(themes[theme].roles.map((role) => [role.id, role.title])), [theme]);
  const layout = useMemo(() => positions(board.steps, board.architecture), [board.steps, board.architecture]);
  const flowNodes = useMemo<Node<AgentNodeData>[]>(() => board.steps.map((step) => {
    const title = step.agentName && step.agentName !== step.agentId ? step.agentName : roleTitles.get(step.agentId) ?? step.agentId;
    return { id: step.id, type: "agent", position: layout.get(step.sequence) ?? { x: 0, y: step.sequence * 160 }, data: { step, title, initials: title.slice(0, 2) }, selected: step.id === selectedStepId };
  }), [board.steps, layout, roleTitles, selectedStepId]);
  const flowEdges = useMemo<Edge[]>(() => {
    const bySequence = new Map(board.steps.map((step) => [step.sequence, step.id]));
    return board.steps.flatMap((step) => step.dependencies.flatMap((dependency) => {
      const source = bySequence.get(dependency); if (!source) return [];
      const handoff = board.handoffs.find((item) => item.sourceSequence === dependency && item.targetSequence === step.sequence);
      return [{ id: `edge-${dependency}-${step.sequence}`, source, target: step.id, animated: step.state === "running" || Boolean(handoff?.acceptedAt), label: handoff?.acceptedAt ? "已交接" : "", markerEnd: { type: MarkerType.ArrowClosed }, className: `architecture-edge architecture-${board.architecture}` }];
    }));
  }, [board.steps, board.handoffs, board.architecture]);
  const selectedStep = board.steps.find((step) => step.id === selectedStepId);
  const relatedHandoffs = selectedStep ? board.handoffs.filter((handoff) => handoff.fromStepId === selectedStep.id || handoff.toStepId === selectedStep.id) : [];
  const memoryEvent = visibleEvents.find((event) => event.event_type === "memory_read");

  useEffect(() => { setCursor(null); setPlaying(false); setSelectedStepId(""); }, [runId]);
  useEffect(() => {
    if (focusSequence === null) return;
    const step = board.steps.find((item) => item.sequence === focusSequence);
    if (!step) return;
    setSelectedStepId(step.id);
    const point = layout.get(step.sequence);
    if (flowInstance && point) void flowInstance.setCenter(point.x + 115, point.y + 48, { zoom: 1, duration: 350 });
  }, [board.steps, flowInstance, focusSequence, layout]);
  useEffect(() => { if (!playing) return; const timer = window.setInterval(() => setCursor((current) => { const next = Math.min((current ?? 0) + 1, runEvents.length); if (next >= runEvents.length) setPlaying(false); return next; }), 650); return () => window.clearInterval(timer); }, [playing, runEvents.length]);
  const seek = (next: number) => { setPlaying(false); setCursor(Math.max(0, Math.min(runEvents.length, next))); };
  const onNodeClick = useCallback<NodeMouseHandler>((_, node) => setSelectedStepId(node.id), []);

  return <article className="panel collaboration-board">
    <header className="collaboration-board-header"><div><p className="eyebrow">协作全景</p><h2>{architectureLabels[board.architecture] ?? "等待路由"}</h2><p className="board-stage">{architectureStages[board.architecture] ?? "入口角色正在理解任务"}</p></div><span className={cursor === null && connected ? "live-indicator" : "muted"}>{cursor !== null ? "历史回放" : connected ? "实时更新" : "等待重连"}</span></header>
    {runs.length > 0 && <div className="board-run-controls"><select aria-label="选择任务轮次" value={selectedRun} onChange={(event) => setSelectedRun(event.target.value)}><option value="">最新任务</option>{runs.map((id, index) => <option key={id} value={id}>任务 {index + 1} · {id.slice(-8)}</option>)}</select><button type="button" className="ghost-button" onClick={() => { setCursor(null); setPlaying(false); }}><Radio size={14} />实时</button></div>}
    <div className={`agent-flow-canvas mode-${board.architecture || "pending"}`}>{flowNodes.length ? <ReactFlow nodes={flowNodes} edges={flowEdges} nodeTypes={nodeTypes} onInit={setFlowInstance} onNodeClick={onNodeClick} fitView fitViewOptions={{ padding: 0.25 }} minZoom={0.35} maxZoom={1.8} nodesDraggable={false} nodesConnectable={false} elementsSelectable attributionPosition="bottom-left"><Background gap={22} size={1} /><MiniMap pannable zoomable nodeColor={(node) => { const data = node.data as AgentNodeData; return data.step.state === "completed" ? "#31836c" : data.step.state === "running" ? "#176b78" : "#8793a1"; }} /><Controls showInteractive={false} /></ReactFlow> : <div className="flow-empty"><Bot size={28} /><p>{runEvents.length ? "正在生成协作拓扑" : "下达任务后，成员与交接路径会在这里出现"}</p></div>}</div>
    {selectedStep && <section className="agent-inspector"><header><div><p className="eyebrow">Agent 详情</p><h3>{roleTitles.get(selectedStep.agentId) ?? selectedStep.agentName}</h3></div><button className="board-icon-button" type="button" onClick={() => setSelectedStepId("")}><X size={16} /></button></header><div className="board-detail-facts"><span><b>步骤</b>#{selectedStep.sequence} {selectedStep.title}</span><span><b>状态</b>{stateLabels[selectedStep.state]}</span><span><b>模型</b>{selectedStep.model || "等待绑定"}</span><span><b>耗时</b>{durationLabel(selectedStep.durationMs)}</span>{selectedStep.started && <span><b>开始</b><time dateTime={selectedStep.started}>{formatDateTime(selectedStep.started)}</time></span>}{selectedStep.ended && <span><b>结束</b><time dateTime={selectedStep.ended}>{formatDateTime(selectedStep.ended)}</time></span>}</div>{selectedStep.error && <p className="board-state-note state-failed"><AlertTriangle size={15} />{selectedStep.error}</p>}<details><summary>处理过程与阶段产出</summary><pre>{selectedStep.output || "尚无阶段产出"}</pre></details>{relatedHandoffs.map((handoff) => <details key={handoff.id}><summary>@{roleTitles.get(handoff.toAgentId) ?? handoff.toAgentId} 交接详情</summary><pre>{handoff.output || handoff.summary}</pre><small>{handoff.createdAt && <><time dateTime={handoff.createdAt}>{formatDateTime(handoff.createdAt)}</time> · </>}来源步骤 #{handoff.sourceSequence} · {handoff.packet?.compressed ? "已压缩" : "未触发压缩"} · 传递约 {String(handoff.packet?.delivered_tokens ?? "-")} tokens{handoff.acceptedAt && <> · 已领取 <time dateTime={handoff.acceptedAt}>{formatDateTime(handoff.acceptedAt)}</time></>}</small></details>)}{memoryEvent && <details><summary>本轮读取记忆</summary><pre>{String(memoryEvent.payload.summary ?? "未读取历史记忆")}</pre><small>引用 {Array.isArray(memoryEvent.payload.message_refs) ? memoryEvent.payload.message_refs.length : 0} 条消息 · {memoryEvent.payload.compressed ? "已压缩" : "未触发压缩"}</small></details>}</section>}
    {runEvents.length > 0 && <div className="board-playback"><button type="button" className="ghost-button" aria-label="上一个事件" onClick={() => seek(count - 1)} disabled={count === 0}><StepBack size={15} /></button><button type="button" className="ghost-button" aria-label={playing ? "暂停回放" : "播放回放"} onClick={() => { if (playing) setPlaying(false); else { if (cursor === null || count === runEvents.length) setCursor(0); setPlaying(true); } }}>{playing ? <Pause size={15} /> : <Play size={15} />}</button><input aria-label="回放进度" type="range" min="0" max={runEvents.length} value={count} onChange={(event) => seek(Number(event.target.value))} /><button type="button" className="ghost-button" aria-label="下一个事件" onClick={() => seek(count + 1)} disabled={count === runEvents.length}><StepForward size={15} /></button><span>{count}/{runEvents.length}</span></div>}
    <p className="board-caption"><Clock size={12} />{runStateLabels[board.runState] ?? (runEvents.length ? "准备拓扑" : "等待任务")}</p>
  </article>;
}
