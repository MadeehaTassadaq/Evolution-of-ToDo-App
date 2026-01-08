export interface Task {
  id: string;
  title: string;
  description?: string;
  status: string;  // "pending" or "completed"
  priority?: string;
  due_date?: string;
  created_at: string;
  updated_at: string;
  user_id: string;
}

// Helper to check if task is completed
export const isTaskCompleted = (task: Task): boolean => {
  return task.status === 'completed';
};
