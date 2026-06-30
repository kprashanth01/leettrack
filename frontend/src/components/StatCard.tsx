import type { DashboardStat } from "../types/dashboard";

type StatCardProps = {
  stat: DashboardStat;
};

function StatCard({ stat }: StatCardProps) {
  return (
    <article className="stat-card">
      <p className="stat-label">{stat.label}</p>
      <strong className="stat-value">{stat.value}</strong>
      <p className="stat-helper">{stat.helper}</p>
    </article>
  );
}

export default StatCard;
