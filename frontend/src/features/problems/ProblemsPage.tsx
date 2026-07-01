import { useMemo, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";

import type { SyncedSubmission, TrackedProblem } from "../../types/dashboard";
import { useWorkspaceData } from "../workspace/WorkspaceDataContext";

const formatSubmittedAt = (value: string) =>
  new Intl.DateTimeFormat(undefined, { dateStyle: "medium" }).format(
    new Date(value),
  );

const getProblemUrl = (slug: string) => `https://leetcode.com/problems/${slug}/`;
const getNoteUrl = (slug: string) => `/notes?problemSlug=${encodeURIComponent(slug)}`;

type LibraryProblem = {
  title: string;
  slug: string;
  difficulty: string | null;
  topicTags: string[];
  sourceLabel: "Solved" | "Saved";
  language?: string;
  submittedAt?: string;
  savedAt?: string;
};

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

const buildLibraryProblems = (
  submissions: SyncedSubmission[],
  trackedProblems: TrackedProblem[],
): LibraryProblem[] => {
  const latestSubmissions = getLatestProblems(submissions);
  const libraryBySlug = new Map<string, LibraryProblem>();

  for (const submission of latestSubmissions) {
    libraryBySlug.set(submission.slug, {
      title: submission.title,
      slug: submission.slug,
      difficulty: submission.difficulty,
      topicTags: submission.topicTags,
      sourceLabel: "Solved",
      language: submission.language,
      submittedAt: submission.submittedAt,
    });
  }

  for (const trackedProblem of trackedProblems) {
    if (libraryBySlug.has(trackedProblem.problemSlug)) {
      continue;
    }

    libraryBySlug.set(trackedProblem.problemSlug, {
      title: trackedProblem.problemTitle,
      slug: trackedProblem.problemSlug,
      difficulty: trackedProblem.difficulty,
      topicTags: trackedProblem.topicTags,
      sourceLabel: "Saved",
      savedAt: trackedProblem.createdAt,
    });
  }

  return Array.from(libraryBySlug.values()).sort((first, second) => {
    const firstTime = new Date(first.submittedAt ?? first.savedAt ?? 0).getTime();
    const secondTime = new Date(second.submittedAt ?? second.savedAt ?? 0).getTime();
    return secondTime - firstTime;
  });
};

function ProblemsPage() {
  const {
    errorMessage,
    isLoading,
    saveTrackedProblem,
    statusMessage,
    submissions,
    trackedProblems,
    username,
  } = useWorkspaceData();
  const [localErrorMessage, setLocalErrorMessage] = useState("");
  const [localStatusMessage, setLocalStatusMessage] = useState("");
  const [searchParams] = useSearchParams();
  const solvedProblems = useMemo(() => getLatestProblems(submissions), [submissions]);
  const problems = useMemo(
    () => buildLibraryProblems(submissions, trackedProblems),
    [submissions, trackedProblems],
  );
  const extensionProblem =
    searchParams.get("source") === "extension"
      ? {
          slug: searchParams.get("problemSlug")?.trim() ?? "",
          title: searchParams.get("problemTitle")?.trim() ?? "",
        }
      : null;
  const detectedProblem = extensionProblem?.slug ? extensionProblem : null;
  const syncedDetectedProblem = detectedProblem
    ? solvedProblems.find((problem) => problem.slug === detectedProblem.slug)
    : undefined;
  const savedDetectedProblem = detectedProblem
    ? trackedProblems.find((problem) => problem.problemSlug === detectedProblem.slug)
    : undefined;
  const isDetectedProblemTracked = Boolean(
    syncedDetectedProblem || savedDetectedProblem,
  );
  const handleSaveDetectedProblem = async () => {
    if (!detectedProblem) {
      return;
    }

    setLocalErrorMessage("");
    setLocalStatusMessage("");

    try {
      const result = await saveTrackedProblem(
        detectedProblem.slug,
        detectedProblem.title || detectedProblem.slug,
      );
      setLocalStatusMessage(
        result.isNew
          ? "Saved this detected problem to your library."
          : "This problem was already saved to your library.",
      );
    } catch (error) {
      setLocalErrorMessage(
        error instanceof Error ? error.message : "Could not save this problem.",
      );
    }
  };

  return (
    <div className="workspace-page">
      <header className="page-header">
        <div>
          <p className="page-kicker">Problems</p>
          <h1>Tracked problem library.</h1>
          <p>
            Review solved LeetCode problems and saved extension picks with
            metadata that will later power notes, revision, and analytics.
          </p>
        </div>
        <aside className="focus-card" aria-label="Problem summary">
          <p>Problem source</p>
          <strong>{username || "No account loaded"}</strong>
          <span>
            {solvedProblems.length} solved, {trackedProblems.length} saved
          </span>
        </aside>
      </header>

      {detectedProblem ? (
        <section
          className="dashboard-section extension-context-panel"
          aria-labelledby="extension-context-heading"
        >
          <div>
            <p className="section-kicker">Detected from extension</p>
            <h2 id="extension-context-heading">
              {syncedDetectedProblem?.title || detectedProblem.title || detectedProblem.slug}
            </h2>
            <p className="problem-note">{detectedProblem.slug}</p>
          </div>

          <div className="extension-context-actions">
            {syncedDetectedProblem ? (
              <span className="status status-solved">Already synced</span>
            ) : savedDetectedProblem ? (
              <span className="status status-solved">Saved to library</span>
            ) : (
              <button
                className="primary-action"
                disabled={isLoading}
                onClick={handleSaveDetectedProblem}
                type="button"
              >
                {isLoading ? "Saving..." : "Save problem"}
              </button>
            )}
            {isDetectedProblemTracked ? (
              <Link
                className="primary-action"
                to={getNoteUrl(detectedProblem.slug)}
              >
                Add note
              </Link>
            ) : null}
            <a
              className="secondary-action"
              href={getProblemUrl(detectedProblem.slug)}
              rel="noreferrer"
              target="_blank"
            >
              Open LeetCode
            </a>
          </div>
          {localStatusMessage ? (
            <p className="form-success extension-context-message" role="status">
              {localStatusMessage}
            </p>
          ) : null}
          {localErrorMessage ? (
            <p className="form-error extension-context-message" role="alert">
              {localErrorMessage}
            </p>
          ) : null}
        </section>
      ) : null}

      <section className="dashboard-section" aria-labelledby="problems-heading">
        <div className="section-heading">
          <div>
            <p className="section-kicker">Library</p>
            <h2 id="problems-heading">Tracked problems</h2>
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
                  {problem.language ? <span className="tag">{problem.language}</span> : null}
                  <span className="tag">{problem.sourceLabel}</span>
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

                <div className="problem-card-footer">
                  <p className="problem-note">
                    {problem.submittedAt
                      ? `Last solved ${formatSubmittedAt(problem.submittedAt)}`
                      : `Saved ${formatSubmittedAt(problem.savedAt ?? "")}`}
                  </p>
                  <Link
                    className="secondary-action"
                    to={getNoteUrl(problem.slug)}
                  >
                    Add note
                  </Link>
                </div>
              </article>
            ))}
          </div>
        ) : (
          <div className="empty-state">
            <strong>No synced problems yet.</strong>
            <p>
              Go to Dashboard and sync accepted submissions, or open a LeetCode
              problem from the extension and save it here.
            </p>
          </div>
        )}
      </section>
    </div>
  );
}

export default ProblemsPage;
