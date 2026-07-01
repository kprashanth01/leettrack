import { useWorkspaceData } from "../workspace/WorkspaceDataContext";

function NotesPage() {
  const { submissions } = useWorkspaceData();
  const problemCount = new Set(submissions.map((submission) => submission.slug)).size;

  return (
    <div className="workspace-page">
      <header className="page-header">
        <div>
          <p className="page-kicker">Notes</p>
          <h1>Problem notes will live here.</h1>
          <p>
            Notes should attach to real synced problems so every observation,
            mistake, and pattern stays connected to your practice history.
          </p>
        </div>
      </header>

      <section className="dashboard-section">
        <div className="empty-state empty-state-large">
          <strong>No notes yet.</strong>
          <p>
            You have {problemCount} synced problems available for future notes.
            The next notes feature will let you write takeaways per problem
            without creating disconnected manual records.
          </p>
        </div>
      </section>
    </div>
  );
}

export default NotesPage;
