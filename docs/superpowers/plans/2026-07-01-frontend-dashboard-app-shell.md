# Frontend Dashboard App Shell Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the foundation placeholder with a responsive LeetTrack dashboard app shell powered by typed mock data.

**Architecture:** This milestone changes only `frontend/`. The implementation separates generic shell components from dashboard-specific feature components, and keeps mock data outside React components so later API integration has a clean replacement point.

**Tech Stack:** React, Vite, TypeScript, CSS, mock data modules.

---

## Issue

GitHub Issue: `#3`  
URL: `https://github.com/kprashanth01/leettrack/issues/3`

## Branch

Create and work on:

```bash
git switch main
git pull origin main
git switch -c feature/frontend-app-shell
```

## File Structure

Create or modify these files:

- Create: `frontend/src/types/dashboard.ts`
- Create: `frontend/src/data/mockDashboardData.ts`
- Create: `frontend/src/components/AppShell.tsx`
- Create: `frontend/src/components/Sidebar.tsx`
- Create: `frontend/src/components/StatCard.tsx`
- Create: `frontend/src/features/dashboard/DashboardPage.tsx`
- Create: `frontend/src/features/dashboard/RecentProblemsTable.tsx`
- Create: `frontend/src/features/dashboard/RevisionPreview.tsx`
- Modify: `frontend/src/App.tsx`
- Modify: `frontend/src/styles.css`

No backend files should change in this milestone.

---

### Task 1: Create Branch And Verify Baseline

**Files:**
- No file changes.

- [ ] **Step 1: Start from updated `main`**

Run:

```bash
git switch main
git pull origin main
```

Expected: local `main` is up to date with `origin/main`.

- [ ] **Step 2: Create the feature branch**

Run:

```bash
git switch -c feature/frontend-app-shell
```

Expected: Git switches to `feature/frontend-app-shell`.

- [ ] **Step 3: Verify the existing frontend build**

Run:

```bash
cd frontend
npm run build
```

Expected: TypeScript and Vite build succeed before any feature changes.

---

### Task 2: Add Dashboard Types And Mock Data

**Files:**
- Create: `frontend/src/types/dashboard.ts`
- Create: `frontend/src/data/mockDashboardData.ts`

- [ ] **Step 1: Add dashboard data types**

Create `frontend/src/types/dashboard.ts`:

```ts
export type Difficulty = "Easy" | "Medium" | "Hard";

export type ProblemStatus = "Solved" | "Needs Review" | "Revised";

export type DashboardStat = {
  label: string;
  value: string;
  helper: string;
};

export type SolvedProblem = {
  id: string;
  title: string;
  difficulty: Difficulty;
  tags: string[];
  status: ProblemStatus;
  solvedAt: string;
};

export type RevisionItem = {
  id: string;
  title: string;
  dueLabel: string;
  note: string;
};
```

- [ ] **Step 2: Add typed mock dashboard data**

Create `frontend/src/data/mockDashboardData.ts`:

