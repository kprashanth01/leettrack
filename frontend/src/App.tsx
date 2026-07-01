import AppShell from "./components/AppShell";
import AuthGate from "./components/AuthGate";
import DashboardPage from "./features/dashboard/DashboardPage";
import { useAuth } from "./auth/AuthContext";

function App() {
  const { isLoading, user } = useAuth();

  return (
    <AppShell>
      {isLoading ? (
        <section className="auth-gate" aria-label="Loading account">
          <div className="auth-gate-content">
            <p className="page-kicker">LeetTrack</p>
            <h1>Checking your session.</h1>
          </div>
        </section>
      ) : user ? (
        <DashboardPage />
      ) : (
        <AuthGate />
      )}
    </AppShell>
  );
}

export default App;
