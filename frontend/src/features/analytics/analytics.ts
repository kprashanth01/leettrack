import type { SyncedSubmission } from "../../types/dashboard";

export type DifficultyBreakdown = {
  easy: number;
  medium: number;
  hard: number;
  unknown: number;
};

export type LanguageStat = {
  language: string;
  count: number;
};

export type TopicStat = {
  topic: string;
  count: number;
};

export type ActivityDay = {
  date: string;
  count: number;
};

export type WeeklyTrendPoint = {
  label: string;
  solves: number;
};

export type AnalyticsSummary = {
  totalSubmissions: number;
  uniqueProblems: number;
  activeDays: number;
  currentStreak: number;
  maxStreak: number;
  difficultyBreakdown: DifficultyBreakdown;
  languageStats: LanguageStat[];
  topicStats: TopicStat[];
  activityDays: ActivityDay[];
  weeklyTrend: WeeklyTrendPoint[];
};

const MS_PER_DAY = 24 * 60 * 60 * 1000;
const HEATMAP_DAYS = 182;
const WEEK_COUNT = 8;

const toDateKey = (value: Date) => value.toISOString().slice(0, 10);

const getStartOfDay = (value: Date) =>
  new Date(value.getFullYear(), value.getMonth(), value.getDate());

const getStartOfWeek = (value: Date) => {
  const day = getStartOfDay(value);
  const dayIndex = day.getDay();
  day.setDate(day.getDate() - dayIndex);
  return day;
};

const getWeekLabel = (date: Date) =>
  new Intl.DateTimeFormat(undefined, {
    month: "short",
    day: "numeric",
  }).format(date);

const incrementMap = (map: Map<string, number>, key: string, amount = 1) => {
  map.set(key, (map.get(key) ?? 0) + amount);
};

const getDifficultyKey = (difficulty: string | null) => {
  switch (difficulty?.toLowerCase()) {
    case "easy":
      return "easy";
    case "medium":
      return "medium";
    case "hard":
      return "hard";
    default:
      return "unknown";
  }
};

const getStreakStats = (activityByDate: Map<string, number>) => {
  if (activityByDate.size === 0) {
    return { currentStreak: 0, maxStreak: 0 };
  }

  const solvedDates = Array.from(activityByDate.keys()).sort();
  let maxStreak = 1;
  let runningStreak = 1;

  for (let index = 1; index < solvedDates.length; index += 1) {
    const previous = new Date(`${solvedDates[index - 1]}T00:00:00`);
    const current = new Date(`${solvedDates[index]}T00:00:00`);
    const diffDays = Math.round(
      (current.getTime() - previous.getTime()) / MS_PER_DAY,
    );

    if (diffDays === 1) {
      runningStreak += 1;
    } else {
      runningStreak = 1;
    }

    maxStreak = Math.max(maxStreak, runningStreak);
  }

  let currentStreak = 0;
  const cursor = getStartOfDay(new Date());

  while (activityByDate.has(toDateKey(cursor))) {
    currentStreak += 1;
    cursor.setDate(cursor.getDate() - 1);
  }

  return { currentStreak, maxStreak };
};

export const buildAnalyticsSummary = (
  submissions: SyncedSubmission[],
): AnalyticsSummary => {
  const uniqueProblems = new Set<string>();
  const activityByDate = new Map<string, number>();
  const languageCounts = new Map<string, number>();
  const topicCounts = new Map<string, number>();
  const difficultyBreakdown: DifficultyBreakdown = {
    easy: 0,
    medium: 0,
    hard: 0,
    unknown: 0,
  };

  for (const submission of submissions) {
    uniqueProblems.add(submission.slug);
    incrementMap(activityByDate, toDateKey(new Date(submission.submittedAt)));
    incrementMap(languageCounts, submission.language);
    difficultyBreakdown[getDifficultyKey(submission.difficulty)] += 1;

    for (const topic of submission.topicTags) {
      incrementMap(topicCounts, topic);
    }
  }

  const today = getStartOfDay(new Date());
  const activityDays = Array.from({ length: HEATMAP_DAYS }, (_, index) => {
    const date = new Date(today);
    date.setDate(today.getDate() - (HEATMAP_DAYS - 1 - index));
    const dateKey = toDateKey(date);
    return {
      date: dateKey,
      count: activityByDate.get(dateKey) ?? 0,
    };
  });

  const weekStart = getStartOfWeek(today);
  const weeklyTrend = Array.from({ length: WEEK_COUNT }, (_, index) => {
    const start = new Date(weekStart);
    start.setDate(weekStart.getDate() - (WEEK_COUNT - 1 - index) * 7);
    const end = new Date(start);
    end.setDate(start.getDate() + 6);

    const solves = submissions.filter((submission) => {
      const submittedAt = new Date(submission.submittedAt);
      return submittedAt >= start && submittedAt <= end;
    }).length;

    return {
      label: getWeekLabel(start),
      solves,
    };
  });

  const languageStats = Array.from(languageCounts.entries())
    .map(([language, count]) => ({ language, count }))
    .sort((first, second) => second.count - first.count);

  const topicStats = Array.from(topicCounts.entries())
    .map(([topic, count]) => ({ topic, count }))
    .sort((first, second) => second.count - first.count)
    .slice(0, 8);

  return {
    totalSubmissions: submissions.length,
    uniqueProblems: uniqueProblems.size,
    activeDays: activityByDate.size,
    ...getStreakStats(activityByDate),
    difficultyBreakdown,
    languageStats,
    topicStats,
    activityDays,
    weeklyTrend,
  };
};