```ts
import type {
  DashboardStat,
  RevisionItem,
  SolvedProblem,
} from "../types/dashboard";

export const dashboardStats: DashboardStat[] = [
  {
    label: "Total solved",
    value: "128",
    helper: "Across 18 topic areas",
  },
  {
    label: "Solved this week",
    value: "7",
    helper: "3 more than last week",
  },
  {
    label: "Current streak",
    value: "9 days",
    helper: "Keep the rhythm steady",
  },
  {
    label: "Revisions due",
    value: "12",
    helper: "Prioritize weak patterns",
  },
];

export const recentProblems: SolvedProblem[] = [
  {
    id: "two-sum",
    title: "Two Sum",
    difficulty: "Easy",
    tags: ["Array", "Hash Map"],
    status: "Revised",
    solvedAt: "Today",
  },
  {
    id: "coin-change",
    title: "Coin Change",
    difficulty: "Medium",
    tags: ["Dynamic Programming", "BFS"],
    status: "Needs Review",
    solvedAt: "Yesterday",
  },
  {
    id: "binary-tree-level-order-traversal",
    title: "Binary Tree Level Order Traversal",
    difficulty: "Medium",
    tags: ["Tree", "Queue"],
    status: "Solved",
    solvedAt: "2 days ago",
  },
  {
    id: "minimum-window-substring",
    title: "Minimum Window Substring",
    difficulty: "Hard",
    tags: ["Sliding Window", "Hash Map"],
    status: "Needs Review",
    solvedAt: "4 days ago",
  },
];

export const revisionItems: RevisionItem[] = [
  {
    id: "coin-change-review",
    title: "Coin Change",
    dueLabel: "Due today",
    note: "Revisit the transition: dp[amount] = min(dp[amount], dp[amount - coin] + 1).",
  },
  {
    id: "minimum-window-review",
    title: "Minimum Window Substring",
    dueLabel: "Due tomorrow",
    note: "Practice explaining why the left pointer only moves after all required chars are covered.",
  },
  {
    id: "tree-bfs-review",
    title: "Binary Tree Level Order Traversal",
    dueLabel: "Due this week",
    note: "Compare queue-based BFS with recursive DFS by depth.",
  },
];
```

- [ ] **Step 3: Verify TypeScript can parse the new modules**

Run:

```bash
cd frontend
npm run build
```

Expected: build succeeds with the new unused data modules present.

---

### Task 3: Add Reusable Shell Components

**Files:**
- Create: `frontend/src/components/AppShell.tsx`
- Create: `frontend/src/components/Sidebar.tsx`
- Create: `frontend/src/components/StatCard.tsx`

- [ ] **Step 1: Add app shell component**

Create `frontend/src/components/AppShell.tsx`:

```tsx
import type { ReactNode } from "react";

import Sidebar from "./Sidebar";

type AppShellProps = {
  children: ReactNode;
};

function AppShell({ children }: AppShellProps) {
  return (
    <div className="app-layout">
      <Sidebar />
      <main className="app-main">{children}</main>
    </div>
  );
}

export default AppShell;
```

- [ ] **Step 2: Add sidebar component**

Create `frontend/src/components/Sidebar.tsx`:

```tsx
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
    </aside>
  );
}

export default Sidebar;
```

- [ ] **Step 3: Add stat card component**

Create `frontend/src/components/StatCard.tsx`:

```tsx
import type { DashboardStat } from "../types/dashboard";

type StatCardProps = {
  stat: DashboardStat;
};

function StatCard({ stat }: StatCardProps) {
  return (
    <article className="stat-card">
      <p className="stat-label">{stat.label}</p>
      <strong className="stat-value">{stat.value}</strong>
      <p className="stat-helper">{stat.helper}</p>
    </article>
  );
}

export default StatCard;
```

- [ ] **Step 4: Verify reusable components compile**

Run:

```bash
cd frontend
npm run build
```

Expected: build succeeds with the new components present.

---

### Task 4: Add Dashboard Feature Components

**Files:**
- Create: `frontend/src/features/dashboard/DashboardPage.tsx`
- Create: `frontend/src/features/dashboard/RecentProblemsTable.tsx`
- Create: `frontend/src/features/dashboard/RevisionPreview.tsx`

- [ ] **Step 1: Add recent problems table**

Create `frontend/src/features/dashboard/RecentProblemsTable.tsx`:

