# Problem Logging Local State Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an inline dashboard form that logs solved problems into local React state and immediately shows them in the recent problems list.

**Architecture:** `DashboardPage` will own the problems array state and pass it down to `RecentProblemsTable`. A new `ProblemLogForm` component will own controlled form inputs, validate on submit, and emit a `SolvedProblem` object to `DashboardPage` through an `onAddProblem` callback.

**Tech Stack:** React, Vite, TypeScript, CSS, local component state.

---

## Issue

GitHub Issue: `#5`  
URL: `https://github.com/kprashanth01/leettrack/issues/5`

## Branch

Create and work on:

```bash
git switch main
git pull origin main
git switch -c feature/problem-logging-ui
```

## File Structure

Create or modify these files:

- Create: `frontend/src/features/dashboard/ProblemLogForm.tsx`
- Modify: `frontend/src/features/dashboard/DashboardPage.tsx`
- Modify: `frontend/src/features/dashboard/RecentProblemsTable.tsx`
- Modify: `frontend/src/types/dashboard.ts`
- Modify: `frontend/src/styles.css`

No backend files should change. Do not add routing, API, persistence, localStorage, Axios, or TanStack Query.

---

### Task 1: Create Branch And Verify Baseline

**Files:**
- No file changes.

- [ ] **Step 1: Start from updated `main`**

Run:

```bash
git switch main
git pull origin main
```

Expected: local `main` is up to date with `origin/main`.

- [ ] **Step 2: Create the feature branch**

Run:

```bash
git switch -c feature/problem-logging-ui
```

Expected: Git switches to `feature/problem-logging-ui`.

- [ ] **Step 3: Verify existing frontend build**

Run:

```bash
cd frontend
npm run build
```

Expected: TypeScript and Vite build succeed before feature changes.

---

### Task 2: Add Problem Log Form Component

**Files:**
- Create: `frontend/src/features/dashboard/ProblemLogForm.tsx`
- Modify: `frontend/src/types/dashboard.ts`

- [ ] **Step 1: Create the controlled form component**

First update `frontend/src/types/dashboard.ts` so `SolvedProblem` can preserve an optional note:

```ts
export type SolvedProblem = {
  id: string;
  title: string;
  difficulty: Difficulty;
  tags: string[];
  status: ProblemStatus;
  solvedAt: string;
  note?: string;
};
```

Then create `frontend/src/features/dashboard/ProblemLogForm.tsx`:

