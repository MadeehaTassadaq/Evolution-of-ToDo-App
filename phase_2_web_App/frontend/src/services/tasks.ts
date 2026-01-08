import { Task } from '../types/task';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Define the shape of our API responses
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
  private getAuthHeaders(): HeadersInit {
    const token = localStorage.getItem('authToken');
    return {
      'Content-Type': 'application/json',
      ...(token && { Authorization: `Bearer ${token}` })
    };
  }

  async getAllTasks(): Promise<ApiResponse<Task[]>> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/tasks/`, {
        method: 'GET',
        headers: this.getAuthHeaders(),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const tasks = await response.json();
      return { data: tasks };
    } catch (error) {
      console.error('Error fetching tasks:', error);
      return { error: error instanceof Error ? error.message : 'Failed to fetch tasks' };
    }
  }

  async createTask(taskData: CreateTaskData): Promise<ApiResponse<Task>> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/tasks/`, {
        method: 'POST',
        headers: this.getAuthHeaders(),
        body: JSON.stringify(taskData),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const newTask = await response.json();
      return { data: newTask };
    } catch (error) {
      console.error('Error creating task:', error);
      return { error: error instanceof Error ? error.message : 'Failed to create task' };
    }
  }

  async updateTask(id: string, taskData: UpdateTaskData): Promise<ApiResponse<Task>> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/tasks/${id}`, {
        method: 'PUT',
        headers: this.getAuthHeaders(),
        body: JSON.stringify(taskData),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const updatedTask = await response.json();
      return { data: updatedTask };
    } catch (error) {
      console.error('Error updating task:', error);
      return { error: error instanceof Error ? error.message : 'Failed to update task' };
    }
  }

  async deleteTask(id: string): Promise<ApiResponse<null>> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/tasks/${id}`, {
        method: 'DELETE',
        headers: this.getAuthHeaders(),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return { data: null };
    } catch (error) {
      console.error('Error deleting task:', error);
      return { error: error instanceof Error ? error.message : 'Failed to delete task' };
    }
  }

  async toggleTaskCompletion(id: string): Promise<ApiResponse<Task>> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/tasks/${id}/complete`, {
        method: 'PATCH',
        headers: this.getAuthHeaders(),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const updatedTask = await response.json();
      return { data: updatedTask };
    } catch (error) {
      console.error('Error toggling task completion:', error);
      return { error: error instanceof Error ? error.message : 'Failed to toggle task completion' };
    }
  }
}

export default new TaskService();
