import {
  ActivityIcon,
  CalendarDaysIcon,
  FlameIcon,
  TargetIcon,
} from "lucide-react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Pie,
  PieChart,
  XAxis,
} from "recharts";

import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  ChartConfig,
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
} from "@/components/ui/chart";
import { Progress } from "@/components/ui/progress";

import { buildAnalyticsSummary } from "./analytics";
import type { SyncedSubmission } from "../../types/dashboard";

type AnalyticsDashboardProps = {
  submissions: SyncedSubmission[];
};

type DifficultyKey = "easy" | "medium" | "hard" | "unknown";

const trendChartConfig = {
  solves: {
    label: "Solves",
    color: "#22c55e",
  },
} satisfies ChartConfig;

const difficultyChartConfig = {
  easy: { label: "Easy", color: "#22c55e" },
  medium: { label: "Medium", color: "#f59e0b" },
  hard: { label: "Hard", color: "#ef4444" },
  unknown: { label: "Unknown", color: "#64748b" },
} satisfies ChartConfig;

const difficultyColors = ["#22c55e", "#f59e0b", "#ef4444", "#64748b"];

const getHeatmapClass = (count: number) => {
  if (count >= 4) {
    return "activity-cell activity-cell-4";
  }
  if (count >= 3) {
    return "activity-cell activity-cell-3";
  }
  if (count >= 2) {
    return "activity-cell activity-cell-2";
  }
  if (count >= 1) {
    return "activity-cell activity-cell-1";
  }
  return "activity-cell";
};

const getDifficultyData = (summary: ReturnType<typeof buildAnalyticsSummary>) => [
  { name: "easy" as DifficultyKey, value: summary.difficultyBreakdown.easy },
  { name: "medium" as DifficultyKey, value: summary.difficultyBreakdown.medium },
  { name: "hard" as DifficultyKey, value: summary.difficultyBreakdown.hard },
  { name: "unknown" as DifficultyKey, value: summary.difficultyBreakdown.unknown },
];

