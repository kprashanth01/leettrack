import AuthPanel from "./AuthPanel";

const navigationItems = ["Dashboard", "Problems", "Notes", "Review"];

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
          <a
            aria-current={item === "Dashboard" ? "page" : undefined}
            className="nav-link"
            href="#dashboard"
            key={item}
          >
            {item}
          </a>
        ))}
      </nav>

      <AuthPanel />
    </aside>
  );
}

export default Sidebar;
