import { FormEvent, useEffect, useMemo, useRef, useState } from "react";
import { useSearchParams } from "react-router-dom";

import {
  createProblemNote,
  deleteProblemNote,
  fetchProblemNotes,
  updateProblemNote,
} from "../../api/notes";
import type {
  ProblemNote,
  SyncedSubmission,
  TrackedProblem,
} from "../../types/dashboard";
import { useWorkspaceData } from "../workspace/WorkspaceDataContext";

const formatUpdatedAt = (value: string) =>
  new Intl.DateTimeFormat(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));

type NoteableProblem = {
  title: string;
  slug: string;
  difficulty: string | null;
  topicTags: string[];
  sourceLabel: "Solved" | "Saved";
};

const getLatestSubmissions = (submissions: SyncedSubmission[]) => {
  const latestBySlug = new Map<string, SyncedSubmission>();

  for (const submission of submissions) {
    const existing = latestBySlug.get(submission.slug);
    if (
      !existing ||
      new Date(submission.submittedAt).getTime() >
        new Date(existing.submittedAt).getTime()
    ) {
      latestBySlug.set(submission.slug, submission);
    }
  }

  return Array.from(latestBySlug.values());
};

const getNoteableProblems = (
  submissions: SyncedSubmission[],
  trackedProblems: TrackedProblem[],
) => {
  const problemsBySlug = new Map<string, NoteableProblem>();

  for (const submission of getLatestSubmissions(submissions)) {
    problemsBySlug.set(submission.slug, {
      title: submission.title,
      slug: submission.slug,
      difficulty: submission.difficulty,
      topicTags: submission.topicTags,
      sourceLabel: "Solved",
    });
  }

  for (const trackedProblem of trackedProblems) {
    if (problemsBySlug.has(trackedProblem.problemSlug)) {
      continue;
    }

    problemsBySlug.set(trackedProblem.problemSlug, {
      title: trackedProblem.problemTitle,
      slug: trackedProblem.problemSlug,
      difficulty: trackedProblem.difficulty,
      topicTags: trackedProblem.topicTags,
      sourceLabel: "Saved",
    });
  }

  return Array.from(problemsBySlug.values()).sort((first, second) =>
    first.title.localeCompare(second.title),
  );
};

