import {
  createContext,
  ReactNode,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";

import {
  fetchLeetCodeSubmissions,
  syncLeetCodeSubmissions,
} from "../../api/leetcode";
import type { SyncedSubmission } from "../../types/dashboard";

const STORED_USERNAME_KEY = "leettrack.leetcodeUsername";

type WorkspaceDataContextValue = {
  username: string;
  submissions: SyncedSubmission[];
  isLoading: boolean;
  statusMessage: string;
  errorMessage: string;
  loadSubmissions: (username: string) => Promise<void>;
  syncSubmissions: (username: string) => Promise<void>;
};

const WorkspaceDataContext = createContext<WorkspaceDataContextValue | null>(
  null,
);

type WorkspaceDataProviderProps = {
  children: ReactNode;
};

export function WorkspaceDataProvider({ children }: WorkspaceDataProviderProps) {
  const [username, setUsername] = useState(
    () => window.localStorage.getItem(STORED_USERNAME_KEY) ?? "",
  );
  const [submissions, setSubmissions] = useState<SyncedSubmission[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [statusMessage, setStatusMessage] = useState("");
  const [errorMessage, setErrorMessage] = useState("");

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

  const value = useMemo<WorkspaceDataContextValue>(
    () => ({
      username,
      submissions,
      isLoading,
      statusMessage,
      errorMessage,
      loadSubmissions,
      syncSubmissions,
    }),
    [errorMessage, isLoading, statusMessage, submissions, username],
  );

  return (
    <WorkspaceDataContext.Provider value={value}>
      {children}
    </WorkspaceDataContext.Provider>
  );
}

export function useWorkspaceData() {
  const value = useContext(WorkspaceDataContext);

  if (!value) {
    throw new Error("useWorkspaceData must be used within WorkspaceDataProvider.");
  }

  return value;
}
