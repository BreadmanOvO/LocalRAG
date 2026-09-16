import type { Member } from "../../shared/api/client";
import { roomTheme, themes } from "../../app/theme";

export function MemberCard({ members, roomId }: { members: Member[]; roomId: string }) {
  const definition = themes[roomTheme(roomId) ?? "company"];
  return <div className="member-card"><div className="panel-heading"><h2>协作成员</h2><span className="muted">{members.length}</span></div>{members.length ? members.map((member) => {
    const name = definition.roles.find((role) => role.id === member.agent_id)?.title ?? member.agent_id;
    return <div className="member-row" key={member.membership_id}><span className="member-avatar">{name.slice(0, 1)}</span><span><b>{name}</b><small>{member.status}</small></span></div>;
  }) : <p className="empty-state">尚无成员加入。</p>}</div>;
}
