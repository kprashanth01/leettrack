import { useMemo, useState } from "react";

import type { SyncedSubmission } from "../../types/dashboard";

type RecentProblemsTableProps = {
  submissions: SyncedSubmission[];
};

type SortOrder = "newest" | "oldest";

const formatSubmittedAt = (value: string) =>
  new Intl.DateTimeFormat(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));

const getSubmittedAtTime = (submission: SyncedSubmission) =>
  new Date(submission.submittedAt).getTime();

function RecentProblemsTable({ submissions }: RecentProblemsTableProps) {
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedLanguage, setSelectedLanguage] = useState("all");
  const [sortOrder, setSortOrder] = useState<SortOrder>("newest");

  const languageOptions = useMemo(
    () =>
      Array.from(new Set(submissions.map((submission) => submission.language)))
        .filter(Boolean)
        .sort((first, second) => first.localeCompare(second)),
    [submissions],
  );

  const filteredSubmissions = useMemo(() => {
    const normalizedQuery = searchQuery.trim().toLowerCase();

    return submissions
      .filter((submission) => {
        const matchesSearch =
          normalizedQuery.length === 0 ||
          submission.title.toLowerCase().includes(normalizedQuery) ||
          submission.slug.toLowerCase().includes(normalizedQuery);
        const matchesLanguage =
          selectedLanguage === "all" || submission.language === selectedLanguage;

        return matchesSearch && matchesLanguage;
      })
      .sort((first, second) => {
        const firstTime = getSubmittedAtTime(first);
        const secondTime = getSubmittedAtTime(second);

        return sortOrder === "newest"
          ? secondTime - firstTime
          : firstTime - secondTime;
      });
  }, [searchQuery, selectedLanguage, sortOrder, submissions]);

  const hasActiveControls =
    searchQuery.trim().length > 0 || selectedLanguage !== "all";
  const hasSubmissions = submissions.length > 0;

  return (
    <section className="dashboard-section" aria-labelledby="recent-problems-heading">
      <div className="section-heading">
        <div>
          <p className="section-kicker">Problem log</p>
          <h2 id="recent-problems-heading">Synced submissions</h2>
        </div>
        <span className="section-meta">
          {filteredSubmissions.length} of {submissions.length} entries
        </span>
      </div>

      <div className="table-controls" aria-label="Submission table controls">
        <label className="table-search" htmlFor="submission-search">
          <span>Search</span>
          <input
            id="submission-search"
            type="search"
            value={searchQuery}
            onChange={(event) => setSearchQuery(event.target.value)}
            placeholder="Search problems or slugs"
            disabled={!hasSubmissions}
          />
        </label>

        <label className="table-control" htmlFor="submission-language">
          <span>Language</span>
          <select
            id="submission-language"
            value={selectedLanguage}
            onChange={(event) => setSelectedLanguage(event.target.value)}
            disabled={!hasSubmissions}
          >
            <option value="all">All languages</option>
            {languageOptions.map((language) => (
              <option key={language} value={language}>
                {language}
              </option>
            ))}
          </select>
        </label>

        <label className="table-control" htmlFor="submission-sort">
          <span>Sort</span>
          <select
            id="submission-sort"
            value={sortOrder}
            onChange={(event) => setSortOrder(event.target.value as SortOrder)}
            disabled={!hasSubmissions}
          >
            <option value="newest">Newest first</option>
            <option value="oldest">Oldest first</option>
          </select>
        </label>
      </div>

      <div className="table-card">
        {filteredSubmissions.length > 0 ? (
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
              {filteredSubmissions.map((submission) => (
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
        ) : hasActiveControls ? (
          <div className="empty-state">
            <strong>No submissions match these controls.</strong>
            <p>
              Try a different search term or switch the language filter back to
              all languages.
            </p>
          </div>
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
