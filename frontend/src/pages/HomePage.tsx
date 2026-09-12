import "./HomePage.css";
import {useState, useEffect} from "react";
import TaskItem from "../components/TaskItem";
import request from "../utils/request";
import type { TaskOut, CursorPage } from "../types/index";
import { useNavigate } from "react-router-dom";



const HomePage = () => {
  const [tasks, setTasks] = useState<TaskOut[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    async function loadTasks() {
      try {
        setIsLoading(true);
        setError(null);

        // Fetch using the generic <CursorPage<TaskOut>>
        const data = await request<CursorPage<TaskOut>>({
          endpoint: "/api/v1/tasks",
          method: "GET",
        });

        setTasks(data.items);
      }
       catch (err) 
      {
        setError(err instanceof Error ? err.message : "Failed to load tasks");
      } 
      finally 
      {
        setIsLoading(false);
      }
    }

    loadTasks();
  }, []);

  function handleCreate() {
    navigate(`/create`);
  }

  function handleEdit(task: TaskOut) {
    navigate(`/detail/${task.id}`);
  }
  
  async function handleDelete(id: string) {
    const confirmed = window.confirm("Are you sure you want to delete this task?");
    if (!confirmed) return;

    try {
      setActionError(null);
      await request<void>({
        endpoint: `/api/v1/tasks/${id}`,
        method: "DELETE",
      });

      setTasks((prev) => prev.filter((task) => task.id !== id));
    } catch (err) {
      setActionError(err instanceof Error ? err.message : "Failed to delete task");
    }
  }

  async function handleToggleComplete(id: string) {
    const target = tasks.find((t) => t.id === id);
    if (!target) return;

    const previousTasks = [...tasks];
    const willBeDone = target.status !== "done";
    const endpoint = `/api/v1/tasks/${id}/${willBeDone ? "complete" : "reopen"}`;

    // Apply change
    setTasks((prev) =>
      prev.map((task) => {
        if (task.id !== id) return task;
        return {
          ...task,
          status: willBeDone ? "done" : "open",
          completed_at: willBeDone ? new Date().toISOString() : null,
          is_overdue: willBeDone ? false : task.is_overdue,
        };
      })
    );

    // Dispatch Network Request
    try {
      setActionError(null);
      const serverUpdatedTask = await request<TaskOut>({
        endpoint,
        method: "POST",
      });

      // Sync fields
      setTasks((prev) =>
        prev.map((t) => (t.id === id ? serverUpdatedTask : t))
      );
    } catch (err) {
      //Rollback on Rejection
      setTasks(previousTasks);
      setActionError(
        `Failed to update "${target.title}". Rolled back changes.`
      );
    }
  }

  if (isLoading) {
    return <div style={{ padding: "20px" }}>Loading tasks...</div>;
  }

  if (error) {
    return (
      <div style={{ padding: "20px", color: "#dc2626" }}>
        <p>Error: {error}</p>
        <button onClick={() => window.location.reload()}>Retry</button>
      </div>
    );
  }

  if (tasks.length === 0) {
    return <div style={{ padding: "20px" }}>No tasks found.</div>;
  }

  return (
    <div style={{ padding: '24px', maxWidth: '1000px', margin: '0 auto'}}>
      <div className="header">
        <h1 style={{textAlign: 'center'}}> Follow-up Tasks</h1>
        <button onClick={handleCreate} className="btn btn-create"> Create </button>
      </div>
      
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '16px'}}>
        {tasks.map(task => (
            <TaskItem 
              key={task.id}
              task={task}
              onToggleComplete={handleToggleComplete}
              onDelete={handleDelete}
              onEdit={handleEdit}
            />
        ))}
      </div>
    </div>
  )
}

export default HomePage