```tsx
import type { Difficulty, ProblemStatus, SolvedProblem } from "../../types/dashboard";

type RecentProblemsTableProps = {
  problems: SolvedProblem[];
};

const difficultyClassName: Record<Difficulty, string> = {
  Easy: "badge badge-easy",
  Medium: "badge badge-medium",
  Hard: "badge badge-hard",
};

const statusClassName: Record<ProblemStatus, string> = {
  Solved: "status status-solved",
  "Needs Review": "status status-review",
  Revised: "status status-revised",
};

function RecentProblemsTable({ problems }: RecentProblemsTableProps) {
  return (
    <section className="dashboard-section" aria-labelledby="recent-problems-heading">
      <div className="section-heading">
        <div>
          <p className="section-kicker">Problem log</p>
          <h2 id="recent-problems-heading">Recent solved problems</h2>
        </div>
        <span className="section-meta">{problems.length} entries</span>
      </div>

      <div className="table-card">
        <table>
          <thead>
            <tr>
              <th scope="col">Problem</th>
              <th scope="col">Difficulty</th>
              <th scope="col">Tags</th>
              <th scope="col">Status</th>
              <th scope="col">Solved</th>
            </tr>
          </thead>
          <tbody>
            {problems.map((problem) => (
              <tr key={problem.id}>
                <td data-label="Problem">
                  <strong>{problem.title}</strong>
                </td>
                <td data-label="Difficulty">
                  <span className={difficultyClassName[problem.difficulty]}>
                    {problem.difficulty}
                  </span>
                </td>
                <td data-label="Tags">
                  <div className="tag-list">
                    {problem.tags.map((tag) => (
                      <span className="tag" key={tag}>
                        {tag}
                      </span>
                    ))}
                  </div>
                </td>
                <td data-label="Status">
                  <span className={statusClassName[problem.status]}>
                    {problem.status}
                  </span>
                </td>
                <td data-label="Solved">{problem.solvedAt}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

export default RecentProblemsTable;
```

- [ ] **Step 2: Add revision preview**

Create `frontend/src/features/dashboard/RevisionPreview.tsx`:

```tsx
import type { RevisionItem } from "../../types/dashboard";

type RevisionPreviewProps = {
  items: RevisionItem[];
};

function RevisionPreview({ items }: RevisionPreviewProps) {
  return (
    <section className="dashboard-section" aria-labelledby="revision-preview-heading">
      <div className="section-heading">
        <div>
          <p className="section-kicker">Revision queue</p>
          <h2 id="revision-preview-heading">Notes to revisit</h2>
        </div>
      </div>

      <div className="revision-list">
        {items.map((item) => (
          <article className="revision-item" key={item.id}>
            <div>
              <h3>{item.title}</h3>
              <p>{item.note}</p>
            </div>
            <span>{item.dueLabel}</span>
          </article>
        ))}
      </div>
    </section>
  );
}

export default RevisionPreview;
```

- [ ] **Step 3: Add dashboard page composition**

Create `frontend/src/features/dashboard/DashboardPage.tsx`:

```tsx
import StatCard from "../../components/StatCard";
import {
  dashboardStats,
  recentProblems,
  revisionItems,
} from "../../data/mockDashboardData";

import RecentProblemsTable from "./RecentProblemsTable";
import RevisionPreview from "./RevisionPreview";

function DashboardPage() {
  return (
    <div className="dashboard" id="dashboard">
      <header className="dashboard-header">
        <div>
          <p className="page-kicker">Dashboard</p>
          <h1>Track your LeetCode progress with intent.</h1>
          <p>
            Review recent solves, spot revision work, and keep your daily
            practice loop visible.
          </p>
        </div>

        <aside className="focus-card" aria-label="Today focus">
          <p>Today&apos;s focus</p>
          <strong>Revise dynamic programming transitions</strong>
          <span>Mock recommendation based on recent practice.</span>
        </aside>
      </header>

      <section className="stats-grid" aria-label="Progress summary">
        {dashboardStats.map((stat) => (
          <StatCard key={stat.label} stat={stat} />
        ))}
      </section>

      <div className="dashboard-grid">
        <RecentProblemsTable problems={recentProblems} />
        <RevisionPreview items={revisionItems} />
      </div>
    </div>
  );
}

export default DashboardPage;
```

- [ ] **Step 4: Verify dashboard feature components compile**

Run:

```bash
cd frontend
npm run build
```

Expected: build succeeds with the feature components present.

---

### Task 5: Compose Dashboard In App And Replace Styles

**Files:**
- Modify: `frontend/src/App.tsx`
- Modify: `frontend/src/styles.css`

