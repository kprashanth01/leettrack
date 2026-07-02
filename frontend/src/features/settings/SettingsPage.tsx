import LeetCodeSyncPanel from "../dashboard/LeetCodeSyncPanel";
import WeeklyEmailPanel from "../dashboard/WeeklyEmailPanel";
import { useWorkspaceData } from "../workspace/WorkspaceDataContext";

function SettingsPage() {
  const {
    errorMessage,
    isLoading,
    loadSubmissions,
    statusMessage,
    submissions,
    syncSubmissions,
    username,
  } = useWorkspaceData();

  return (
    <div className="workspace-page settings-page">
      <header className="page-header">
        <div>
          <p className="page-kicker">Settings</p>
          <h1>Control how LeetTrack stays fresh.</h1>
          <p>
            Manage your LeetCode connection, trigger manual syncs, and configure
            weekly progress emails from one account workspace.
          </p>
        </div>

        <aside className="focus-card" aria-label="Account automation status">
          <p>Account automation</p>
          <strong>{username || "No username saved"}</strong>
          <span>
            {submissions.length > 0
              ? `${submissions.length} solved submissions are available for reports.`
              : "Sync submissions before enabling useful weekly summaries."}
          </span>
        </aside>
      </header>

      <div className="settings-grid">
        <LeetCodeSyncPanel
          initialUsername={username}
          isLoading={isLoading}
          statusMessage={statusMessage}
          errorMessage={errorMessage}
          onLoadSubmissions={loadSubmissions}
          onSyncSubmissions={syncSubmissions}
        />

        <WeeklyEmailPanel disabled={submissions.length === 0} />
      </div>
    </div>
  );
}

export default SettingsPage;
