import { useWorkspaceData } from "../workspace/WorkspaceDataContext";

function ReviewPage() {
  const { submissions } = useWorkspaceData();
  const problemCount = new Set(submissions.map((submission) => submission.slug)).size;

  return (
    <div className="workspace-page">
      <header className="page-header">
        <div>
          <p className="page-kicker">Review</p>
          <h1>Revision scheduling comes next.</h1>
          <p>
            Review should be generated from solved problems, notes, and mistake
            patterns instead of a separate manual checklist.
          </p>
        </div>
      </header>

      <section className="dashboard-section">
        <div className="empty-state empty-state-large">
          <strong>No revision queue yet.</strong>
          <p>
            LeetTrack has {problemCount} synced problems to schedule from. The
            next revision feature can use difficulty, tags, and solve dates to
            create smarter review reminders.
          </p>
          <div className="empty-state-actions" aria-label="Planned review workflow">
            <span>Prioritize stale topics</span>
            <span>Use notes as context</span>
            <span>Schedule reminders</span>
          </div>
        </div>
      </section>
    </div>
  );
}

export default ReviewPage;
