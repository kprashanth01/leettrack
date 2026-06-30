export type Difficulty = "Easy" | "Medium" | "Hard";

export type ProblemStatus = "Solved" | "Needs Review" | "Revised";

export type DashboardStat = {
  label: string;
  value: string;
  helper: string;
};

export type SolvedProblem = {
  id: string;
  title: string;
  difficulty: Difficulty;
  tags: string[];
  status: ProblemStatus;
  solvedAt: string;
};

export type RevisionItem = {
  id: string;
  title: string;
  dueLabel: string;
  note: string;
};
