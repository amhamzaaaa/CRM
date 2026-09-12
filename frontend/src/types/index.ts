export type TaskStatus = "open" | "done";
export type TaskPriority = "low" | "medium" | "high";

export interface TaskOut {
  id: string;
  title: string;
  notes: string | null;
  status: TaskStatus;
  priority: TaskPriority;
  due_at: string | null;
  assignee_user_id: string | null;
  customer_id: string | null;
  completed_at: string | null;
  is_overdue: boolean;
  created_at: string;
  updated_at: string;
}

export interface TaskCreateIn {
  title: string;
  notes?: string | null;
  priority?: TaskPriority;
  due_at?: string | null;
  assignee_user_id?: string | null;
  customer_id?: string | null;
}
export type TaskUpdateIn = Partial<TaskCreateIn>; // Partial makes every property optional

export interface CursorPage<T> {
  items: T[];
  next_cursor: string | null;
}