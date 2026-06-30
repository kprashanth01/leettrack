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
};
