import { useState } from "react";

import { useAuth } from "../auth/AuthContext";

function getUserLabel(email?: string) {
  return email ?? "Signed in";
}

function AuthPanel() {
  const { isConfigured, isLoading, user, signInWithGitHub, signOut } = useAuth();
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

  const handleSignOut = async () => {
    setErrorMessage("");

    try {
      await signOut();
    } catch (error) {
      setErrorMessage(
        error instanceof Error ? error.message : "Could not sign out.",
      );
    }
  };

  if (!isConfigured) {
    return (
      <section className="auth-panel" aria-label="Authentication status">
        <p className="auth-label">Auth setup needed</p>
        <p className="auth-helper">Add Supabase env vars to enable login.</p>
      </section>
    );
  }

  return (
    <section className="auth-panel" aria-label="Authentication status">
      <p className="auth-label">{user ? "Signed in" : "Account"}</p>

      {isLoading ? (
        <p className="auth-helper">Checking session...</p>
      ) : user ? (
        <>
          <p className="auth-user">{getUserLabel(user.email)}</p>
          <button className="secondary-action auth-action" onClick={handleSignOut}>
            Sign out
          </button>
        </>
      ) : (
        <button className="primary-action auth-action" onClick={handleSignIn}>
          Sign in with GitHub
        </button>
      )}

      {errorMessage ? (
        <p className="auth-error" role="alert">
          {errorMessage}
        </p>
      ) : null}
    </section>
  );
}

export default AuthPanel;
