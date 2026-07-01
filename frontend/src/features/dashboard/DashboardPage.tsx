import { lazy, Suspense } from "react";

import { useWorkspaceData } from "../workspace/WorkspaceDataContext";

import LeetCodeSyncPanel from "./LeetCodeSyncPanel";
import RecentProblemsTable from "./RecentProblemsTable";
import WeeklyEmailPanel from "./WeeklyEmailPanel";

const AnalyticsDashboard = lazy(() => import("../analytics/AnalyticsDashboard"));

function DashboardPage() {
  const {
    username,
    submissions,
    isLoading,
    statusMessage,
    errorMessage,
    loadSubmissions,
    syncSubmissions,
  } = useWorkspaceData();

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
          <p>Tracked account</p>
          <strong>{username || "Not set"}</strong>
          <span>
            {username
              ? `${submissions.length} saved submissions loaded.`
              : "Enter a username to load persisted submissions."}
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

      <LeetCodeSyncPanel
        initialUsername={username}
        isLoading={isLoading}
        statusMessage={statusMessage}
        errorMessage={errorMessage}
        onLoadSubmissions={loadSubmissions}
        onSyncSubmissions={syncSubmissions}
      />

      <WeeklyEmailPanel disabled={submissions.length === 0} />

      <RecentProblemsTable submissions={submissions} />
    </div>
  );
}

export default DashboardPage;
