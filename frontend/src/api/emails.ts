import { getCurrentAccessToken } from "../lib/supabase";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL?.replace(/\/$/, "") ??
  "http://127.0.0.1:8000";

type WeeklySummaryEmailResponse = {
  status: "sent";
  email_id: string;
  recipient: string;
};

export type WeeklySummaryEmailResult = {
  status: "sent";
  emailId: string;
  recipient: string;
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

export async function sendWeeklySummaryEmail(): Promise<WeeklySummaryEmailResult> {
  const response = await fetch(`${API_BASE_URL}/emails/weekly-summary`, {
    method: "POST",
    headers: await getAuthHeaders(),
  });

  if (!response.ok) {
    throw new Error(await readErrorMessage(response));
  }

  const body = (await response.json()) as WeeklySummaryEmailResponse;
  return {
    status: body.status,
    emailId: body.email_id,
    recipient: body.recipient,
  };
}
