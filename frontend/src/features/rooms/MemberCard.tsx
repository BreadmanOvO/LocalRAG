import type { Member } from "../../shared/api/client";

export function MemberCard({ members }: { members: Member[] }) {
  return <div className="member-card"><div className="panel-heading"><h2>协作成员</h2><span className="muted">{members.length || "总助理"}</span></div>{members.length ? members.map((member) => <div className="member-row" key={member.membership_id}><span className="member-avatar">{member.agent_id.slice(0, 1).toUpperCase()}</span><span><b>{member.agent_id}</b><small>{member.status}</small></span></div>) : <p className="empty-state">当前任务由总助理处理，出现协作分工时会显示参与成员。</p>}</div>;
}
