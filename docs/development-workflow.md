# Development Workflow

LeetTrack is built one professional milestone at a time.

## Standard Sequence

1. Explain the objective.
2. Explain the architecture involved.
3. Explain important concepts.
4. Create or reference a GitHub issue.
5. Create a development plan.
6. Create a feature branch.
7. Implement the feature.
8. Explain important files.
9. Review the code.
10. Suggest improvements.
11. Commit with a professional message.
12. Merge only after review.

## Branch Naming

Use these prefixes:

- `feature/` for new capabilities;
- `fix/` for bug fixes;
- `refactor/` for behavior-preserving code improvements;
- `docs/` for documentation-only changes;
- `chore/` for maintenance tasks.

## Commit Style

Use Conventional Commits:

```text
feat(project): initialize LeetTrack foundation
docs(project): add architecture guide
fix(api): validate empty notes before insertion
```

## Scope Rule

Each branch should represent one logical unit of work. Avoid mixing unrelated setup, UI, API, and database changes in one commit.
