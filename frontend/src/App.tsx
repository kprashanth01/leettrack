import AppShell from "./components/AppShell";
import AuthGate from "./components/AuthGate";
import DashboardPage from "./features/dashboard/DashboardPage";
import { useAuth } from "./auth/AuthContext";

function App() {
  const { isLoading, user } = useAuth();

  if (isLoading) {
    return (
      <section
        className="auth-screen auth-screen-loading"
        aria-label="Loading account"
      >
        <div className="auth-brand">
          <span className="brand-mark" aria-hidden="true">
            LT
          </span>
          <div>
            <p className="brand-name">LeetTrack</p>
            <p className="brand-caption">CP progress tracker</p>
          </div>
        </div>
        <p className="auth-loading-text">Checking your session...</p>
      </section>
    );
  }

  if (!user) {
    return <AuthGate />;
  }

  return (
    <AppShell>
      <DashboardPage />
    </AppShell>
  );
}

export default App;
