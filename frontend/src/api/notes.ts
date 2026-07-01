import { getCurrentAccessToken } from "../lib/supabase";
import type { ProblemNote } from "../types/dashboard";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL?.replace(/\/$/, "") ??
  "http://127.0.0.1:8000";

type ApiProblemNote = {
  id: number;
  problem_title: string;
  problem_slug: string;
  difficulty: string | null;
  topic_tags: string[];
  content: string;
  created_at: string;
  updated_at: string;
};

type NotesResponse = {
  notes: ApiProblemNote[];
};

const mapNote = (note: ApiProblemNote): ProblemNote => ({
  id: note.id,
  problemTitle: note.problem_title,
  problemSlug: note.problem_slug,
  difficulty: note.difficulty,
  topicTags: note.topic_tags,
  content: note.content,
  createdAt: note.created_at,
  updatedAt: note.updated_at,
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

export async function fetchProblemNotes(): Promise<ProblemNote[]> {
  const response = await fetch(`${API_BASE_URL}/notes`, {
    headers: await getAuthHeaders(),
  });

  if (!response.ok) {
    throw new Error(await readErrorMessage(response));
  }

  const body = (await response.json()) as NotesResponse;
  return body.notes.map(mapNote);
}

export async function createProblemNote(
  problemSlug: string,
  content: string,
): Promise<ProblemNote> {
  const response = await fetch(`${API_BASE_URL}/notes`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...(await getAuthHeaders()),
    },
    body: JSON.stringify({ problem_slug: problemSlug, content }),
  });

  if (!response.ok) {
    throw new Error(await readErrorMessage(response));
  }

  return mapNote((await response.json()) as ApiProblemNote);
}

export async function updateProblemNote(
  noteId: number,
  content: string,
): Promise<ProblemNote> {
  const response = await fetch(`${API_BASE_URL}/notes/${noteId}`, {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json",
      ...(await getAuthHeaders()),
    },
    body: JSON.stringify({ content }),
  });

  if (!response.ok) {
    throw new Error(await readErrorMessage(response));
  }

  return mapNote((await response.json()) as ApiProblemNote);
}

export async function deleteProblemNote(noteId: number): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/notes/${noteId}`, {
    method: "DELETE",
    headers: await getAuthHeaders(),
  });

  if (!response.ok) {
    throw new Error(await readErrorMessage(response));
  }
}
