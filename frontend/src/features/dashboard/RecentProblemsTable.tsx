import type {
  Difficulty,
  ProblemStatus,
  SolvedProblem,
} from "../../types/dashboard";

type RecentProblemsTableProps = {
  problems: SolvedProblem[];
};

const difficultyClassName: Record<Difficulty, string> = {
  Easy: "badge badge-easy",
  Medium: "badge badge-medium",
  Hard: "badge badge-hard",
};

const statusClassName: Record<ProblemStatus, string> = {
  Solved: "status status-solved",
  "Needs Review": "status status-review",
  Revised: "status status-revised",
};

function RecentProblemsTable({ problems }: RecentProblemsTableProps) {
  return (
    <section className="dashboard-section" aria-labelledby="recent-problems-heading">
      <div className="section-heading">
        <div>
          <p className="section-kicker">Problem log</p>
          <h2 id="recent-problems-heading">Recent solved problems</h2>
        </div>
        <span className="section-meta">{problems.length} entries</span>
      </div>

      <div className="table-card">
        <table>
          <thead>
            <tr>
              <th scope="col">Problem</th>
              <th scope="col">Difficulty</th>
              <th scope="col">Tags</th>
              <th scope="col">Status</th>
              <th scope="col">Solved</th>
            </tr>
          </thead>
          <tbody>
            {problems.map((problem) => (
              <tr key={problem.id}>
                <td data-label="Problem">
                  <strong>{problem.title}</strong>
                </td>
                <td data-label="Difficulty">
                  <span className={difficultyClassName[problem.difficulty]}>
                    {problem.difficulty}
                  </span>
                </td>
                <td data-label="Tags">
                  <div className="tag-list">
                    {problem.tags.map((tag) => (
                      <span className="tag" key={tag}>
                        {tag}
                      </span>
                    ))}
                  </div>
                </td>
                <td data-label="Status">
                  <span className={statusClassName[problem.status]}>
                    {problem.status}
                  </span>
                </td>
                <td data-label="Solved">{problem.solvedAt}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

export default RecentProblemsTable;
