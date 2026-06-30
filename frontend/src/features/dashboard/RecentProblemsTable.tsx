import type { SyncedSubmission } from "../../types/dashboard";

type RecentProblemsTableProps = {
  submissions: SyncedSubmission[];
};

const formatSubmittedAt = (value: string) =>
  new Intl.DateTimeFormat(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));

function RecentProblemsTable({ submissions }: RecentProblemsTableProps) {
  return (
    <section className="dashboard-section" aria-labelledby="recent-problems-heading">
      <div className="section-heading">
        <div>
          <p className="section-kicker">Problem log</p>
          <h2 id="recent-problems-heading">Synced submissions</h2>
        </div>
        <span className="section-meta">{submissions.length} entries</span>
      </div>

      <div className="table-card">
        {submissions.length > 0 ? (
          <table>
            <thead>
              <tr>
                <th scope="col">Problem</th>
                <th scope="col">Language</th>
                <th scope="col">Source</th>
                <th scope="col">Submitted</th>
              </tr>
            </thead>
            <tbody>
              {submissions.map((submission) => (
                <tr key={`${submission.slug}-${submission.submittedAt}`}>
                  <td data-label="Problem">
                    <strong>{submission.title}</strong>
                    <p className="problem-note">{submission.slug}</p>
                  </td>
                  <td data-label="Language">
                    <span className="tag">{submission.language}</span>
                  </td>
                  <td data-label="Source">
                    <span className="status status-solved">
                      {submission.source}
                    </span>
                  </td>
                  <td data-label="Submitted">
                    {formatSubmittedAt(submission.submittedAt)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <div className="empty-state">
            <strong>No synced submissions yet.</strong>
            <p>Enter your LeetCode username, then load saved data or run sync.</p>
          </div>
        )}
      </div>
    </section>
  );
}

export default RecentProblemsTable;
