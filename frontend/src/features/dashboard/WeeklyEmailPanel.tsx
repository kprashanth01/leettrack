import { useState } from "react";

import { sendWeeklySummaryEmail } from "../../api/emails";

type WeeklyEmailPanelProps = {
  disabled: boolean;
};

function WeeklyEmailPanel({ disabled }: WeeklyEmailPanelProps) {
  const [isSending, setIsSending] = useState(false);
  const [statusMessage, setStatusMessage] = useState("");
  const [errorMessage, setErrorMessage] = useState("");

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
          Email yourself a snapshot of solved volume, active days, topic
          coverage, difficulty mix, recent solves, and recent notes.
        </p>
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
