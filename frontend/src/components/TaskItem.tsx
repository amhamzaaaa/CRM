import "./TaskItem.css";
import { useState } from "react";
import type { TaskOut } from "../types/index";

interface TaskItemProps {
  task: TaskOut;
  onToggleComplete?: (id: string) => void;
  onDelete?: (id: string) => void;
  onEdit?: (task: TaskOut) => void;
}

function TaskItem({ task, onToggleComplete, onDelete, onEdit }: TaskItemProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  const isDone = task.status === "done";
  const hasLongNotes = Boolean(task.notes && task.notes.length > 90);

  return (
    <div className={`task-item-parent ${task.is_overdue && !isDone ? "is-overdue" : ""} ${isDone ? "is-done" : ""}`}>
      <div className="task-item-left-space">
        <input
          type="checkbox"
          checked={isDone}
          onChange={() => onToggleComplete?.(task.id)}
          className="task-checkbox"
          aria-label={`Mark "${task.title}" as complete`}
        />
      </div>
      <div className="task-item-right">
        <div className="task-item-content">
          <div className="task-item-header">
            <span className={`task-title ${isDone ? "completed" : ""}`}>
              {task.title}
            </span>

            <div className="task-badges">
              {task.is_overdue && !isDone && (
                <span className="badge badge-overdue">⚠️ Overdue</span>
              )}
              <span className={`badge badge-priority priority-${task.priority}`}>
                {task.priority}
              </span>
            </div>
          </div>

          {task.notes && (
            <div className="task-item-body">
              <p className="task-notes">
                {isExpanded || !hasLongNotes
                  ? task.notes
                  : `${task.notes.slice(0, 90)}... `}
                {hasLongNotes && (
                  <button
                    type="button"
                    className="see-more-btn"
                    onClick={() => setIsExpanded(!isExpanded)}
                  >
                    {isExpanded ? "Show less" : "See more"}
                  </button>
                )}
              </p>
            </div>
          )}

      
          <div className="task-item-footer">
            <span className="task-due-date">
              {task.due_at
                ? `Due: ${new Date(task.due_at).toLocaleDateString()}`
                : "No due date"}
            </span>

            <div className="task-actions">
              <button
                type="button"
                className="btn btn-edit"
                onClick={() => onEdit?.(task)}
              >
                Edit
              </button>
              <button
                type="button"
                className="btn btn-delete"
                onClick={() => onDelete?.(task.id)}
              >
                Delete
              </button>
            </div>
          </div>

        </div>
      </div>
    </div>
  );
}

export default TaskItem;