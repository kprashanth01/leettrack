import { useEffect, useState } from "react";

import {
  fetchEmailPreferences,
  sendWeeklySummaryEmail,
  updateEmailPreferences,
  type EmailPreferences,
} from "../../api/emails";

type WeeklyEmailPanelProps = {
  disabled: boolean;
};

function WeeklyEmailPanel({ disabled }: WeeklyEmailPanelProps) {
  const [preferences, setPreferences] = useState<EmailPreferences | null>(null);
  const [isLoadingPreferences, setIsLoadingPreferences] = useState(true);
  const [isSavingPreferences, setIsSavingPreferences] = useState(false);
  const [isSending, setIsSending] = useState(false);
  const [statusMessage, setStatusMessage] = useState("");
  const [errorMessage, setErrorMessage] = useState("");

  useEffect(() => {
    let isMounted = true;

    const loadPreferences = async () => {
      setIsLoadingPreferences(true);
      setErrorMessage("");

      try {
        const loadedPreferences = await fetchEmailPreferences();
        if (isMounted) {
          setPreferences(loadedPreferences);
        }
      } catch (error) {
        if (isMounted) {
          setErrorMessage(
            error instanceof Error
              ? error.message
              : "Could not load email preferences.",
          );
        }
      } finally {
        if (isMounted) {
          setIsLoadingPreferences(false);
        }
      }
    };

    void loadPreferences();

    return () => {
      isMounted = false;
    };
  }, []);

  const handlePreferenceChange = async () => {
    if (!preferences || isSavingPreferences) {
      return;
    }

    const nextValue = !preferences.weeklySummaryEnabled;
    setIsSavingPreferences(true);
    setStatusMessage("");
    setErrorMessage("");

    try {
      const updatedPreferences = await updateEmailPreferences(nextValue);
      setPreferences(updatedPreferences);
      setStatusMessage(
        updatedPreferences.weeklySummaryEnabled
          ? "Weekly summaries enabled for future scheduled emails."
          : "Weekly summaries disabled for future scheduled emails.",
      );
    } catch (error) {
      setErrorMessage(
        error instanceof Error
          ? error.message
          : "Could not update email preferences.",
      );
    } finally {
      setIsSavingPreferences(false);
    }
  };

  const handleSendSummary = async () => {
    setIsSending(true);
    setStatusMessage("");
    setErrorMessage("");

    try {
      const result = await sendWeeklySummaryEmail();
      setStatusMessage(`Weekly summary sent to ${result.recipient}.`);
    } catch (error) {
      setErrorMessage(
        error instanceof Error ? error.message : "Could not send weekly summary.",
      );
    } finally {
      setIsSending(false);
    }
  };

  return (
    <section className="dashboard-section" aria-labelledby="weekly-email-heading">
      <div className="section-heading">
        <div>
          <p className="section-kicker">Email summary</p>
          <h2 id="weekly-email-heading">Send weekly progress report</h2>
        </div>
      </div>

      <div className="email-summary-panel">
        <p className="email-summary-copy">
          Email yourself a polished snapshot of solved volume, active days,
          streaks, difficulty mix, topic coverage, recent solves, notes, and a
          recommended focus area.
        </p>
        <div className="email-preference-card">
          <div>
            <p className="email-preference-label">Weekly automation preference</p>
            <strong>
              {preferences?.weeklySummaryEnabled
                ? "Scheduled summaries are on"
                : "Scheduled summaries are off"}
            </strong>
            <span>
              {isLoadingPreferences
                ? "Loading your email preference..."
                : `Recipient: ${preferences?.recipient ?? "your account email"}`}
            </span>
          </div>
          <button
            aria-pressed={preferences?.weeklySummaryEnabled ?? false}
            className="email-toggle"
            disabled={!preferences || isLoadingPreferences || isSavingPreferences}
            onClick={handlePreferenceChange}
            type="button"
          >
            <span />
            {isSavingPreferences
              ? "Saving"
              : preferences?.weeklySummaryEnabled
                ? "On"
                : "Off"}
          </button>
        </div>

        <button
          className="primary-action"
          disabled={disabled || isSending}
          onClick={handleSendSummary}
          type="button"
        >
          {isSending ? "Sending..." : "Send weekly summary"}
        </button>

        {statusMessage ? (
          <p className="form-success" role="status">
            {statusMessage}
          </p>
        ) : null}

        {errorMessage ? (
          <p className="form-error" role="alert">
            {errorMessage}
          </p>
        ) : null}
      </div>
    </section>
  );
}

export default WeeklyEmailPanel;
