import express from "express";
import cors from "cors";
import fs from "fs/promises";
import path from "path";
import { fileURLToPath } from "url";
import crypto from "crypto";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const PORT = 5000;
const DB_FILE = path.join(__dirname, "tasks.json");

app.use(cors());
app.use(express.json());

// Helper: Read from JSON file
async function readTasks() {
  try {
    const data = await fs.readFile(DB_FILE, "utf-8");
    return JSON.parse(data);
  } catch (err) {
    if (err.code === "ENOENT") return [];
    throw err;
  }
}

// Helper: Write to JSON file
async function writeTasks(tasks) {
  await fs.writeFile(DB_FILE, JSON.stringify(tasks, null, 2), "utf-8");
}

// Helper: Dynamic is_overdue per 
// status == "open" && due_at != null && due_at < now()
function computeOverdue(task) {
  if (task.status !== "open" || !task.due_at) return false;
  return new Date(task.due_at).getTime() < Date.now();
}

// Helper: Consistent error envelope 
function sendError(res, status, code, message) {
  return res.status(status).json({
    error: {
      code,
      message,
      details: null,
      request_id: crypto.randomUUID(),
    },
  });
}

// Artificially simulate 300ms latency 
app.use((req, res, next) => {
  setTimeout(next, 300);
});

// GET /api/v1/tasks
app.get("/api/v1/tasks", async (req, res) => {
  try {
    let tasks = await readTasks();
    const { status, assignee_user_id, overdue, limit = "25" } = req.query;

    tasks = tasks.map((t) => ({ ...t, is_overdue: computeOverdue(t) }));

    if (status) {
      tasks = tasks.filter((t) => t.status === status);
    }
    if (assignee_user_id) {
      tasks = tasks.filter((t) => t.assignee_user_id === assignee_user_id);
    }
    if (overdue === "true") {
      tasks = tasks.filter((t) => t.is_overdue === true);
    }

    // Sort: created_at DESC, then id
    tasks.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime() || b.id.localeCompare(a.id));

    const pageLimit = Math.min(parseInt(limit, 10) || 25, 100);
    const items = tasks.slice(0, pageLimit);

    res.json({
      items,
      next_cursor: tasks.length > pageLimit ? "next-mock-cursor" : null,
    });
  } catch (err) {
    sendError(res, 500, "internal_error", "Failed to load tasks");
  }
});

// GET /api/v1/tasks/:id
app.get("/api/v1/tasks/:id", async (req, res) => {
  const tasks = await readTasks();
  const task = tasks.find((t) => t.id === req.params.id);

  if (!task) {
    return sendError(res, 404, "not_found", "Task not found");
  }

  res.json({ ...task, is_overdue: computeOverdue(task) });
});

// POST /api/v1/tasks
app.post("/api/v1/tasks", async (req, res) => {
  const { title, notes = null, priority = "medium", due_at = null, assignee_user_id = null, customer_id = null } = req.body;

  if (!title || typeof title !== "string" || !title.trim() || title.trim().length > 200) {
    return sendError(res, 422, "validation_error", "Title is required and must be between 1 and 200 characters.");
  }

  const nowIso = new Date().toISOString();
  const newTask = {
    id: crypto.randomUUID(),
    title: title.trim(),
    notes: notes || null,
    status: "open",
    priority,
    due_at: due_at || null,
    assignee_user_id: assignee_user_id || null,
    customer_id: customer_id || null,
    completed_at: null,
    is_overdue: false,
    created_at: nowIso,
    updated_at: nowIso,
  };

  newTask.is_overdue = computeOverdue(newTask);

  const tasks = await readTasks();
  tasks.unshift(newTask);
  await writeTasks(tasks);

  res.status(201).json(newTask);
});

// PATCH /api/v1/tasks/:id
app.patch("/api/v1/tasks/:id", async (req, res) => {
  const tasks = await readTasks();
  const index = tasks.findIndex((t) => t.id === req.params.id);

  if (index === -1) {
    return sendError(res, 404, "not_found", "Task not found");
  }

  const task = tasks[index];
  const updates = req.body;

  if (updates.title !== undefined) {
    if (typeof updates.title !== "string" || !updates.title.trim() || updates.title.trim().length > 200) {
      return sendError(res, 422, "validation_error", "Title must be between 1 and 200 characters.");
    }
    task.title = updates.title.trim();
  }
  if (updates.notes !== undefined) task.notes = updates.notes;
  if (updates.priority !== undefined) task.priority = updates.priority;
  if (updates.due_at !== undefined) task.due_at = updates.due_at;
  if (updates.assignee_user_id !== undefined) task.assignee_user_id = updates.assignee_user_id;
  if (updates.customer_id !== undefined) task.customer_id = updates.customer_id;

  task.updated_at = new Date().toISOString();
  task.is_overdue = computeOverdue(task);

  tasks[index] = task;
  await writeTasks(tasks);

  res.json(task);
});


app.post("/api/v1/tasks/:id/complete", async (req, res) => {
  const tasks = await readTasks();
  const index = tasks.findIndex((t) => t.id === req.params.id);

  if (index === -1) {
    return sendError(res, 404, "not_found", "Task not found");
  }

  const task = tasks[index];
  if (task.status !== "done") {
    task.status = "done";
    task.completed_at = new Date().toISOString();
    task.updated_at = new Date().toISOString();
  }
  task.is_overdue = false;

  tasks[index] = task;
  await writeTasks(tasks);

  res.json(task);
});


app.post("/api/v1/tasks/:id/reopen", async (req, res) => {
  const tasks = await readTasks();
  const index = tasks.findIndex((t) => t.id === req.params.id);

  if (index === -1) {
    return sendError(res, 404, "not_found", "Task not found");
  }

  const task = tasks[index];
  task.status = "open";
  task.completed_at = null;
  task.updated_at = new Date().toISOString();
  task.is_overdue = computeOverdue(task);

  tasks[index] = task;
  await writeTasks(tasks);

  res.json(task);
});

// DELETE /api/v1/tasks/:id (204 No Content per §2.2)
app.delete("/api/v1/tasks/:id", async (req, res) => {
  let tasks = await readTasks();
  const exists = tasks.some((t) => t.id === req.params.id);

  if (!exists) {
    return sendError(res, 404, "not_found", "Task not found");
  }

  tasks = tasks.filter((t) => t.id !== req.params.id);
  await writeTasks(tasks);

  res.status(204).send();
});

app.listen(PORT, () => {
  console.log(`Mock server running at http://localhost:${PORT}`);
});