function AnalyticsDashboard({ submissions }: AnalyticsDashboardProps) {
  const summary = buildAnalyticsSummary(submissions);
  const difficultyData = getDifficultyData(summary).filter((item) => item.value > 0);
  const topLanguageCount = summary.languageStats[0]?.count ?? 0;
  const topTopicCount = summary.topicStats[0]?.count ?? 0;

  return (
    <section className="analytics-dashboard" aria-label="Progress analytics">
      <div className="analytics-hero">
        <Card className="analytics-card analytics-card-primary">
          <CardHeader>
            <CardDescription>Current streak</CardDescription>
            <CardTitle className="analytics-score">
              <FlameIcon aria-hidden="true" />
              {summary.currentStreak}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p>
              {summary.currentStreak > 0
                ? "You solved today. Keep the chain alive."
                : "Sync a solve today to start a fresh streak."}
            </p>
            <div className="analytics-mini-row">
              <Badge variant="secondary">Max {summary.maxStreak} days</Badge>
              <Badge variant="secondary">{summary.activeDays} active days</Badge>
            </div>
          </CardContent>
        </Card>

        <Card className="analytics-card">
          <CardHeader>
            <CardDescription>Total volume</CardDescription>
            <CardTitle className="analytics-score">
              <TargetIcon aria-hidden="true" />
              {summary.totalSubmissions}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p>{summary.uniqueProblems} unique problems tracked from real syncs.</p>
          </CardContent>
        </Card>

        <Card className="analytics-card">
          <CardHeader>
            <CardDescription>Consistency</CardDescription>
            <CardTitle className="analytics-score">
              <CalendarDaysIcon aria-hidden="true" />
              {summary.activeDays}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p>Days with at least one accepted synced submission.</p>
          </CardContent>
        </Card>
      </div>

      <div className="analytics-grid">
        <Card className="analytics-card analytics-wide">
          <CardHeader>
            <CardDescription>Last 6 months</CardDescription>
            <CardTitle>Submission activity</CardTitle>
          </CardHeader>
          <CardContent>
            {summary.totalSubmissions > 0 ? (
              <div className="activity-heatmap">
                {summary.activityDays.map((day) => (
                  <span
                    className={getHeatmapClass(day.count)}
                    key={day.date}
                    title={`${day.date}: ${day.count} submissions`}
                  />
                ))}
              </div>
            ) : (
              <div className="analytics-empty">
                Sync submissions to reveal your activity heatmap.
              </div>
            )}
          </CardContent>
        </Card>

        <Card className="analytics-card">
          <CardHeader>
            <CardDescription>Weekly trend</CardDescription>
            <CardTitle>Recent momentum</CardTitle>
          </CardHeader>
          <CardContent>
            <ChartContainer
              className="analytics-chart"
              config={trendChartConfig}
              initialDimension={{ width: 420, height: 220 }}
            >
              <BarChart data={summary.weeklyTrend}>
                <CartesianGrid vertical={false} />
                <XAxis
                  axisLine={false}
                  dataKey="label"
                  tickLine={false}
                  tickMargin={10}
                />
                <ChartTooltip content={<ChartTooltipContent />} />
                <Bar dataKey="solves" fill="var(--color-solves)" radius={6} />
              </BarChart>
            </ChartContainer>
          </CardContent>
        </Card>

        <Card className="analytics-card">
          <CardHeader>
            <CardDescription>Difficulty</CardDescription>
            <CardTitle>Solve mix</CardTitle>
          </CardHeader>
          <CardContent className="difficulty-layout">
            {difficultyData.length > 0 ? (
              <>
                <ChartContainer
                  className="difficulty-chart"
                  config={difficultyChartConfig}
                  initialDimension={{ width: 220, height: 220 }}
                >
                  <PieChart>
                    <ChartTooltip content={<ChartTooltipContent hideLabel />} />
                    <Pie
                      data={difficultyData}
                      dataKey="value"
                      innerRadius={46}
                      nameKey="name"
                      outerRadius={78}
                      paddingAngle={4}
                    >
                      {difficultyData.map((entry, index) => (
                        <Cell
                          fill={difficultyColors[index % difficultyColors.length]}
                          key={entry.name}
                        />
                      ))}
                    </Pie>
                  </PieChart>
                </ChartContainer>
                <div className="difficulty-list">
                  {difficultyData.map((item, index) => (
                    <div className="difficulty-row" key={item.name}>
                      <span>
                        <i
                          aria-hidden="true"
                          style={{
                            backgroundColor:
                              difficultyColors[index % difficultyColors.length],
                          }}
                        />
                        {difficultyChartConfig[item.name].label}
                      </span>
                      <strong>{item.value}</strong>
                    </div>
                  ))}
                </div>
              </>
            ) : (
              <div className="analytics-empty">No difficulty metadata yet.</div>
            )}
          </CardContent>
        </Card>

        <Card className="analytics-card">
          <CardHeader>
            <CardDescription>Languages</CardDescription>
            <CardTitle>Primary tools</CardTitle>
          </CardHeader>
          <CardContent className="analytics-list">
            {summary.languageStats.length > 0 ? (
              summary.languageStats.slice(0, 5).map((item) => (
                <div className="metric-progress-row" key={item.language}>
                  <div>
                    <span>{item.language}</span>
                    <strong>{item.count}</strong>
                  </div>
                  <Progress
                    value={topLanguageCount ? (item.count / topLanguageCount) * 100 : 0}
                  />
                </div>
              ))
            ) : (
              <div className="analytics-empty">No language data yet.</div>
            )}
          </CardContent>
        </Card>

        <Card className="analytics-card analytics-wide">
          <CardHeader>
            <CardDescription>Topic coverage</CardDescription>
            <CardTitle>Strongest tags</CardTitle>
          </CardHeader>
          <CardContent className="topic-cloud">
            {summary.topicStats.length > 0 ? (
              summary.topicStats.map((item) => (
                <Badge
                  className="topic-badge"
                  key={item.topic}
                  style={{
                    opacity: topTopicCount ? 0.55 + item.count / topTopicCount / 2 : 1,
                  }}
                  variant="secondary"
                >
                  <ActivityIcon aria-hidden="true" />
                  {item.topic}
                  <span>{item.count}</span>
                </Badge>
              ))
            ) : (
              <div className="analytics-empty">
                Sync metadata to see topic coverage.
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </section>
  );
}

export default AnalyticsDashboard;
