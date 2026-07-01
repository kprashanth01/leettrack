import { Navigate, Route, Routes } from "react-router-dom";

import AppShell from "./components/AppShell";
import AuthGate from "./components/AuthGate";
import DashboardPage from "./features/dashboard/DashboardPage";
import NotesPage from "./features/notes/NotesPage";
import ProblemsPage from "./features/problems/ProblemsPage";
import ReviewPage from "./features/review/ReviewPage";
import { WorkspaceDataProvider } from "./features/workspace/WorkspaceDataContext";
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
    <WorkspaceDataProvider>
      <AppShell>
        <Routes>
          <Route element={<Navigate replace to="/dashboard" />} path="/" />
          <Route element={<DashboardPage />} path="/dashboard" />
          <Route element={<ProblemsPage />} path="/problems" />
          <Route element={<NotesPage />} path="/notes" />
          <Route element={<ReviewPage />} path="/review" />
          <Route element={<Navigate replace to="/dashboard" />} path="*" />
        </Routes>
      </AppShell>
    </WorkspaceDataProvider>
  );
}

export default App;
