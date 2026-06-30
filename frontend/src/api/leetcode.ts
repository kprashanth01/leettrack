import type { SyncedSubmission } from "../types/dashboard";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL?.replace(/\/$/, "") ??
  "http://127.0.0.1:8000";

type ApiSubmission = {
  title: string;
  slug: string;
  language: string;
  submitted_at: string;
  source: "leetcode";
};

type SyncResponse = {
  status: "completed";
  username: string;
  fetched_count: number;
  saved_count: number;
  submissions: ApiSubmission[];
};

type SubmissionsResponse = {
  username: string;
  submissions: ApiSubmission[];
};

export type SyncResult = {
  username: string;
  fetchedCount: number;
  savedCount: number;
  submissions: SyncedSubmission[];
};

const mapSubmission = (submission: ApiSubmission): SyncedSubmission => ({
  title: submission.title,
  slug: submission.slug,
  language: submission.language,
  submittedAt: submission.submitted_at,
  source: submission.source,
});

const readErrorMessage = async (response: Response) => {
  try {
    const body = (await response.json()) as { detail?: unknown };
    if (typeof body.detail === "string") {
      return body.detail;
    }
  } catch {
    // Fall back to a generic message below.
  }

  return "LeetTrack could not complete the request.";
};

export async function syncLeetCodeSubmissions(
  username: string,
  limit = 20,
): Promise<SyncResult> {
  const response = await fetch(`${API_BASE_URL}/leetcode/sync`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, limit }),
  });

  if (!response.ok) {
    throw new Error(await readErrorMessage(response));
  }

  const body = (await response.json()) as SyncResponse;
  return {
    username: body.username,
    fetchedCount: body.fetched_count,
    savedCount: body.saved_count,
    submissions: body.submissions.map(mapSubmission),
  };
}

export async function fetchLeetCodeSubmissions(
  username: string,
): Promise<SyncedSubmission[]> {
  const params = new URLSearchParams({ username });
  const response = await fetch(`${API_BASE_URL}/leetcode/submissions?${params}`);

  if (!response.ok) {
    throw new Error(await readErrorMessage(response));
  }

  const body = (await response.json()) as SubmissionsResponse;
  return body.submissions.map(mapSubmission);
}
