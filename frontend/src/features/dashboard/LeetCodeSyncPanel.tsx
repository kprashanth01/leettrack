import { FormEvent, useState } from "react";

type LeetCodeSyncPanelProps = {
  initialUsername: string;
  isLoading: boolean;
  statusMessage: string;
  errorMessage: string;
  onLoadSubmissions: (username: string) => Promise<void>;
  onSyncSubmissions: (username: string) => Promise<void>;
};

function LeetCodeSyncPanel({
  initialUsername,
  isLoading,
  statusMessage,
  errorMessage,
  onLoadSubmissions,
  onSyncSubmissions,
}: LeetCodeSyncPanelProps) {
  const [username, setUsername] = useState(initialUsername);

  const handleLoad = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    await onLoadSubmissions(username);
  };

  return (
    <section className="dashboard-section" aria-labelledby="sync-heading">
      <div className="section-heading">
        <div>
          <p className="section-kicker">LeetCode sync</p>
          <h2 id="sync-heading">Load real submissions</h2>
        </div>
      </div>

      <form className="sync-form" onSubmit={handleLoad}>
        <label className="form-field" htmlFor="leetcode-username">
          <span>LeetCode username</span>
          <input
            id="leetcode-username"
            name="username"
            type="text"
            value={username}
            onChange={(event) => setUsername(event.target.value)}
            placeholder="kprashanth01"
          />
        </label>

        <div className="sync-actions">
          <button className="primary-action" disabled={isLoading} type="submit">
            Load saved submissions
          </button>
          <button
            className="secondary-action"
            disabled={isLoading}
            type="button"
            onClick={() => onSyncSubmissions(username)}
          >
            Sync from LeetCode
          </button>
        </div>

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
      </form>
    </section>
  );
}

export default LeetCodeSyncPanel;