- [ ] **Step 1: Replace the placeholder app composition**

Update `frontend/src/App.tsx`:

```tsx
import AppShell from "./components/AppShell";
import DashboardPage from "./features/dashboard/DashboardPage";

function App() {
  return (
    <AppShell>
      <DashboardPage />
    </AppShell>
  );
}

export default App;
```

- [ ] **Step 2: Replace foundation styles with dashboard styles**

Update `frontend/src/styles.css`:

```css
:root {
  color: #172033;
  background: #eef2f7;
  font-family:
    Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI",
    sans-serif;
  font-synthesis: none;
  text-rendering: optimizeLegibility;
}

* {
  box-sizing: border-box;
}

body {
  margin: 0;
  min-width: 320px;
  min-height: 100vh;
}

a {
  color: inherit;
  text-decoration: none;
}

button,
input,
textarea,
select {
  font: inherit;
}

.app-layout {
  display: grid;
  grid-template-columns: 260px minmax(0, 1fr);
  min-height: 100vh;
}

.sidebar {
  position: sticky;
  top: 0;
  display: flex;
  flex-direction: column;
  gap: 32px;
  height: 100vh;
  border-right: 1px solid #d6deea;
  background: #ffffff;
  padding: 28px 20px;
}

.brand {
  display: flex;
  align-items: center;
  gap: 12px;
}

.brand-mark {
  display: inline-grid;
  width: 42px;
  height: 42px;
  place-items: center;
  border-radius: 8px;
  background: #172033;
  color: #ffffff;
  font-size: 0.9rem;
  font-weight: 800;
}

.brand-name,
.brand-caption,
.page-kicker,
.section-kicker,
.stat-label,
.stat-helper,
.focus-card p,
.focus-card span {
  margin: 0;
}

.brand-name {
  color: #111827;
  font-size: 1rem;
  font-weight: 800;
}

.brand-caption {
  color: #6b778c;
  font-size: 0.78rem;
}

.nav-list {
  display: grid;
  gap: 8px;
}

.nav-link {
  border-radius: 8px;
  color: #506078;
  font-size: 0.95rem;
  font-weight: 700;
  padding: 12px;
}

.nav-link:hover,
.nav-link[aria-current="page"] {
  background: #edf4ff;
  color: #1d4ed8;
}

.app-main {
  min-width: 0;
  padding: 36px;
}

.dashboard {
  display: grid;
  gap: 24px;
  max-width: 1180px;
  margin: 0 auto;
}

.dashboard-header {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(260px, 340px);
  gap: 24px;
  align-items: stretch;
}

.page-kicker,
.section-kicker {
  color: #2563eb;
  font-size: 0.78rem;
  font-weight: 800;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

h1,
h2,
h3,
p {
  margin-top: 0;
}

h1 {
  max-width: 760px;
  margin-bottom: 14px;
  color: #0f172a;
  font-size: clamp(2.1rem, 5vw, 4rem);
  line-height: 1.02;
}

.dashboard-header > div > p:last-child {
  max-width: 660px;
  margin-bottom: 0;
  color: #506078;
  font-size: 1.05rem;
  line-height: 1.7;
}

.focus-card,
.stat-card,
.dashboard-section {
  border: 1px solid #d8e0ec;
  border-radius: 8px;
  background: #ffffff;
  box-shadow: 0 16px 40px rgb(15 23 42 / 0.05);
}

.focus-card {
  display: grid;
  align-content: center;
  gap: 10px;
  padding: 22px;
}

.focus-card p,
.focus-card span {
  color: #66758d;
  font-size: 0.88rem;
}

.focus-card strong {
  color: #111827;
  font-size: 1.2rem;
  line-height: 1.35;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 16px;
}

.stat-card {
  display: grid;
  gap: 8px;
  min-height: 136px;
  padding: 20px;
}

.stat-label {
  color: #64748b;
  font-size: 0.85rem;
  font-weight: 800;
}

.stat-value {
  color: #0f172a;
  font-size: 2rem;
  line-height: 1;
}

.stat-helper {
  color: #64748b;
  font-size: 0.9rem;
  line-height: 1.5;
}

.dashboard-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.5fr) minmax(300px, 0.8fr);
  gap: 18px;
  align-items: start;
}

.dashboard-section {
  min-width: 0;
  overflow: hidden;
}

.section-heading {
  display: flex;
  align-items: start;
  justify-content: space-between;
  gap: 16px;
  border-bottom: 1px solid #e4eaf3;
  padding: 20px;
}

.section-heading h2 {
  margin: 4px 0 0;
  color: #111827;
  font-size: 1.2rem;
}

.section-meta {
  border-radius: 999px;
  background: #eef4ff;
  color: #1d4ed8;
  font-size: 0.78rem;
  font-weight: 800;
  padding: 6px 10px;
  white-space: nowrap;
}

.table-card {
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th,
td {
  border-bottom: 1px solid #edf1f7;
  padding: 16px 20px;
  text-align: left;
  vertical-align: top;
}

th {
  color: #66758d;
  font-size: 0.78rem;
  font-weight: 800;
  text-transform: uppercase;
}

td {
  color: #344258;
  font-size: 0.92rem;
}

td strong {
  color: #111827;
}

.badge,
.status,
.tag {
  display: inline-flex;
  align-items: center;
  border-radius: 999px;
  font-size: 0.78rem;
  font-weight: 800;
  line-height: 1;
  padding: 7px 9px;
  white-space: nowrap;
}

.badge-easy {
  background: #e8f7ef;
  color: #047857;
}

.badge-medium {
  background: #fff4dc;
  color: #b45309;
}

.badge-hard {
  background: #feecef;
  color: #be123c;
}

.status-solved,
.status-revised {
  background: #edf4ff;
  color: #1d4ed8;
}

.status-review {
  background: #fff4dc;
  color: #92400e;
}

.tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.tag {
  background: #f1f5f9;
  color: #475569;
  font-weight: 700;
}

.revision-list {
  display: grid;
  gap: 0;
}

.revision-item {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 16px;
  border-bottom: 1px solid #edf1f7;
  padding: 18px 20px;
}

.revision-item:last-child,
tbody tr:last-child td {
  border-bottom: 0;
}

.revision-item h3 {
  margin-bottom: 8px;
  color: #111827;
  font-size: 1rem;
}

.revision-item p {
  margin-bottom: 0;
  color: #5c6b82;
  font-size: 0.92rem;
  line-height: 1.55;
}

.revision-item span {
  color: #1d4ed8;
  font-size: 0.82rem;
  font-weight: 800;
  white-space: nowrap;
}

@media (max-width: 960px) {
  .app-layout {
    grid-template-columns: 1fr;
  }

  .sidebar {
    position: static;
    height: auto;
    gap: 18px;
  }

  .nav-list {
    grid-template-columns: repeat(4, minmax(0, 1fr));
  }

  .nav-link {
    text-align: center;
  }

  .app-main {
    padding: 24px;
  }

  .dashboard-header,
  .dashboard-grid {
    grid-template-columns: 1fr;
  }

  .stats-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 640px) {
  .sidebar {
    padding: 20px 16px;
  }

  .nav-list {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .app-main {
    padding: 20px 16px 32px;
  }

  .dashboard {
    gap: 18px;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .section-heading,
  .revision-item {
    grid-template-columns: 1fr;
  }

  .table-card {
    overflow-x: visible;
  }

  table,
  thead,
  tbody,
  tr,
  th,
  td {
    display: block;
  }

  thead {
    display: none;
  }

  tr {
    border-bottom: 1px solid #edf1f7;
    padding: 14px 20px;
  }

  td {
    display: grid;
    grid-template-columns: 96px minmax(0, 1fr);
    gap: 12px;
    border-bottom: 0;
    padding: 8px 0;
  }

  td::before {
    color: #66758d;
    content: attr(data-label);
    font-size: 0.76rem;
    font-weight: 800;
    text-transform: uppercase;
  }

  .revision-item span {
    white-space: normal;
  }
}
```

