import { getCurrentAccessToken } from "../lib/supabase";
import type { TrackedProblem } from "../types/dashboard";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL?.replace(/\/$/, "") ??
  "http://127.0.0.1:8000";

type ApiTrackedProblem = {
  id: number;
  problem_title: string;
  problem_slug: string;
  difficulty: string | null;
  topic_tags: string[];
  source: "extension";
  created_at: string;
};

type TrackedProblemsResponse = {
  problems: ApiTrackedProblem[];
};

type SaveTrackedProblemResponse = {
  is_new: boolean;
  problem: ApiTrackedProblem;
};

export type SaveTrackedProblemResult = {
  isNew: boolean;
  problem: TrackedProblem;
};

const mapTrackedProblem = (problem: ApiTrackedProblem): TrackedProblem => ({
  id: problem.id,
  problemTitle: problem.problem_title,
  problemSlug: problem.problem_slug,
  difficulty: problem.difficulty,
  topicTags: problem.topic_tags,
  source: problem.source,
  createdAt: problem.created_at,
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

const getAuthHeaders = async (): Promise<Record<string, string>> => {
  const token = await getCurrentAccessToken();

  if (!token) {
    return {};
  }

  return {
    Authorization: `Bearer ${token}`,
  };
};

export async function fetchTrackedProblems(): Promise<TrackedProblem[]> {
  const response = await fetch(`${API_BASE_URL}/problems/tracked`, {
    headers: await getAuthHeaders(),
  });

  if (!response.ok) {
    throw new Error(await readErrorMessage(response));
  }

  const body = (await response.json()) as TrackedProblemsResponse;
  return body.problems.map(mapTrackedProblem);
}

export async function saveTrackedProblemFromExtension(
  problemSlug: string,
  problemTitle: string,
): Promise<SaveTrackedProblemResult> {
  const response = await fetch(`${API_BASE_URL}/problems/tracked`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...(await getAuthHeaders()),
    },
    body: JSON.stringify({
      problem_slug: problemSlug,
      problem_title: problemTitle,
      source: "extension",
    }),
  });

  if (!response.ok) {
    throw new Error(await readErrorMessage(response));
  }

  const body = (await response.json()) as SaveTrackedProblemResponse;
  return {
    isNew: body.is_new,
    problem: mapTrackedProblem(body.problem),
  };
}
