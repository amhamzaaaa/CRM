import { useState, useEffect, type FormEvent } from "react";
import { useParams, useNavigate } from "react-router-dom";
import request from "../utils/request";
import type { TaskOut, TaskPriority, TaskUpdateIn } from "../types";
import "./DetailPage.css";

export default function TaskDetailsPage() 
{
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  // Data states
  const [task, setTask] = useState<TaskOut | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [isSaving, setIsSaving] = useState<boolean>(false);
  const [saveSuccess, setSaveSuccess] = useState<boolean>(false);

  // Form Field States
  const [title, setTitle] = useState<string>("");
  const [notes, setNotes] = useState<string>("");
  const [priority, setPriority] = useState<TaskPriority>("medium");
  const [dueAt, setDueAt] = useState<string>("");
  const [assigneeUserId, setAssigneeUserId] = useState<string>("");

  // Fetch taskj
  useEffect(() => {
    if (!id) return;

    async function fetchTask() {
      try {
        setIsLoading(true);
        setError(null);

        const data = await request<TaskOut>({
          endpoint: `/api/v1/tasks/${id}`,
          method: "GET",
        });

        setTask(data);
        setTitle(data.title);
        setNotes(data.notes || "");
        setPriority(data.priority);
        
        setDueAt(data.due_at ? data.due_at.slice(0, 16) : "");
        setAssigneeUserId(data.assignee_user_id || "");
      } 
      catch (err) 
      {
        setError(err instanceof Error ? err.message : "Failed to load task details");
      } 
      finally 
      {
        setIsLoading(false);
      }
    }

    fetchTask();
  }, [id]);

  // Handle Form Save (PATCH /api/v1/tasks/:id)
  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!id) return;

    if (!title.trim() || title.trim().length > 200) {
      alert("Title is required and must be under 200 characters.");
      return;
    }

    try {
      setIsSaving(true);
      setSaveSuccess(false);

      const payload: TaskUpdateIn = {
        title: title.trim(),
        notes: notes.trim() ? notes.trim() : null,
        priority,
        due_at: dueAt ? new Date(dueAt).toISOString() : null,
        assignee_user_id: assigneeUserId.trim() ? assigneeUserId.trim() : null,
      };

      const updated = await request<TaskOut>({
        endpoint: `/api/v1/tasks/${id}`,
        method: "PATCH",
        body: payload,
      });

      setTask(updated);
      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 2500);
    } catch (err) {
      alert(err instanceof Error ? err.message : "Failed to update task");
    } finally {
      setIsSaving(false);
    }
  }

  // Status Action
  async function handleToggleStatus() {
    if (!task || !id) return;

    const isDone = task.status === "done";
    const endpoint = `/api/v1/tasks/${id}/${isDone ? "reopen" : "complete"}`;

    try {
      const updated = await request<TaskOut>({
        endpoint,
        method: "POST",
      });
      setTask(updated);
    } catch (err) {
      alert(err instanceof Error ? err.message : "Failed to change task status");
    }
  }

  // DELETE /api/v1/tasks/:id
  async function handleDelete() {
    if (!id) return;
    const confirmed = window.confirm("Are you sure you want to delete this task? This action cannot be undone.");
    if (!confirmed) return;

    try {
      await request<void>({
        endpoint: `/api/v1/tasks/${id}`,
        method: "DELETE",
      });
      navigate("/");
    } catch (err) {
      alert(err instanceof Error ? err.message : "Failed to delete task");
    }
  }

  // Loading
  if (isLoading) {
    return <div className="details-container"><p className="state-msg">Loading task details...</p></div>;
  }

  // Error
  if (error) {
    return (
      <div className="details-container">
        <p className="state-msg error-msg">Error: {error}</p>
        <button className="btn btn-secondary" onClick={() => navigate("/")}>← Back to List</button>
      </div>
    );
  }

  // Not Found
  if (!task) {
    return (
      <>
      <div className="details-container">
        <p className="state-msg">Task not found.</p>
        <button className="btn btn-secondary" onClick={() => navigate("/")}>← Back to List</button>
      </div>
      </>
    );
  }

  const isDone = task.status === "done";
  console.log(`task status: ${task.status}, task title: ${task.title}`);
  console.log(task);
  //  Loaded or Edit View
  return (
    <div className="details-container">
      
      <div className="details-header">
        <button type="button" className="btn btn-back" onClick={() => navigate("/")}>
          ← Back to Tasks
        </button>

        <div className="details-header-actions">
          <button
            type="button"
            className={`btn ${isDone ? "btn-reopen" : "btn-complete"}`}
            onClick={handleToggleStatus}
          >
            {isDone ? "↩ Mark as Open" : "Mark as Done"}
          </button>
          <button type="button" className="btn btn-delete" onClick={handleDelete}>
            Delete
          </button>
        </div>
      </div>

      <div className="details-meta-bar">
        <span className={`status-pill ${task.status}`}>{task.status.toUpperCase()}</span>
        {task.is_overdue && !isDone && (
          <span className="overdue-pill">OVERDUE</span>
        )}
        <span className="timestamp-text">
          Created: {new Date(task.created_at).toLocaleString()}
        </span>
      </div>
      
      <form onSubmit={handleSubmit} className="details-form">
        <div className="form-group">
          <label htmlFor="title">Title *</label>
          <input
            id="title"
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            maxLength={200}
            required
            className="form-input"
            placeholder="e.g. Call back about pricing"
          />
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
          <label htmlFor="assignee">Assignee User ID (UUID)</label>
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
          <label htmlFor="notes">Notes / Description (max 2000 chars)</label>
          <textarea
            id="notes"
            rows={5}
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            maxLength={2000}
            className="form-input"
            placeholder="Add relevant notes here..."
          />
          <small className="char-count">{notes.length} / 2000</small>
        </div>

        <div className="form-footer">
          {saveSuccess && <span className="save-indicator">Changes saved successfully!</span>}
          <button type="submit" className="btn btn-save" disabled={isSaving}>
            {isSaving ? "Saving..." : "Save Changes"}
          </button>
        </div>
      </form>
    </div>
  );
}