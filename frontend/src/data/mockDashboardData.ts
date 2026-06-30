import type {
  DashboardStat,
  RevisionItem,
  SolvedProblem,
} from "../types/dashboard";

export const dashboardStats: DashboardStat[] = [
  {
    label: "Total solved",
    value: "128",
    helper: "Across 18 topic areas",
  },
  {
    label: "Solved this week",
    value: "7",
    helper: "3 more than last week",
  },
  {
    label: "Current streak",
    value: "9 days",
    helper: "Keep the rhythm steady",
  },
  {
    label: "Revisions due",
    value: "12",
    helper: "Prioritize weak patterns",
  },
];

export const recentProblems: SolvedProblem[] = [
  {
    id: "two-sum",
    title: "Two Sum",
    difficulty: "Easy",
    tags: ["Array", "Hash Map"],
    status: "Revised",
    solvedAt: "Today",
  },
  {
    id: "coin-change",
    title: "Coin Change",
    difficulty: "Medium",
    tags: ["Dynamic Programming", "BFS"],
    status: "Needs Review",
    solvedAt: "Yesterday",
  },
  {
    id: "binary-tree-level-order-traversal",
    title: "Binary Tree Level Order Traversal",
    difficulty: "Medium",
    tags: ["Tree", "Queue"],
    status: "Solved",
    solvedAt: "2 days ago",
  },
  {
    id: "minimum-window-substring",
    title: "Minimum Window Substring",
    difficulty: "Hard",
    tags: ["Sliding Window", "Hash Map"],
    status: "Needs Review",
    solvedAt: "4 days ago",
  },
];

export const revisionItems: RevisionItem[] = [
  {
    id: "coin-change-review",
    title: "Coin Change",
    dueLabel: "Due today",
    note: "Revisit the transition: dp[amount] = min(dp[amount], dp[amount - coin] + 1).",
  },
  {
    id: "minimum-window-review",
    title: "Minimum Window Substring",
    dueLabel: "Due tomorrow",
    note: "Practice explaining why the left pointer only moves after all required chars are covered.",
  },
  {
    id: "tree-bfs-review",
    title: "Binary Tree Level Order Traversal",
    dueLabel: "Due this week",
    note: "Compare queue-based BFS with recursive DFS by depth.",
  },
];
