import { useMemo } from "react";

import type { SyncedSubmission } from "../../types/dashboard";
import { useWorkspaceData } from "../workspace/WorkspaceDataContext";

const formatSubmittedAt = (value: string) =>
  new Intl.DateTimeFormat(undefined, { dateStyle: "medium" }).format(
    new Date(value),
  );

const getProblemUrl = (slug: string) => `https://leetcode.com/problems/${slug}/`;

const getLatestProblems = (submissions: SyncedSubmission[]) => {
  const latestBySlug = new Map<string, SyncedSubmission>();

  for (const submission of submissions) {
    const existing = latestBySlug.get(submission.slug);
    if (
      !existing ||
      new Date(submission.submittedAt).getTime() >
        new Date(existing.submittedAt).getTime()
    ) {
      latestBySlug.set(submission.slug, submission);
    }
  }

  return Array.from(latestBySlug.values()).sort(
    (first, second) =>
      new Date(second.submittedAt).getTime() -
      new Date(first.submittedAt).getTime(),
  );
};

function ProblemsPage() {
  const { submissions, username } = useWorkspaceData();
  const problems = useMemo(() => getLatestProblems(submissions), [submissions]);

  return (
    <div className="workspace-page">
      <header className="page-header">
        <div>
          <p className="page-kicker">Problems</p>
          <h1>Solved problem library.</h1>
          <p>
            Review unique synced problems from your LeetCode account with
            metadata that will later power notes, revision, and analytics.
          </p>
        </div>
        <aside className="focus-card" aria-label="Problem summary">
          <p>Problem source</p>
          <strong>{username || "No account loaded"}</strong>
          <span>{problems.length} unique synced problems</span>
        </aside>
      </header>

      <section className="dashboard-section" aria-labelledby="problems-heading">
        <div className="section-heading">
          <div>
            <p className="section-kicker">Library</p>
            <h2 id="problems-heading">Synced problems</h2>
          </div>
          <span className="section-meta">{problems.length} problems</span>
        </div>

        {problems.length > 0 ? (
          <div className="problem-grid">
            {problems.map((problem) => (
              <article className="problem-card" key={problem.slug}>
                <div>
                  <a
                    className="problem-link"
                    href={getProblemUrl(problem.slug)}
                    rel="noreferrer"
                    target="_blank"
                  >
                    {problem.title}
                  </a>
                  <p className="problem-note">{problem.slug}</p>
                </div>

                <div className="problem-card-meta">
                  {problem.difficulty ? (
                    <span
                      className={`badge badge-${problem.difficulty.toLowerCase()}`}
                    >
                      {problem.difficulty}
                    </span>
                  ) : (
                    <span className="tag">Unknown difficulty</span>
                  )}
                  <span className="tag">{problem.language}</span>
                </div>

                {problem.topicTags.length > 0 ? (
                  <div className="tag-list">
                    {problem.topicTags.map((tag) => (
                      <span className="tag" key={tag}>
                        {tag}
                      </span>
                    ))}
                  </div>
                ) : (
                  <p className="problem-note">No topic tags saved yet.</p>
                )}

                <p className="problem-note">
                  Last solved {formatSubmittedAt(problem.submittedAt)}
                </p>
              </article>
            ))}
          </div>
        ) : (
          <div className="empty-state">
            <strong>No synced problems yet.</strong>
            <p>
              Go to Dashboard, enter your LeetCode username, and sync accepted
              submissions to build your problem library.
            </p>
          </div>
        )}
      </section>
    </div>
  );
}

export default ProblemsPage;