- [ ] **Step 3: Verify the full frontend build**

Run:

```bash
cd frontend
npm run build
```

Expected: build succeeds after replacing the app and CSS.

---

### Task 6: Manual Browser Verification

**Files:**
- Review: `frontend/src/App.tsx`
- Review: `frontend/src/styles.css`
- Review: `frontend/src/data/mockDashboardData.ts`

- [ ] **Step 1: Start the frontend dev server**

Run:

```bash
cd frontend
npm run dev
```

Expected: Vite prints a local URL, usually `http://localhost:5173`.

- [ ] **Step 2: Verify desktop layout**

Open the dev server URL.

Expected:

- sidebar is visible on the left;
- dashboard header and focus card are visible;
- four stat cards appear;
- recent problems table appears;
- revision preview appears;
- no backend server is required.

- [ ] **Step 3: Verify mobile layout**

Use browser responsive mode or a narrow browser width around `390px`.

Expected:

- sidebar becomes a top area;
- navigation wraps cleanly;
- stat cards stack;
- problem rows become label/value blocks;
- no horizontal page overflow.

- [ ] **Step 4: Confirm mock data boundaries**

Inspect these files:

```text
frontend/src/data/mockDashboardData.ts
frontend/src/features/dashboard/DashboardPage.tsx
frontend/src/features/dashboard/RecentProblemsTable.tsx
frontend/src/features/dashboard/RevisionPreview.tsx
```

