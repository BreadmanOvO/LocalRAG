import { useQuery } from "@tanstack/react-query";
import { api } from "../shared/api/client";

export function CompanyPage() {
  const roles = useQuery({ queryKey: ["roles"], queryFn: api.roles });
  return <section className="page"><header className="page-header"><div><p className="eyebrow">公司设置</p><h1>角色与人设</h1><p className="subtitle">角色定义职责和能力，人设只影响表达；运行绑定会冻结版本。</p></div></header><div className="role-grid">{roles.isLoading && <p className="muted">加载角色…</p>}{roles.isError && <p className="error-text">角色读取失败</p>}{roles.data?.items.map((role) => <article className="panel role-card" key={role.role_id}><p className="eyebrow">{role.department}</p><h2>{role.name}</h2><p className="muted">职责：{role.responsibilities.join("、")}</p><p className="muted">能力：{role.capabilities.join(" · ")}</p></article>)}</div></section>;
}
