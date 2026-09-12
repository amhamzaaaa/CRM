import { useState, type FormEvent } from "react";
import type { TaskCreateIn, TaskPriority } from "../types";
import "./TaskForm.css";

export interface TaskFormValues {
  title: string;
  notes: string;
  priority: TaskPriority;
  due_at: string;
  assignee_user_id: string;
}

interface TaskFormProps {
  initialValues?: Partial<TaskFormValues>;
  onSubmit: (values: TaskCreateIn) => Promise<void>;
  submitButtonText?: string;
  isSubmitting?: boolean;
}

export default function TaskForm({
  initialValues,
  onSubmit,
  submitButtonText = "Save Task",
  isSubmitting = false,
}: TaskFormProps) {
  const [title, setTitle] = useState(initialValues?.title || "");
  const [notes, setNotes] = useState(initialValues?.notes || "");
  const [priority, setPriority] = useState<TaskPriority>(initialValues?.priority || "medium");
  const [dueAt, setDueAt] = useState(
    initialValues?.due_at ? initialValues.due_at.slice(0, 16) : ""
  );
  const [assigneeUserId, setAssigneeUserId] = useState(initialValues?.assignee_user_id || "");
  const [titleError, setTitleError] = useState<string | null>(null);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();

    const trimmedTitle = title.trim();
    if (!trimmedTitle) {
      setTitleError("Title is required.");
      return;
    }
    if (trimmedTitle.length > 200) {
      setTitleError("Title must be under 200 characters.");
      return;
    }
    setTitleError(null);

    const payload: TaskCreateIn = {
      title: trimmedTitle,
      notes: notes.trim() ? notes.trim() : null,
      priority,
      due_at: dueAt ? new Date(dueAt).toISOString() : null,
      assignee_user_id: assigneeUserId.trim() ? assigneeUserId.trim() : null,
    };

    await onSubmit(payload);
  }

  return (
    <form onSubmit={handleSubmit} className="task-form">
      <div className="form-group">
        <label htmlFor="title">Title *</label>
        <input
          id="title"
          type="text"
          value={title}
          onChange={(e) => {
            setTitle(e.target.value);
            if (titleError) setTitleError(null);
          }}
          maxLength={200}
          required
          className={`form-input ${titleError ? "input-error" : ""}`}
          placeholder="e.g. Follow up on proposal"
        />
        {titleError && <span className="field-error">{titleError}</span>}
      </div>

      <div className="form-row">
        <div className="form-group">
          <label htmlFor="priority">Priority</label>
          <select
            id="priority"
            value={priority}
            onChange={(e) => setPriority(e.target.value as TaskPriority)}
            className="form-input"
          >
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="dueAt">Due Date & Time</label>
          <input
            id="dueAt"
            type="datetime-local"
            value={dueAt}
            onChange={(e) => setDueAt(e.target.value)}
            className="form-input"
          />
        </div>
      </div>

      <div className="form-group">
        <label htmlFor="assignee">Assignee User ID</label>
        <input
          id="assignee"
          type="text"
          value={assigneeUserId}
          onChange={(e) => setAssigneeUserId(e.target.value)}
          className="form-input"
          placeholder="e.g. usr_101 or UUID"
        />
      </div>

      <div className="form-group">
        <label htmlFor="notes">Notes (max 2000 chars)</label>
        <textarea
          id="notes"
          rows={4}
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          maxLength={2000}
          className="form-input"
          placeholder="Details, next steps, context..."
        />
        <small className="char-count">{notes.length} / 2000</small>
      </div>

      <div className="form-footer">
        <button type="submit" className="btn btn-save" disabled={isSubmitting}>
          {isSubmitting ? "Saving..." : submitButtonText}
        </button>
      </div>
    </form>
  );
}