Expected:

- mock arrays live in `mockDashboardData.ts`;
- presentational components receive data through props;
- no backend URLs, Axios calls, TanStack Query, or React Router imports exist.

- [ ] **Step 5: Check Git diff scope**

Run:

```bash
git status --short
git diff --stat
```

Expected: only frontend source files and this plan file are changed. No backend files are changed.

---

### Task 7: Commit The Implementation

**Files:**
- Stage all files created or modified by this milestone.

- [ ] **Step 1: Run final verification**

Run:

```bash
cd frontend
npm run build
```

Expected: build succeeds.

- [ ] **Step 2: Stage implementation files**

Run:

```bash
git add frontend/src docs/superpowers/plans/2026-07-01-frontend-dashboard-app-shell.md
```

Expected: dashboard implementation files and the implementation plan are staged.

- [ ] **Step 3: Commit implementation**

Run:

```bash
git commit -m "feat(frontend): build dashboard app shell"
```

Expected: one implementation commit on `feature/frontend-app-shell`.

---

## Manual Testing Steps

- Run `npm run build` inside `frontend/`.
- Run `npm run dev` inside `frontend/`.
- Open the app on desktop and verify dashboard shell content renders.
- Resize to mobile width and verify there is no horizontal page overflow.
- Confirm the backend server is not needed for the frontend dashboard to render.

## Edge Cases

- Long title: `Binary Tree Level Order Traversal` should wrap without breaking layout.
- Multiple tags should wrap inside the tag list.
- Navigation labels should wrap into two columns on small screens.
- Revision notes should wrap inside their cards without overflow.

## Future Improvements

- Add local problem logging UI with temporary client state.
- Introduce TailwindCSS and shadcn/ui in a dedicated styling-system milestone.
- Add React Router when there is more than one real route.
- Add Axios and TanStack Query when real backend calls begin.

## Plan Self-Review

- Spec coverage: Tasks cover sidebar shell, stat cards, recent problems, revision preview, typed mock data, responsive CSS, and build/browser verification.
- Placeholder scan: No unfinished implementation placeholders remain.
- Type consistency: `Difficulty`, `ProblemStatus`, `DashboardStat`, `SolvedProblem`, and `RevisionItem` are used consistently across mock data and components.
- Scope check: Backend, auth, database, routing, API calls, charts, and AI recommendations remain out of scope.
