import { FormEvent, useState } from "react";

import type {
  Difficulty,
  ProblemStatus,
  SolvedProblem,
} from "../../types/dashboard";

type ProblemLogFormProps = {
  onAddProblem: (problem: SolvedProblem) => void;
};

type FormErrors = { title?: string; tags?: string; solvedAt?: string };

const difficultyOptions: Difficulty[] = ["Easy", "Medium", "Hard"];
const statusOptions: ProblemStatus[] = ["Solved", "Needs Review", "Revised"];

const getInitialFields = () => ({
  title: "",
  difficulty: "Medium" as Difficulty,
  tags: "",
  status: "Solved" as ProblemStatus,
  solvedAt: "Today",
  notes: "",
});

const slugifyTitle = (title: string) =>
  title
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");

const dedupeTags = (tags: string[]) => {
  const seenTags = new Set<string>();

  return tags.filter((tag) => {
    const normalizedTag = tag.toLowerCase();

    if (seenTags.has(normalizedTag)) {
      return false;
    }

    seenTags.add(normalizedTag);
    return true;
  });
};

function ProblemLogForm({ onAddProblem }: ProblemLogFormProps) {
  const [fields, setFields] = useState(getInitialFields);
  const [errors, setErrors] = useState<FormErrors>({});
  const [successMessage, setSuccessMessage] = useState("");

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    const nextErrors: FormErrors = {};
    const parsedTags = dedupeTags(
      fields.tags
        .split(",")
        .map((tag) => tag.trim())
        .filter(Boolean),
    );

    if (!fields.title.trim()) {
      nextErrors.title = "Enter a problem title.";
    }

    if (parsedTags.length === 0) {
      nextErrors.tags = "Add at least one tag.";
    }

    if (!fields.solvedAt.trim()) {
      nextErrors.solvedAt = "Enter when you solved it.";
    }

    setErrors(nextErrors);

    if (Object.keys(nextErrors).length > 0) {
      setSuccessMessage("");
      return;
    }

    const slug = slugifyTitle(fields.title) || "problem";
    const problem: SolvedProblem = {
      id: `${slug}-${Date.now()}`,
      title: fields.title.trim(),
      difficulty: fields.difficulty,
      tags: parsedTags,
      status: fields.status,
      solvedAt: fields.solvedAt.trim(),
      note: fields.notes.trim() || undefined,
    };

    onAddProblem(problem);
    setFields(getInitialFields());
    setErrors({});
    setSuccessMessage("Problem added to your log.");
  };

  return (
    <section className="dashboard-section" aria-labelledby="problem-log-heading">
      <div className="section-heading">
        <div>
          <p className="section-kicker">New entry</p>
          <h2 id="problem-log-heading">Log a solved problem</h2>
        </div>
      </div>

      <form className="problem-form" onSubmit={handleSubmit} noValidate>
        {Object.keys(errors).length > 0 ? (
          <div className="form-error-summary" role="alert">
            <strong>Review the highlighted fields.</strong>
            <ul>
              {Object.values(errors).map((error) => (
                <li key={error}>{error}</li>
              ))}
            </ul>
          </div>
        ) : null}

        <label className="form-field" htmlFor="problem-title">
          <span>Problem title</span>
          <input
            id="problem-title"
            name="title"
            type="text"
            value={fields.title}
            onChange={(event) =>
              setFields((current) => ({
                ...current,
                title: event.target.value,
              }))
            }
            aria-invalid={errors.title ? "true" : "false"}
            aria-describedby={errors.title ? "problem-title-error" : undefined}
          />
          {errors.title ? (
            <span className="field-error" id="problem-title-error">
              {errors.title}
            </span>
          ) : null}
        </label>

        <div className="form-row">
          <label className="form-field" htmlFor="problem-difficulty">
            <span>Difficulty</span>
            <select
              id="problem-difficulty"
              name="difficulty"
              value={fields.difficulty}
              onChange={(event) =>
                setFields((current) => ({
                  ...current,
                  difficulty: event.target.value as Difficulty,
                }))
              }
            >
              {difficultyOptions.map((difficulty) => (
                <option key={difficulty} value={difficulty}>
                  {difficulty}
                </option>
              ))}
            </select>
          </label>

          <label className="form-field" htmlFor="problem-status">
            <span>Status</span>
            <select
              id="problem-status"
              name="status"
              value={fields.status}
              onChange={(event) =>
                setFields((current) => ({
                  ...current,
                  status: event.target.value as ProblemStatus,
                }))
              }
            >
              {statusOptions.map((status) => (
                <option key={status} value={status}>
                  {status}
                </option>
              ))}
            </select>
          </label>
        </div>

        <label className="form-field" htmlFor="problem-tags">
          <span>Tags</span>
          <input
            id="problem-tags"
            name="tags"
            type="text"
            value={fields.tags}
            onChange={(event) =>
              setFields((current) => ({
                ...current,
                tags: event.target.value,
              }))
            }
            aria-invalid={errors.tags ? "true" : "false"}
            aria-describedby={errors.tags ? "problem-tags-error" : undefined}
            placeholder="Array, Hash Map"
          />
          {errors.tags ? (
            <span className="field-error" id="problem-tags-error">
              {errors.tags}
            </span>
          ) : null}
        </label>

        <label className="form-field" htmlFor="problem-solved-at">
          <span>Solved date label</span>
          <input
            id="problem-solved-at"
            name="solvedAt"
            type="text"
            value={fields.solvedAt}
            onChange={(event) =>
              setFields((current) => ({
                ...current,
                solvedAt: event.target.value,
              }))
            }
            aria-invalid={errors.solvedAt ? "true" : "false"}
            aria-describedby={
              errors.solvedAt ? "problem-solved-at-error" : undefined
            }
          />
          {errors.solvedAt ? (
            <span className="field-error" id="problem-solved-at-error">
              {errors.solvedAt}
            </span>
          ) : null}
        </label>

        <label className="form-field" htmlFor="problem-notes">
          <span>Notes</span>
          <textarea
            id="problem-notes"
            name="notes"
            value={fields.notes}
            onChange={(event) =>
              setFields((current) => ({
                ...current,
                notes: event.target.value,
              }))
            }
            placeholder="Key idea, mistake, or revision reminder"
          />
        </label>

        <button className="primary-action" type="submit">
          Add problem
        </button>

        {successMessage ? (
          <p className="form-success" role="status">
            {successMessage}
          </p>
        ) : null}
      </form>
    </section>
  );
}

export default ProblemLogForm;
