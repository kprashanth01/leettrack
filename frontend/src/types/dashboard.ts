export type DashboardStat = {
  label: string;
  value: string;
  helper: string;
};

export type SyncedSubmission = {
  title: string;
  slug: string;
  language: string;
  submittedAt: string;
  source: "leetcode";
  difficulty: string | null;
  topicTags: string[];
};

export type ProblemNote = {
  id: number;
  problemTitle: string;
  problemSlug: string;
  difficulty: string | null;
  topicTags: string[];
  content: string;
  createdAt: string;
  updatedAt: string;
};

export type TrackedProblem = {
  id: number;
  problemTitle: string;
  problemSlug: string;
  difficulty: string | null;
  topicTags: string[];
  source: "extension";
  createdAt: string;
};
