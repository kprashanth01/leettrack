import { useState } from "react";

import StatCard from "../../components/StatCard";
import {
  dashboardStats,
  recentProblems,
  revisionItems,
} from "../../data/mockDashboardData";
import type { SolvedProblem } from "../../types/dashboard";

import ProblemLogForm from "./ProblemLogForm";
import RecentProblemsTable from "./RecentProblemsTable";
import RevisionPreview from "./RevisionPreview";

function DashboardPage() {
  const [problems, setProblems] = useState<SolvedProblem[]>(recentProblems);

  const handleAddProblem = (problem: SolvedProblem) => {
    setProblems((currentProblems) => [problem, ...currentProblems]);
  };

  return (
    <div className="dashboard" id="dashboard">
      <header className="dashboard-header">
        <div>
          <p className="page-kicker">Dashboard</p>
          <h1>Track your LeetCode progress with intent.</h1>
          <p>
            Review recent solves, spot revision work, and keep your daily
            practice loop visible.
          </p>
        </div>

        <aside className="focus-card" aria-label="Today focus">
          <p>Today&apos;s focus</p>
          <strong>Revise dynamic programming transitions</strong>
          <span>Mock recommendation based on recent practice.</span>
        </aside>
      </header>

      <section className="stats-grid" aria-label="Progress summary">
        {dashboardStats.map((stat) => (
          <StatCard key={stat.label} stat={stat} />
        ))}
      </section>

      <div className="dashboard-grid dashboard-grid-with-form">
        <ProblemLogForm onAddProblem={handleAddProblem} />
        <RevisionPreview items={revisionItems} />
      </div>

      <RecentProblemsTable problems={problems} />
    </div>
  );
}

export default DashboardPage;
