import { useState } from "react";
import { useNavigate } from "react-router-dom";
import request from "../utils/request";
import type { TaskCreateIn, TaskOut } from "../types";
import TaskForm from "../components/TaskForm";
import "./DetailPage.css"; 

export default function CreateTaskPage() {
  const navigate = useNavigate();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  async function handleCreate(payload: TaskCreateIn) {
    try {
      setIsSubmitting(true);
      setErrorMessage(null);

      await request<TaskOut>({
        endpoint: "/api/v1/tasks",
        method: "POST",
        body: payload,
      });

      navigate("/");
    } catch (err) {
      setErrorMessage(err instanceof Error ? err.message : "Failed to create task");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div className="details-container">
      <div className="details-header">
        <button type="button" className="btn btn-back" onClick={() => navigate("/")}>
          ← Back to Tasks
        </button>
      </div>

      <h2 style={{ margin: "0 0 20px 0", color: "#0f172a" }}>Create Follow-up Task</h2>

      {errorMessage && (
        <div style={{ color: "#dc2626", marginBottom: "16px", fontSize: "0.9rem" }}>
          {errorMessage}
        </div>
      )}

      <TaskForm
        onSubmit={handleCreate}
        submitButtonText="Create Task"
        isSubmitting={isSubmitting}
      />
    </div>
  );
}