import { useEffect, useMemo, useState } from "react";

import StatCard from "../../components/StatCard";
import {
  fetchLeetCodeSubmissions,
  syncLeetCodeSubmissions,
} from "../../api/leetcode";
import type { DashboardStat, SyncedSubmission } from "../../types/dashboard";

import LeetCodeSyncPanel from "./LeetCodeSyncPanel";
import RecentProblemsTable from "./RecentProblemsTable";

const STORED_USERNAME_KEY = "leettrack.leetcodeUsername";

const formatLatestSubmission = (submissions: SyncedSubmission[]) => {
  if (submissions.length === 0) {
    return "No submissions";
  }

  return new Intl.DateTimeFormat(undefined, { dateStyle: "medium" }).format(
    new Date(submissions[0].submittedAt),
  );
};

const getLanguageCount = (submissions: SyncedSubmission[]) =>
  new Set(submissions.map((submission) => submission.language)).size;

function DashboardPage() {
  const [username, setUsername] = useState(
    () => window.localStorage.getItem(STORED_USERNAME_KEY) ?? "",
  );
  const [submissions, setSubmissions] = useState<SyncedSubmission[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [statusMessage, setStatusMessage] = useState("");
  const [errorMessage, setErrorMessage] = useState("");

  const dashboardStats: DashboardStat[] = useMemo(
    () => [
      {
        label: "Total synced",
        value: submissions.length.toString(),
        helper: "Persisted accepted submissions",
      },
      {
        label: "Languages",
        value: getLanguageCount(submissions).toString(),
        helper: "Based on saved submissions",
      },
      {
        label: "Latest submission",
        value: formatLatestSubmission(submissions),
        helper: "Newest persisted LeetCode solve",
      },
      {
        label: "Tracked account",
        value: username || "Not set",
        helper: "Loaded from real backend data",
      },
    ],
    [submissions, username],
  );

  const loadSubmissions = async (nextUsername: string) => {
    const normalizedUsername = nextUsername.trim();
    if (!normalizedUsername) {
      setErrorMessage("Enter a LeetCode username.");
      setStatusMessage("");
      return;
    }

    setIsLoading(true);
    setErrorMessage("");
    setStatusMessage("");

    try {
      const savedSubmissions = await fetchLeetCodeSubmissions(normalizedUsername);
      setUsername(normalizedUsername);
      setSubmissions(savedSubmissions);
      window.localStorage.setItem(STORED_USERNAME_KEY, normalizedUsername);
      setStatusMessage(`Loaded ${savedSubmissions.length} saved submissions.`);
    } catch (error) {
      setErrorMessage(
        error instanceof Error ? error.message : "Could not load submissions.",
      );
    } finally {
      setIsLoading(false);
    }
  };

  const syncSubmissions = async (nextUsername: string) => {
    const normalizedUsername = nextUsername.trim();
    if (!normalizedUsername) {
      setErrorMessage("Enter a LeetCode username.");
      setStatusMessage("");
      return;
    }

    setIsLoading(true);
    setErrorMessage("");
    setStatusMessage("");

    try {
      const result = await syncLeetCodeSubmissions(normalizedUsername);
      const savedSubmissions = await fetchLeetCodeSubmissions(normalizedUsername);
      setUsername(result.username);
      setSubmissions(savedSubmissions);
      window.localStorage.setItem(STORED_USERNAME_KEY, result.username);
      setStatusMessage(
        `Fetched ${result.fetchedCount}; saved ${result.savedCount} new submissions.`,
      );
    } catch (error) {
      setErrorMessage(
        error instanceof Error ? error.message : "Could not sync submissions.",
      );
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (username) {
      void loadSubmissions(username);
    }
  }, []);

  return (
    <div className="dashboard" id="dashboard">
      <header className="dashboard-header">
        <div>
          <p className="page-kicker">Dashboard</p>
          <h1>Track your LeetCode progress with intent.</h1>
          <p>
            Sync accepted submissions from LeetCode, persist them in Supabase,
            and review your real practice history.
          </p>
        </div>

        <aside className="focus-card" aria-label="Sync status">
          <p>Data source</p>
          <strong>LeetCode + Supabase</strong>
          <span>
            {username
              ? `Showing persisted submissions for ${username}.`
              : "Enter a username to load persisted submissions."}
          </span>
        </aside>
      </header>

      <section className="stats-grid" aria-label="Progress summary">
        {dashboardStats.map((stat) => (
          <StatCard key={stat.label} stat={stat} />
        ))}
      </section>

      <LeetCodeSyncPanel
        initialUsername={username}
        isLoading={isLoading}
        statusMessage={statusMessage}
        errorMessage={errorMessage}
        onLoadSubmissions={loadSubmissions}
        onSyncSubmissions={syncSubmissions}
      />

      <RecentProblemsTable submissions={submissions} />
    </div>
  );
}

export default DashboardPage;
