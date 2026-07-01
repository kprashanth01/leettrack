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
    <section
      className="auth-screen auth-screen-dark dark"
      aria-labelledby="auth-gate-heading"
    >
      <div className="auth-screen-copy">
        <div className="auth-brand">
          <span className="brand-mark" aria-hidden="true">
            LT
          </span>
          <div>
            <p className="brand-name">LeetTrack</p>
            <p className="brand-caption">CP progress tracker</p>
          </div>
        </div>

        <div>
          <p className="page-kicker">Private workspace</p>
          <h1 id="auth-gate-heading">Sign in before syncing LeetCode data.</h1>
          <p className="auth-screen-lede">
            LeetTrack stores your submissions, notes, revision history, and
            analytics under your account. GitHub login keeps that workspace
            separate from every other user.
          </p>
        </div>
      </div>

      <div className="auth-card" aria-label="Sign in">
        <p className="auth-card-label">Account</p>
        <h2>Continue with GitHub</h2>
        <p>
          After signing in, you can sync accepted submissions and review your
          real saved dashboard.
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