```tsx
import { FormEvent, useState } from "react";

import type {
  Difficulty,
  ProblemStatus,
  SolvedProblem,
} from "../../types/dashboard";

type ProblemLogFormProps = {
  onAddProblem: (problem: SolvedProblem) => void;
};

type FormErrors = {
  title?: string;
  tags?: string;
  solvedAt?: string;
};

const difficultyOptions: Difficulty[] = ["Easy", "Medium", "Hard"];
const statusOptions: ProblemStatus[] = ["Solved", "Needs Review", "Revised"];

function createProblemId(title: string) {
  return `${title
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/(^-|-$)/g, "")}-${Date.now()}`;
}

function parseTags(tagsInput: string) {
  const seenTags = new Set<string>();

  return tagsInput
    .split(",")
    .map((tag) => tag.trim())
    .filter(Boolean)
    .filter((tag) => {
      const normalizedTag = tag.toLowerCase();

      if (seenTags.has(normalizedTag)) {
        return false;
      }

      seenTags.add(normalizedTag);
      return true;
    });
}

function ProblemLogForm({ onAddProblem }: ProblemLogFormProps) {
  const [title, setTitle] = useState("");
  const [difficulty, setDifficulty] = useState<Difficulty>("Medium");
  const [tagsInput, setTagsInput] = useState("");
  const [status, setStatus] = useState<ProblemStatus>("Solved");
  const [solvedAt, setSolvedAt] = useState("Today");
  const [notes, setNotes] = useState("");
  const [errors, setErrors] = useState<FormErrors>({});
  const [successMessage, setSuccessMessage] = useState("");

  function validateForm() {
    const nextErrors: FormErrors = {};
    const tags = parseTags(tagsInput);

    if (!title.trim()) {
      nextErrors.title = "Problem title is required.";
    }

    if (tags.length === 0) {
      nextErrors.tags = "Add at least one topic tag.";
    }

    if (!solvedAt.trim()) {
      nextErrors.solvedAt = "Solved date label is required.";
    }

    return { nextErrors, tags };
  }

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const { nextErrors, tags } = validateForm();

    if (Object.keys(nextErrors).length > 0) {
      setErrors(nextErrors);
      setSuccessMessage("");
      return;
    }

    const problem: SolvedProblem = {
      id: createProblemId(title),
      title: title.trim(),
      difficulty,
      tags,
      status,
      solvedAt: solvedAt.trim(),
      note: notes.trim() || undefined,
    };

    onAddProblem(problem);
    setTitle("");
    setDifficulty("Medium");
    setTagsInput("");
    setStatus("Solved");
    setSolvedAt("Today");
    setNotes("");
    setErrors({});
    setSuccessMessage(`Logged ${problem.title}.`);
  }

  return (
    <section className="dashboard-section problem-form-section" aria-labelledby="problem-form-heading">
      <div className="section-heading">
        <div>
          <p className="section-kicker">Log solved problem</p>
          <h2 id="problem-form-heading">Add your latest solve</h2>
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

        <label className="form-field">
          <span>Problem title</span>
          <input
            aria-describedby={errors.title ? "title-error" : undefined}
            aria-invalid={Boolean(errors.title)}
            onChange={(event) => setTitle(event.target.value)}
            placeholder="e.g. Longest Substring Without Repeating Characters"
            value={title}
          />
          {errors.title ? (
            <small className="field-error" id="title-error">
              {errors.title}
            </small>
          ) : null}
        </label>

        <div className="form-row">
          <label className="form-field">
            <span>Difficulty</span>
            <select
              onChange={(event) => setDifficulty(event.target.value as Difficulty)}
              value={difficulty}
            >
              {difficultyOptions.map((option) => (
                <option key={option} value={option}>
                  {option}
                </option>
              ))}
            </select>
          </label>

          <label className="form-field">
            <span>Status</span>
            <select
              onChange={(event) => setStatus(event.target.value as ProblemStatus)}
              value={status}
            >
              {statusOptions.map((option) => (
                <option key={option} value={option}>
                  {option}
                </option>
              ))}
            </select>
          </label>
        </div>

        <label className="form-field">
          <span>Tags</span>
          <input
            aria-describedby={errors.tags ? "tags-error" : undefined}
            aria-invalid={Boolean(errors.tags)}
            onChange={(event) => setTagsInput(event.target.value)}
            placeholder="Array, Hash Map, Sliding Window"
            value={tagsInput}
          />
          {errors.tags ? (
            <small className="field-error" id="tags-error">
              {errors.tags}
            </small>
          ) : null}
        </label>

        <label className="form-field">
          <span>Solved date label</span>
          <input
            aria-describedby={errors.solvedAt ? "solved-at-error" : undefined}
            aria-invalid={Boolean(errors.solvedAt)}
            onChange={(event) => setSolvedAt(event.target.value)}
            placeholder="Today"
            value={solvedAt}
          />
          {errors.solvedAt ? (
            <small className="field-error" id="solved-at-error">
              {errors.solvedAt}
            </small>
          ) : null}
        </label>

        <label className="form-field">
          <span>Notes</span>
          <textarea
            onChange={(event) => setNotes(event.target.value)}
            placeholder="What pattern or mistake should you remember?"
            rows={4}
            value={notes}
          />
        </label>

        <button className="primary-action" type="submit">
          Log problem
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
```

- [ ] **Step 2: Verify the new component compiles while unused**

Run:

```bash
cd frontend
npm run build
```

Expected: build succeeds with `ProblemLogForm.tsx` present.

---

### Task 3: Lift Problems Into Dashboard State

**Files:**
- Modify: `frontend/src/features/dashboard/DashboardPage.tsx`
- Modify: `frontend/src/features/dashboard/RecentProblemsTable.tsx`

- [ ] **Step 1: Update dashboard composition to own local problem state**

Update `frontend/src/features/dashboard/DashboardPage.tsx`:

```tsx
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

  function handleAddProblem(problem: SolvedProblem) {
    setProblems((currentProblems) => [problem, ...currentProblems]);
  }

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
```

