import { NavLink } from "react-router-dom";

import AuthPanel from "./AuthPanel";

const navigationItems = [
  { label: "Dashboard", path: "/dashboard" },
  { label: "Problems", path: "/problems" },
  { label: "Notes", path: "/notes" },
  { label: "Review", path: "/review" },
  { label: "Settings", path: "/settings" },
];

function Sidebar() {
  return (
    <aside className="sidebar" aria-label="Primary navigation">
      <div className="brand">
        <span className="brand-mark" aria-hidden="true">
          LT
        </span>
        <div>
          <p className="brand-name">LeetTrack</p>
          <p className="brand-caption">CP progress tracker</p>
        </div>
      </div>

      <nav className="nav-list" aria-label="Main sections">
        {navigationItems.map((item) => (
          <NavLink
            className={({ isActive }) =>
              isActive ? "nav-link nav-link-active" : "nav-link"
            }
            key={item.path}
            to={item.path}
          >
            {item.label}
          </NavLink>
        ))}
      </nav>

      <AuthPanel />
    </aside>
  );
}

export default Sidebar;