function NotesPage() {
  const { submissions, trackedProblems, username } = useWorkspaceData();
  const [searchParams] = useSearchParams();
  const requestedProblemSlug = searchParams.get("problemSlug")?.trim() ?? "";
  const appliedRequestedProblemRef = useRef<string | null>(null);
  const problems = useMemo(
    () => getNoteableProblems(submissions, trackedProblems),
    [submissions, trackedProblems],
  );
  const [notes, setNotes] = useState<ProblemNote[]>([]);
  const [selectedSlug, setSelectedSlug] = useState("");
  const [content, setContent] = useState("");
  const [editingNoteId, setEditingNoteId] = useState<number | null>(null);
  const [isLoadingNotes, setIsLoadingNotes] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [statusMessage, setStatusMessage] = useState("");
  const [errorMessage, setErrorMessage] = useState("");
  const problemCount = problems.length;
  const selectedProblem = problems.find((problem) => problem.slug === selectedSlug);
  const showSelectedProblemFallback = Boolean(selectedSlug && !selectedProblem);
  const editingNote = notes.find((note) => note.id === editingNoteId);

  useEffect(() => {
    if (
      requestedProblemSlug &&
      appliedRequestedProblemRef.current !== requestedProblemSlug
    ) {
      appliedRequestedProblemRef.current = requestedProblemSlug;
      setSelectedSlug(requestedProblemSlug);
      return;
    }

    if (requestedProblemSlug) {
      return;
    }

    if (!selectedSlug && problems.length > 0) {
      setSelectedSlug(problems[0].slug);
    }
  }, [problems, requestedProblemSlug, selectedSlug]);

  useEffect(() => {
    let isMounted = true;
    setIsLoadingNotes(true);
    setErrorMessage("");

    fetchProblemNotes()
      .then((savedNotes) => {
        if (isMounted) {
          setNotes(savedNotes);
        }
      })
      .catch((error) => {
        if (isMounted) {
          setErrorMessage(
            error instanceof Error ? error.message : "Could not load notes.",
          );
        }
      })
      .finally(() => {
        if (isMounted) {
          setIsLoadingNotes(false);
        }
      });

    return () => {
      isMounted = false;
    };
  }, []);

  const resetEditor = () => {
    setEditingNoteId(null);
    setContent("");
    setStatusMessage("");
  };

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const trimmedContent = content.trim();

    if (!selectedSlug) {
      setErrorMessage("Sync or save problems before writing notes.");
      setStatusMessage("");
      return;
    }

    if (!trimmedContent) {
      setErrorMessage("Write a note before saving.");
      setStatusMessage("");
      return;
    }

    setIsSaving(true);
    setErrorMessage("");
    setStatusMessage("");

    try {
      if (editingNoteId) {
        const updatedNote = await updateProblemNote(editingNoteId, trimmedContent);
        setNotes((currentNotes) =>
          currentNotes.map((note) =>
            note.id === updatedNote.id ? updatedNote : note,
          ),
        );
        setStatusMessage("Note updated.");
      } else {
        const createdNote = await createProblemNote(selectedSlug, trimmedContent);
        setNotes((currentNotes) => [createdNote, ...currentNotes]);
        setStatusMessage("Note saved.");
      }
      setContent("");
      setEditingNoteId(null);
    } catch (error) {
      setErrorMessage(
        error instanceof Error ? error.message : "Could not save note.",
      );
    } finally {
      setIsSaving(false);
    }
  };

  const handleEdit = (note: ProblemNote) => {
    setEditingNoteId(note.id);
    setSelectedSlug(note.problemSlug);
    setContent(note.content);
    setStatusMessage("");
    setErrorMessage("");
  };

  const handleDelete = async (noteId: number) => {
    setIsSaving(true);
    setErrorMessage("");
    setStatusMessage("");

    try {
      await deleteProblemNote(noteId);
      setNotes((currentNotes) =>
        currentNotes.filter((note) => note.id !== noteId),
      );
      if (editingNoteId === noteId) {
        resetEditor();
      }
      setStatusMessage("Note deleted.");
    } catch (error) {
      setErrorMessage(
        error instanceof Error ? error.message : "Could not delete note.",
      );
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="workspace-page">
      <header className="page-header">
        <div>
          <p className="page-kicker">Notes</p>
          <h1>Capture what each solve taught you.</h1>
          <p>
            Attach notes to solved and saved LeetCode problems so observations,
            mistakes, and patterns stay connected to your practice history.
          </p>
        </div>
        <aside className="focus-card" aria-label="Notes summary">
          <p>Notes workspace</p>
          <strong>{notes.length} notes</strong>
          <span>
            {problemCount} tracked problems
            {username ? ` from ${username}` : ""}
          </span>
        </aside>
      </header>

      <section className="notes-layout">
        <form
          className="dashboard-section note-editor"
          onSubmit={handleSubmit}
          aria-labelledby="note-editor-heading"
        >
          <div className="section-heading">
            <div>
              <p className="section-kicker">Editor</p>
              <h2 id="note-editor-heading">
                {editingNote ? "Edit note" : "New problem note"}
              </h2>
            </div>
            {editingNote ? <span className="section-meta">Editing</span> : null}
          </div>

          {problemCount > 0 ? (
            <div className="note-form-body">
              <label className="form-field" htmlFor="note-problem">
                <span>Tracked problem</span>
                <select
                  id="note-problem"
                  value={selectedSlug}
                  onChange={(event) => setSelectedSlug(event.target.value)}
                  disabled={isSaving || editingNoteId !== null}
                >
                  {showSelectedProblemFallback ? (
                    <option value={selectedSlug}>{selectedSlug}</option>
                  ) : null}
                  {problems.map((problem) => (
                    <option key={problem.slug} value={problem.slug}>
                      {problem.title}
                    </option>
                  ))}
                </select>
              </label>

              {selectedProblem ? (
                <div className="note-problem-preview">
                  <span
                    className={
                      selectedProblem.difficulty
                        ? `badge badge-${selectedProblem.difficulty.toLowerCase()}`
                        : "tag"
                    }
                  >
                    {selectedProblem.difficulty ?? "Unknown"}
                  </span>
                  <span className="problem-note">{selectedProblem.slug}</span>
                  <span className="tag">{selectedProblem.sourceLabel}</span>
                </div>
              ) : null}

              <label className="form-field" htmlFor="note-content">
                <span>Note</span>
                <textarea
                  id="note-content"
                  value={content}
                  onChange={(event) => setContent(event.target.value)}
                  placeholder="What did you miss? What pattern unlocked it? What should future-you review?"
                  rows={8}
                  disabled={isSaving}
                />
              </label>

              <div className="note-actions">
                <button className="primary-action" disabled={isSaving} type="submit">
                  {isSaving
                    ? "Saving..."
                    : editingNote
                      ? "Update note"
                      : "Save note"}
                </button>
                {editingNote ? (
                  <button
                    className="secondary-action"
                    disabled={isSaving}
                    onClick={resetEditor}
                    type="button"
                  >
                    Cancel edit
                  </button>
                ) : null}
              </div>

              {statusMessage ? (
                <p className="form-success" role="status">
                  {statusMessage}
                </p>
              ) : null}
              {errorMessage ? (
                <p className="form-error" role="alert">
                  {errorMessage}
                </p>
              ) : null}
            </div>
          ) : (
            <div className="empty-state">
              <strong>Sync problems before writing notes.</strong>
              <p>
                Go to Dashboard to sync submissions, or save a detected problem
                from the extension, then return here to attach notes.
              </p>
            </div>
          )}
        </form>

        <section className="dashboard-section note-list-section">
          <div className="section-heading">
            <div>
              <p className="section-kicker">Notebook</p>
              <h2>Saved notes</h2>
            </div>
            <span className="section-meta">{notes.length} notes</span>
          </div>

          {isLoadingNotes ? (
            <div className="empty-state">
              <strong>Loading notes...</strong>
              <p>Fetching your saved problem notes from LeetTrack.</p>
            </div>
          ) : notes.length > 0 ? (
            <div className="note-list">
              {notes.map((note) => (
                <article className="note-card" key={note.id}>
                  <div className="note-card-header">
                    <div>
                      <h3>{note.problemTitle}</h3>
                      <p className="problem-note">{note.problemSlug}</p>
                    </div>
                    {note.difficulty ? (
                      <span className={`badge badge-${note.difficulty.toLowerCase()}`}>
                        {note.difficulty}
                      </span>
                    ) : null}
                  </div>

                  <p className="note-content">{note.content}</p>

                  {note.topicTags.length > 0 ? (
                    <div className="tag-list">
                      {note.topicTags.slice(0, 5).map((tag) => (
                        <span className="tag" key={tag}>
                          {tag}
                        </span>
                      ))}
                    </div>
                  ) : null}

                  <div className="note-card-footer">
                    <span>Updated {formatUpdatedAt(note.updatedAt)}</span>
                    <div className="note-actions">
                      <button
                        className="secondary-action"
                        disabled={isSaving}
                        onClick={() => handleEdit(note)}
                        type="button"
                      >
                        Edit
                      </button>
                      <button
                        className="secondary-action"
                        disabled={isSaving}
                        onClick={() => handleDelete(note.id)}
                        type="button"
                      >
                        Delete
                      </button>
                    </div>
                  </div>
                </article>
              ))}
            </div>
          ) : (
            <div className="empty-state empty-state-large">
              <strong>No notes yet.</strong>
              <p>
                Pick one of your {problemCount} tracked problems and save the
                key idea, mistake, or revision hint you want to remember.
              </p>
            </div>
          )}
        </section>
      </section>
    </div>
  );
}

export default NotesPage;