- [ ] **Step 2: Verify local state integration compiles**

Update `frontend/src/features/dashboard/RecentProblemsTable.tsx` so optional notes render under the problem title:

```tsx
<td data-label="Problem">
  <strong>{problem.title}</strong>
  {problem.note ? <p className="problem-note">{problem.note}</p> : null}
</td>
```

- [ ] **Step 3: Verify local state integration compiles**

Run:

```bash
cd frontend
npm run build
```

Expected: build succeeds after wiring `ProblemLogForm` into `DashboardPage`.

---

### Task 4: Add Problem Form Styles

**Files:**
- Modify: `frontend/src/styles.css`

- [ ] **Step 1: Add form layout and field styles**

In `frontend/src/styles.css`, add these styles after the `.dashboard-grid` block:

```css
.dashboard-grid-with-form {
  grid-template-columns: minmax(0, 1fr) minmax(300px, 0.8fr);
}

.problem-form {
  display: grid;
  gap: 16px;
  padding: 20px;
}

.form-row {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}

.form-field {
  display: grid;
  gap: 8px;
}

.form-field span {
  color: #475569;
  font-size: 0.82rem;
  font-weight: 800;
}

.form-field input,
.form-field select,
.form-field textarea {
  width: 100%;
  border: 1px solid #d8e0ec;
  border-radius: 8px;
  background: #ffffff;
  color: #172033;
  font-size: 0.95rem;
  padding: 12px 13px;
}

.form-field textarea {
  min-height: 112px;
  resize: vertical;
}

.form-field input:focus,
.form-field select:focus,
.form-field textarea:focus {
  border-color: #2563eb;
  box-shadow: 0 0 0 3px rgb(37 99 235 / 0.14);
  outline: none;
}

.form-field input[aria-invalid="true"] {
  border-color: #dc2626;
}

.field-error {
  color: #b91c1c;
  font-size: 0.8rem;
  font-weight: 700;
}

.form-error-summary {
  border: 1px solid #fecaca;
  border-radius: 8px;
  background: #fff1f2;
  color: #991b1b;
  font-size: 0.88rem;
  font-weight: 700;
  padding: 12px;
}

.form-error-summary strong {
  display: block;
  margin-bottom: 6px;
}

.form-error-summary ul {
  margin: 0;
  padding-left: 18px;
}

.primary-action {
  width: fit-content;
  border: 0;
  border-radius: 8px;
  background: #1d4ed8;
  color: #ffffff;
  cursor: pointer;
  font-size: 0.95rem;
  font-weight: 800;
  padding: 12px 16px;
}

.primary-action:hover {
  background: #1e40af;
}

.form-success {
  margin: 0;
  border-radius: 8px;
  background: #e8f7ef;
  color: #047857;
  font-size: 0.88rem;
  font-weight: 800;
  padding: 12px;
}

.problem-note {
  max-width: 34rem;
  margin: 6px 0 0;
  color: #64748b;
  font-size: 0.84rem;
  line-height: 1.45;
  overflow-wrap: anywhere;
}
```

- [ ] **Step 2: Extend the mobile form layout**

Inside the existing `@media (max-width: 640px)` block in `frontend/src/styles.css`, add:

```css
  .form-row {
    grid-template-columns: 1fr;
  }

  .primary-action {
    width: 100%;
  }
```

- [ ] **Step 3: Verify styles compile**

Run:

```bash
cd frontend
npm run build
```

Expected: build succeeds after form styles are added.

---

### Task 5: Manual Interaction Verification

**Files:**
- Review: `frontend/src/features/dashboard/ProblemLogForm.tsx`
- Review: `frontend/src/features/dashboard/DashboardPage.tsx`
- Review: `frontend/src/styles.css`

- [ ] **Step 1: Start frontend dev server**

Run:

```bash
cd frontend
npm run dev
```

Expected: Vite prints a local URL, usually `http://localhost:5173`.

- [ ] **Step 2: Verify empty-submit validation**

In the browser:

1. Clear `Problem title`.
2. Clear `Tags`.
3. Clear `Solved date label`.
4. Submit the form.

Expected:

- title validation message appears;
- tags validation message appears;
- solved date validation message appears;
- no new problem is added to the table.

