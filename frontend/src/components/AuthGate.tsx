import { useState } from "react";

import { useAuth } from "../auth/AuthContext";

function AuthGate() {
  const { isConfigured, isLoading, signInWithGitHub } = useAuth();
  const [errorMessage, setErrorMessage] = useState("");

  const handleSignIn = async () => {
    setErrorMessage("");

    try {
      await signInWithGitHub();
    } catch (error) {
      setErrorMessage(
        error instanceof Error ? error.message : "Could not start GitHub login.",
      );
    }
  };

  return (
    <section className="auth-gate" aria-labelledby="auth-gate-heading">
      <div className="auth-gate-content">
        <p className="page-kicker">LeetTrack</p>
        <h1 id="auth-gate-heading">Sign in to track your LeetCode progress.</h1>
        <p>
          Your submissions, notes, revision history, and analytics belong to
          your account. Sign in before syncing or viewing dashboard data.
        </p>

        {isConfigured ? (
          <button
            className="primary-action auth-gate-action"
            disabled={isLoading}
            onClick={handleSignIn}
          >
            {isLoading ? "Checking session..." : "Sign in with GitHub"}
          </button>
        ) : (
          <p className="form-error" role="alert">
            Supabase Auth is not configured. Add the frontend env vars first.
          </p>
        )}

        {errorMessage ? (
          <p className="form-error" role="alert">
            {errorMessage}
          </p>
        ) : null}
      </div>
    </section>
  );
}

export default AuthGate;
