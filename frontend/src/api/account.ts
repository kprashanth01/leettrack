import { getCurrentAccessToken } from "../lib/supabase";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL?.replace(/\/$/, "") ??
  "http://127.0.0.1:8000";

type AccountSettingsApiResponse = {
  leetcode_username: string | null;
  email: string | null;
};

export type AccountSettings = {
  leetcodeUsername: string | null;
  email: string | null;
};

const readErrorMessage = async (response: Response) => {
  try {
    const body = (await response.json()) as { detail?: unknown };
    if (typeof body.detail === "string") {
      return body.detail;
    }
  } catch {
    // Fall back to a generic message below.
  }

  return "LeetTrack could not load account settings.";
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

export async function fetchAccountSettings(): Promise<AccountSettings> {
  const response = await fetch(`${API_BASE_URL}/account/settings`, {
    headers: await getAuthHeaders(),
  });

  if (!response.ok) {
    throw new Error(await readErrorMessage(response));
  }

  const body = (await response.json()) as AccountSettingsApiResponse;
  return {
    leetcodeUsername: body.leetcode_username,
    email: body.email,
  };
}
