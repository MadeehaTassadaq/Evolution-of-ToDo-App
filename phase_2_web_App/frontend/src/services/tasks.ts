import { Task } from '../types/task';
import { apiFetch, AuthenticationError } from '../lib/api-client';

interface ApiResponse<T> {
  data?: T;
  error?: string;
}

interface CreateTaskData {
  title: string;
  description?: string;
}

interface UpdateTaskData {
  title?: string;
  description?: string;
  status?: string;
}

class TaskService {
  async getAllTasks(): Promise<ApiResponse<Task[]>> {
    try {
      const tasks = await apiFetch<Task[]>('/api/tasks/', { method: 'GET' });
      return { data: tasks };
    } catch (error) {
      if (error instanceof AuthenticationError) {
        return { error: 'Not authenticated' };
      }
      console.error('Error fetching tasks:', error);
      return { error: error instanceof Error ? error.message : 'Failed to fetch tasks' };
    }
  }

  async createTask(taskData: CreateTaskData): Promise<ApiResponse<Task>> {
    try {
      const newTask = await apiFetch<Task>('/api/tasks/', {
        method: 'POST',
        body: JSON.stringify(taskData)
      });
      return { data: newTask };
    } catch (error) {
      if (error instanceof AuthenticationError) {
        return { error: 'Not authenticated' };
      }
      console.error('Error creating task:', error);
      return { error: error instanceof Error ? error.message : 'Failed to create task' };
    }
  }

  async updateTask(id: string, taskData: UpdateTaskData): Promise<ApiResponse<Task>> {
    try {
      const updatedTask = await apiFetch<Task>(`/api/tasks/${id}`, {
        method: 'PUT',
        body: JSON.stringify(taskData)
      });
      return { data: updatedTask };
    } catch (error) {
      if (error instanceof AuthenticationError) {
        return { error: 'Not authenticated' };
      }
      console.error('Error updating task:', error);
      return { error: error instanceof Error ? error.message : 'Failed to update task' };
    }
  }

  async deleteTask(id: string): Promise<ApiResponse<null>> {
    try {
      await apiFetch<null>(`/api/tasks/${id}`, { method: 'DELETE' });
      return { data: null };
    } catch (error) {
      if (error instanceof AuthenticationError) {
        return { error: 'Not authenticated' };
      }
      console.error('Error deleting task:', error);
      return { error: error instanceof Error ? error.message : 'Failed to delete task' };
    }
  }

  async toggleTaskCompletion(id: string): Promise<ApiResponse<Task>> {
    try {
      const updatedTask = await apiFetch<Task>(`/api/tasks/${id}/complete`, { method: 'PATCH' });
      return { data: updatedTask };
    } catch (error) {
      if (error instanceof AuthenticationError) {
        return { error: 'Not authenticated' };
      }
      console.error('Error toggling task completion:', error);
      return { error: error instanceof Error ? error.message : 'Failed to toggle task completion' };
    }
  }
}

export default new TaskService();
