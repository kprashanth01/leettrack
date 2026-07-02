import { lazy, Suspense } from "react";

import { useWorkspaceData } from "../workspace/WorkspaceDataContext";

import RecentProblemsTable from "./RecentProblemsTable";

const AnalyticsDashboard = lazy(() => import("../analytics/AnalyticsDashboard"));

function DashboardPage() {
  const { submissions } = useWorkspaceData();

  return (
    <div className="dashboard" id="dashboard">
      <header className="dashboard-header">
        <div>
          <p className="page-kicker">Dashboard</p>
          <h1>Build your LeetCode streak with intent.</h1>
          <p>
            Track consistency, volume, difficulty mix, languages, and topic
            coverage from your real synced submissions.
          </p>
        </div>

        <aside className="focus-card" aria-label="Sync status">
          <p>Practice snapshot</p>
          <strong>{submissions.length} solved records</strong>
          <span>
            Analytics are generated from your saved LeetCode submissions.
          </span>
        </aside>
      </header>

      <Suspense
        fallback={
          <section className="analytics-dashboard" aria-label="Loading analytics">
            <div className="analytics-loading-card">Loading progress analytics...</div>
          </section>
        }
      >
        <AnalyticsDashboard submissions={submissions} />
      </Suspense>

      <RecentProblemsTable submissions={submissions} />
    </div>
  );
}

export default DashboardPage;
