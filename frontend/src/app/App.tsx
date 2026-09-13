import { NavLink, Outlet, useLocation, useNavigate } from "react-router-dom";
import { Building2, Crown, FolderArchive, Landmark, PlusSquare, Settings2, Stamp } from "lucide-react";
import { RoomList } from "../features/rooms/RoomList";
import { roomTheme, themes, useTheme, type ThemeId } from "./theme";

function ThemeChoice() {
  const { setTheme } = useTheme();
  const choices: Array<{ id: ThemeId; title: string; description: string }> = [
    { id: "company", title: "公司", description: "以董事长办公室和正式部门协作处理任务" },
    { id: "emperor", title: "当皇上", description: "以御前、内阁与六部的称谓组织同一套能力" },
  ];
  return <main className="theme-choice" aria-labelledby="theme-choice-title">
    <div className="theme-choice-intro">
      <span className="product-kicker">BeTheBoss</span>
      <h1 id="theme-choice-title">选择你的管理方式</h1>
      <p>两种主题使用相同的任务、协作和追溯能力；你可以稍后在设置中切换。</p>
    </div>
    <div className="theme-choice-grid">
      {choices.map((choice) => {
        const Icon = choice.id === "company" ? Building2 : Crown;
        return <button className={`theme-choice-card ${choice.id}`} key={choice.id} type="button" onClick={() => setTheme(choice.id)}>
          <span className="theme-choice-icon"><Icon aria-hidden="true" size={28} /></span>
          <span className="theme-choice-copy"><strong>{choice.title}</strong><small>{choice.description}</small></span>
          <span className="theme-choice-action">进入</span>
        </button>;
      })}
    </div>
  </main>;
}

export function App() {
  const navigate = useNavigate();
  const location = useLocation();
  const { theme, definition } = useTheme();
  if (!theme || !definition) return <ThemeChoice />;
  const roomId = location.pathname.match(/^\/rooms\/([^/]+)/)?.[1];
  const activeTheme = roomId ? roomTheme(roomId) ?? "company" : theme;
  const activeDefinition = themes[activeTheme];
  const BrandIcon = activeTheme === "company" ? Landmark : Stamp;
  return (
    <div className="app-shell" data-theme={activeTheme}>
      <aside className="sidebar">
        <button className="brand" onClick={() => navigate("/workspace")} aria-label="回到新任务" title="回到新任务">
          <span className="brand-mark"><BrandIcon aria-hidden="true" size={18} /></span>
          <span>BeTheBoss</span>
        </button>
        <nav className="nav-list" aria-label="主导航">
          <NavLink className={({ isActive }) => (isActive ? "nav-item active" : "nav-item")} to="/workspace"><PlusSquare aria-hidden="true" size={17} />新任务</NavLink>
          <NavLink className={({ isActive }) => (isActive ? "nav-item active" : "nav-item")} to="/assets"><FolderArchive aria-hidden="true" size={17} />资料资产</NavLink>
        </nav>
        <RoomList />
        <div className="sidebar-bottom">
          <NavLink className={({ isActive }) => (isActive ? "nav-item settings-link active" : "nav-item settings-link")} to="/company"><Settings2 aria-hidden="true" size={17} />{activeDefinition.setupLabel}</NavLink>
          <span className="theme-status"><BrandIcon aria-hidden="true" size={14} />{activeDefinition.name}主题</span>
        </div>
      </aside>
      <main className="main-content"><Outlet /></main>
    </div>
  );
}
