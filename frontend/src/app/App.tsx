import { NavLink, Outlet, useNavigate } from "react-router-dom";

export function App() {
  const navigate = useNavigate();
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <button className="brand" onClick={() => navigate("/workspace")} aria-label="回到工作台">
          <span className="brand-mark">L</span>
          <span>LocalRAG</span>
        </button>
        <p className="eyebrow">AGENT WORKSPACE</p>
        <nav className="nav-list" aria-label="主导航">
          <NavLink className={({ isActive }) => (isActive ? "nav-item active" : "nav-item")} to="/workspace">工作台</NavLink>
          <NavLink className={({ isActive }) => (isActive ? "nav-item active" : "nav-item")} to="/assets">资料资产</NavLink>
        </nav>
        <div className="sidebar-footer">
          <span className="status-dot" /> API 合同 v1.8
        </div>
      </aside>
      <main className="main-content"><Outlet /></main>
    </div>
  );
}
