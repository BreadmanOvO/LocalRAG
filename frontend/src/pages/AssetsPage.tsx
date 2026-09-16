import { useRef, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { CheckCircle2, FileArchive, LoaderCircle, RotateCcw, Search, Trash2, UploadCloud } from "lucide-react";
import { api, type AssetIngestion } from "../shared/api/client";
import { stableSpaceId } from "../shared/space";

const stages = ["queued", "parsing", "cleaning", "chunking", "indexing", "publishing", "completed"];
const labels: Record<string, string> = { queued: "排队", parsing: "解析", cleaning: "清洗", chunking: "分块", indexing: "建立索引", publishing: "登记来源", completed: "已入库" };
const accepted = ".pdf,.docx,.md,.txt,.csv,.tsv,.xlsx,.json,.png,.jpg,.jpeg,.webp";

function FileProgress({ job, retry, remove, retrying, removing }: { job: AssetIngestion; retry: () => void; remove: () => void; retrying: boolean; removing: boolean }) {
  const active = stages.indexOf(job.stage);
  return <article className="asset-progress-card">
    <div className="asset-file-summary">
      {job.status === "completed" ? <CheckCircle2 size={20} /> : job.status === "running" ? <LoaderCircle size={20} className="spin" /> : <FileArchive size={20} />}
      <div><strong>{job.filename}</strong><span>{Math.max(1, Math.ceil(job.size_bytes / 1024))} KB · {job.status === "failed" ? `${labels[job.stage] ?? job.stage}失败` : labels[job.stage]}{job.chunk_count > 0 && ` · ${job.chunk_count} 个分块`}</span></div>
      {job.status === "failed" && <button className="ghost-button" onClick={retry} disabled={retrying}><RotateCcw size={15} />重新处理</button>}
      {job.status === "completed" && <button className="ghost-button danger-button" onClick={remove} disabled={removing}><Trash2 size={15} />删除</button>}
    </div>
    <ol className="asset-progress-track" aria-label={`${job.filename}入库进度`}>
      {stages.map((stage, index) => <li key={stage} className={job.status === "completed" || index < active ? "done" : index === active ? job.status === "failed" ? "failed" : "active" : ""} aria-current={index === active ? "step" : undefined}>{labels[stage]}</li>)}
    </ol>
    {job.error && <p className="error-text" role="alert">{job.error}</p>}
    {job.evaluation_status === "not_configured" && <p className="muted">未执行额外质量评测：当前未配置评测器。</p>}
    <details className="asset-history"><summary>处理记录</summary><ul>{job.history.map((item, index) => <li key={`${item.at}-${index}`}><time>{new Date(item.at).toLocaleString()}</time> {labels[item.stage] ?? item.stage}</li>)}</ul>{job.source_id && <p>来源：{job.source_id}</p>}</details>
  </article>;
}

export function AssetsPage() {
  const input = useRef<HTMLInputElement>(null);
  const busy = useRef(false);
  const [spaceId] = useState(stableSpaceId);
  const [uploading, setUploading] = useState("");
  const [uploadErrors, setUploadErrors] = useState<string[]>([]);
  const [query, setQuery] = useState("");
  const cache = useQueryClient();
  const jobsKey = ["asset-ingestions", spaceId];
  const jobs = useQuery({ queryKey: jobsKey, queryFn: () => api.assetIngestions(spaceId), refetchInterval: (data) => data.state.data?.items.some((job) => job.status === "queued" || job.status === "running") ? 1500 : 10000 });
  const retry = useMutation({ mutationFn: api.retryIngestion, onSuccess: () => cache.invalidateQueries({ queryKey: jobsKey }) });
  const remove = useMutation({ mutationFn: api.deleteIngestion, onSuccess: () => cache.invalidateQueries({ queryKey: jobsKey }) });
  const search = useMutation({ mutationFn: (text: string) => api.searchAssets(spaceId, text) });
  const choose = async (files: FileList | null) => {
    if (!files?.length || busy.current) return;
    busy.current = true;
    setUploadErrors([]);
    try {
      for (const file of Array.from(files)) {
        setUploading(file.name);
        try {
          await api.uploadAsset(spaceId, file);
          await cache.invalidateQueries({ queryKey: jobsKey });
        } catch (error) {
          setUploadErrors((current) => [...current, `${file.name}：${error instanceof Error ? error.message : "上传失败，请重试"}`]);
        }
      }
    } finally {
      setUploading("");
      busy.current = false;
      if (input.current) input.current.value = "";
    }
  };
  return <section className="page assets-page">
    <header className="product-page-header"><span className="section-icon"><FileArchive size={18} /></span><div><p className="eyebrow">知识库</p><h1>资料资产</h1><p className="subtitle">添加资料，随时检索原文与出处。</p></div></header>
    <section className="asset-upload-card">
      <input ref={input} hidden type="file" multiple accept={accepted} onChange={(event) => void choose(event.target.files)} />
      <button type="button" className="asset-dropzone" onClick={() => input.current?.click()} onDragOver={(event) => event.preventDefault()} onDrop={(event) => { event.preventDefault(); void choose(event.dataTransfer.files); }} disabled={!!uploading}>
        {uploading ? <LoaderCircle size={30} className="spin" /> : <UploadCloud size={30} />}
        <strong>{uploading ? `正在上传 ${uploading}` : "选择文件或拖拽到这里"}</strong><span>可同时选择多个文件，上传后自动入库 · 每个文件最多 30 MB</span>
      </button>
      <p className="asset-format-hint">PDF、DOCX、Markdown、TXT、CSV、TSV、XLSX、JSON、PNG、JPG、WebP。图片与扫描页需要启用支持图片的模型。</p>
      {uploadErrors.map((error, index) => <p className="error-text" role="alert" key={index}>{error}</p>)}
    </section>
    <section className="asset-search-card"><h2>检索资料</h2><form onSubmit={(event) => { event.preventDefault(); if (query.trim()) search.mutate(query.trim()); }}><input aria-label="检索资料" value={query} onChange={(event) => setQuery(event.target.value)} placeholder="输入关键词或问题" maxLength={2000} /><button className="primary-button" disabled={!query.trim() || search.isPending}><Search size={16} />{search.isPending ? "检索中" : "检索"}</button></form>
      {search.isError && <p className="error-text" role="alert">{search.error.message}</p>}
      {search.data && <div className="asset-search-results">{search.data.items.length === 0 ? <p className="muted">暂无可检索内容，请先完成资料入库。</p> : search.data.items.map((hit, index) => <article key={index}><strong>{String(hit.metadata.source ?? "资料")} · {String(hit.metadata.locator ?? "正文")}</strong><p>{hit.text}</p></article>)}</div>}
    </section>
    <div className="asset-list-heading"><h2>入库记录</h2><span className="muted">{jobs.data?.items.length ?? 0} 个文件</span></div>
    {jobs.isError && <p className="error-text" role="alert">记录加载失败：{jobs.error.message}</p>}
    {retry.isError && <p className="error-text" role="alert">{retry.error.message}</p>}
    {jobs.isPending && <p className="muted">正在加载…</p>}
    {jobs.data?.items.length === 0 && <p className="asset-empty">还没有资料。上传第一份文件，建立你的知识库。</p>}
    {remove.isError && <p className="error-text" role="alert">删除失败：{remove.error.message}</p>}
    <div className="asset-job-list">{jobs.data?.items.filter((job) => job.status !== "deleted").map((job) => <FileProgress key={job.job_id} job={job} retry={() => retry.mutate(job.job_id)} remove={() => { if (window.confirm(`确定删除“${job.filename}”及其入库内容吗？`)) remove.mutate(job.job_id); }} retrying={retry.isPending} removing={remove.isPending} />)}</div>
  </section>;
}
