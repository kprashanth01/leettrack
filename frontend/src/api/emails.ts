import { getCurrentAccessToken } from "../lib/supabase";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL?.replace(/\/$/, "") ??
  "http://127.0.0.1:8000";

type WeeklySummaryEmailResponse = {
  status: "sent";
  email_id: string;
  recipient: string;
};

type EmailPreferencesResponse = {
  weekly_summary_enabled: boolean;
  recipient: string;
};

export type WeeklySummaryEmailResult = {
  status: "sent";
  emailId: string;
  recipient: string;
};

export type EmailPreferences = {
  weeklySummaryEnabled: boolean;
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

export async function fetchEmailPreferences(): Promise<EmailPreferences> {
  const response = await fetch(`${API_BASE_URL}/emails/preferences`, {
    headers: await getAuthHeaders(),
  });

  if (!response.ok) {
    throw new Error(await readErrorMessage(response));
  }

  const body = (await response.json()) as EmailPreferencesResponse;
  return {
    weeklySummaryEnabled: body.weekly_summary_enabled,
    recipient: body.recipient,
  };
}

export async function updateEmailPreferences(
  weeklySummaryEnabled: boolean,
): Promise<EmailPreferences> {
  const response = await fetch(`${API_BASE_URL}/emails/preferences`, {
    method: "PATCH",
    headers: {
      ...(await getAuthHeaders()),
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      weekly_summary_enabled: weeklySummaryEnabled,
    }),
  });

  if (!response.ok) {
    throw new Error(await readErrorMessage(response));
  }

  const body = (await response.json()) as EmailPreferencesResponse;
  return {
    weeklySummaryEnabled: body.weekly_summary_enabled,
    recipient: body.recipient,
  };
}