- [ ] **Step 3: Verify valid submit updates the problem list**

In the browser, submit:

```text
Problem title: Longest Substring Without Repeating Characters
Difficulty: Medium
Status: Needs Review
Tags: String, Sliding Window, Hash Map
Solved date label: Today
Notes: Remember to move the left pointer past the last duplicate index.
```

Expected:

- success message appears;
- new problem appears at the top of the recent problems list;
- tags are split into `String`, `Sliding Window`, and `Hash Map`;
- default mock problems still remain below the new item.

- [ ] **Step 4: Verify tag trimming edge case**

Submit another valid problem with tags:

```text
Array,  , Prefix Sum,  
```

Expected:

- the new problem appears in the table;
- tags display only `Array` and `Prefix Sum`;
- empty tag values are not rendered.

- [ ] **Step 5: Verify mobile layout**

Use browser responsive mode or a narrow browser width around `390px`.

Expected:

- problem form fields stack cleanly;
- submit button spans the available width;
- problem list remains readable;
- there is no horizontal page overflow.

---

### Task 6: Final Scope And Build Verification

**Files:**
- Review all changed frontend files.

- [ ] **Step 1: Run final frontend build**

Run:

```bash
cd frontend
npm run build
```

Expected: TypeScript and Vite build succeed.

- [ ] **Step 2: Confirm frontend-only scope**

Run:

```bash
git diff --name-only
```

Expected changed files:

```text
frontend/src/features/dashboard/DashboardPage.tsx
frontend/src/features/dashboard/ProblemLogForm.tsx
frontend/src/features/dashboard/RecentProblemsTable.tsx
frontend/src/types/dashboard.ts
frontend/src/styles.css
docs/superpowers/specs/2026-07-01-problem-logging-local-state-design.md
docs/superpowers/plans/2026-07-01-problem-logging-local-state.md
```

- [ ] **Step 3: Confirm no forbidden integrations**

Run:

```bash
rg -n "axios|TanStack|useQuery|react-router|createBrowserRouter|localStorage|fetch\\(|http://|https://|localhost|8000" frontend/src
```

Expected: no matches.

- [ ] **Step 4: Commit implementation**

Run:

```bash
git add frontend/src/features/dashboard/DashboardPage.tsx frontend/src/features/dashboard/ProblemLogForm.tsx frontend/src/features/dashboard/RecentProblemsTable.tsx frontend/src/types/dashboard.ts frontend/src/styles.css docs/superpowers/specs/2026-07-01-problem-logging-local-state-design.md docs/superpowers/plans/2026-07-01-problem-logging-local-state.md
git commit -m "feat(frontend): add local problem logging form"
```

Expected: one implementation commit on `feature/problem-logging-ui`.

---

## Manual Testing Steps

- Run `npm run build` inside `frontend/`.
- Submit the empty form and verify validation messages.
- Submit a valid problem and verify it appears at the top of the list.
- Submit tags with extra spaces and empty comma segments and verify only non-empty tags render.
- Submit duplicate tags and verify each tag appears once.
- Submit a note and verify it appears under the problem title.
- Resize to mobile width and verify no horizontal page overflow.
- Confirm no backend server is required.

## Edge Cases

- Empty title should block submit.
- Empty tags should block submit.
- Empty solved date label should block submit.
- Extra spaces around tags should be trimmed.
- Consecutive commas should not create empty tag pills.
- Duplicate tags should only render once.
- Long problem titles should wrap instead of overflowing.

## Future Improvements

- Persist locally logged problems with a backend API and database.
- Add search and filters for the problem list.
- Add edit/delete actions for locally logged problems.
- Expand notes into a dedicated notes/revision workflow when backend persistence exists.

## Plan Self-Review

- Spec coverage: Tasks cover inline form, controlled inputs, local state, validation, notes preservation, immediate list update, form reset, styling, and verification.
- Placeholder scan: No unfinished implementation placeholders remain.
- Type consistency: The form emits the existing `SolvedProblem` shape consumed by `RecentProblemsTable`.
- Scope check: Backend calls, localStorage, database, auth, router, Axios, TanStack Query, search/filter behavior, edit/delete actions, scheduler logic, and AI remain out of scope.
