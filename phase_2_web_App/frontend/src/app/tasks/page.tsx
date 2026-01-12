"use client";

import { useEffect, useState, useMemo } from 'react';
import { useRouter } from 'next/navigation';
import { Task, isTaskCompleted } from '@/types/task';
import taskService from '@/services/tasks';
import { useAuth } from '@/context/AuthContext';

type FilterType = 'all' | 'pending' | 'completed';
type SortType = 'newest' | 'oldest' | 'name' | 'status';

export default function DashboardPage() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<FilterType>('all');
  const [sort, setSort] = useState<SortType>('newest');
  const [showAddForm, setShowAddForm] = useState(false);
  const [editingTask, setEditingTask] = useState<Task | null>(null);
  const [newTask, setNewTask] = useState({ title: '', description: '' });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isAuthChecked, setIsAuthChecked] = useState(false);
  const router = useRouter();
  const { isAuthenticated } = useAuth(); // Use AuthContext instead of standalone util

  const stats = useMemo(() => {
    const completed = tasks.filter(t => isTaskCompleted(t)).length;
    const pending = tasks.length - completed;
    const percentage = tasks.length > 0 ? Math.round((completed / tasks.length) * 100) : 0;
    return { total: tasks.length, completed, pending, percentage };
  }, [tasks]);

  const filteredAndSortedTasks = useMemo(() => {
    let result = [...tasks];

    // Filter
    if (filter === 'pending') {
      result = result.filter(t => !isTaskCompleted(t));
    } else if (filter === 'completed') {
      result = result.filter(t => isTaskCompleted(t));
    }

    // Sort
    switch (sort) {
      case 'oldest':
        result.sort((a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime());
        break;
      case 'newest':
        result.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());
        break;
      case 'name':
        result.sort((a, b) => a.title.localeCompare(b.title));
        break;
      case 'status':
        result.sort((a, b) => {
          if (isTaskCompleted(a) === isTaskCompleted(b)) return 0;
          return isTaskCompleted(a) ? 1 : -1;
        });
        break;
    }

    return result;
  }, [tasks, filter, sort]);

  useEffect(() => {
    let isMounted = true;

    const checkAuthAndLoadTasks = async () => {
      if (!isMounted) return;

      // Wait for the component to mount before checking auth (SSR-safe)
      if (typeof window !== 'undefined') {
        // Check if user is authenticated using AuthContext
        if (!isAuthenticated) {
          // Only redirect to login if not already on login page
          if (window.location.pathname !== '/login') {
            router.replace('/login');
          }
          setIsAuthChecked(true); // Set auth checked to avoid loading spinner
          return;
        }

        // If authenticated, proceed to fetch tasks
        setIsAuthChecked(true);
        fetchTasks();
      }
    };

    // Small delay to ensure component is mounted before checking auth
    const timer = setTimeout(() => {
      checkAuthAndLoadTasks();
    }, 10);

    return () => {
      isMounted = false;
      clearTimeout(timer);
    };
  }, [isAuthenticated]); // Remove router from dependencies to prevent infinite loop


  const fetchTasks = async () => {
    try {
      setLoading(true);
      const response = await taskService.getAllTasks();
      if (response.error) {
        setError(response.error);
        return;
      }
      setTasks(response.data || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch tasks');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateTask = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTask.title.trim()) return;

    setIsSubmitting(true);
    const response = await taskService.createTask({
      title: newTask.title.trim(),
      description: newTask.description.trim() || undefined
    });

    if (response.data) {
      setTasks([response.data, ...tasks]);
      setNewTask({ title: '', description: '' });
      setShowAddForm(false);
    } else if (response.error) {
      setError(response.error);
    }
    setIsSubmitting(false);
  };

  const handleToggleTask = async (id: string) => {
    const response = await taskService.toggleTaskCompletion(id);
    if (response.data) {
      setTasks(tasks.map(task => task.id === id ? response.data! : task));
    }
  };

  const handleUpdateTask = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingTask) return;

    setIsSubmitting(true);
    const response = await taskService.updateTask(editingTask.id, {
      title: editingTask.title,
      description: editingTask.description,
      status: editingTask.status
    });

    if (response.data) {
      setTasks(tasks.map(task => task.id === editingTask.id ? response.data! : task));
      setEditingTask(null);
    }
    setIsSubmitting(false);
  };

  const handleDeleteTask = async (id: string) => {
    const response = await taskService.deleteTask(id);
    if (!response.error) {
      setTasks(tasks.filter(task => task.id !== id));
    }
  };

  const { logout } = useAuth(); // Get logout function from AuthContext

  const handleLogout = () => {
    // Use AuthContext logout function
    logout();
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
    if (diffHours < 1) return 'Just now';
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  };

  if (!isAuthChecked || loading) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center">
        <div className="flex items-center gap-3">
          <svg className="animate-spin w-8 h-8 text-emerald-500" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <span className="text-gray-400">{!isAuthChecked ? 'Checking authentication...' : 'Loading tasks...'}</span>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-black">
      {/* Background effects */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-0 right-0 w-[600px] h-[600px] bg-emerald-500/5 rounded-full blur-3xl" />
        <div className="absolute bottom-0 left-0 w-[400px] h-[400px] bg-emerald-500/5 rounded-full blur-3xl" />
      </div>

      {/* Header */}
      <header className="sticky top-0 z-50 backdrop-blur-xl bg-black/80 border-b border-gray-800/50">
        <div className="max-w-6xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-400 to-emerald-600 flex items-center justify-center">
                <svg className="w-5 h-5 text-black" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                </svg>
              </div>
              <div>
                <h1 className="text-lg font-bold text-white">TaskFlow</h1>
                <p className="text-xs text-gray-500">Dashboard</p>
              </div>
            </div>
            <button
              onClick={handleLogout}
              className="flex items-center gap-2 px-4 py-2 text-sm text-gray-400 hover:text-white hover:bg-gray-800/50 rounded-xl transition-all"
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
              </svg>
              Logout
            </button>
          </div>
        </div>
      </header>

      <main className="relative z-10 max-w-6xl mx-auto px-6 py-8">
        {/* Stats Cards */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          <div className="bg-gray-900/50 backdrop-blur border border-gray-800/50 rounded-2xl p-5">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs font-medium text-gray-500 uppercase tracking-wider">Total Tasks</p>
                <p className="text-3xl font-bold text-white mt-1">{stats.total}</p>
              </div>
              <div className="w-12 h-12 rounded-xl bg-gray-800/50 flex items-center justify-center">
                <svg className="w-6 h-6 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                </svg>
              </div>
            </div>
          </div>

          <div className="bg-gray-900/50 backdrop-blur border border-gray-800/50 rounded-2xl p-5">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs font-medium text-gray-500 uppercase tracking-wider">Pending</p>
                <p className="text-3xl font-bold text-amber-400 mt-1">{stats.pending}</p>
              </div>
              <div className="w-12 h-12 rounded-xl bg-amber-500/10 flex items-center justify-center">
                <svg className="w-6 h-6 text-amber-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
            </div>
          </div>

          <div className="bg-gray-900/50 backdrop-blur border border-gray-800/50 rounded-2xl p-5">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs font-medium text-gray-500 uppercase tracking-wider">Completed</p>
                <p className="text-3xl font-bold text-emerald-400 mt-1">{stats.completed}</p>
              </div>
              <div className="w-12 h-12 rounded-xl bg-emerald-500/10 flex items-center justify-center">
                <svg className="w-6 h-6 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
            </div>
          </div>

          <div className="bg-gray-900/50 backdrop-blur border border-gray-800/50 rounded-2xl p-5">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs font-medium text-gray-500 uppercase tracking-wider">Progress</p>
                <p className="text-3xl font-bold text-white mt-1">{stats.percentage}%</p>
              </div>
              <div className="w-12 h-12 rounded-xl bg-emerald-500/10 flex items-center justify-center">
                <svg className="w-6 h-6 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                </svg>
              </div>
            </div>
            {/* Progress bar */}
            <div className="mt-3 h-1.5 bg-gray-800 rounded-full overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-emerald-500 to-emerald-400 rounded-full transition-all duration-500"
                style={{ width: `${stats.percentage}%` }}
              />
            </div>
          </div>
        </div>

        {/* Error Alert */}
        {error && (
          <div className="mb-6 p-4 bg-red-500/10 border border-red-500/20 rounded-xl flex items-center justify-between">
            <div className="flex items-center gap-3">
              <svg className="w-5 h-5 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span className="text-sm text-red-400">{error}</span>
            </div>
            <button onClick={() => setError(null)} className="text-red-400 hover:text-red-300">
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        )}

        {/* Toolbar */}
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-6">
          <div className="flex items-center gap-2">
            {/* Filter Tabs */}
            <div className="flex items-center gap-1 p-1 bg-gray-900/50 border border-gray-800/50 rounded-xl">
              {(['all', 'pending', 'completed'] as FilterType[]).map((f) => (
                <button
                  key={f}
                  onClick={() => setFilter(f)}
                  className={`px-4 py-2 text-sm font-medium rounded-lg transition-all ${
                    filter === f
                      ? 'bg-emerald-500 text-black'
                      : 'text-gray-400 hover:text-white'
                  }`}
                >
                  {f.charAt(0).toUpperCase() + f.slice(1)}
                </button>
              ))}
            </div>

            {/* Sort Dropdown */}
            <div className="relative">
              <select
                value={sort}
                onChange={(e) => setSort(e.target.value as SortType)}
                className="appearance-none px-4 py-2.5 pr-10 bg-gray-900/50 border border-gray-800/50 rounded-xl text-sm text-gray-300 focus:outline-none focus:border-emerald-500/50 cursor-pointer"
              >
                <option value="newest">Newest First</option>
                <option value="oldest">Oldest First</option>
                <option value="name">By Name</option>
                <option value="status">By Status</option>
              </select>
              <svg className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500 pointer-events-none" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
              </svg>
            </div>
          </div>

          {/* Add Task Button */}
          <button
            onClick={() => setShowAddForm(!showAddForm)}
            className={`flex items-center gap-2 px-5 py-2.5 rounded-xl font-medium transition-all ${
              showAddForm
                ? 'bg-gray-800 text-gray-300'
                : 'bg-gradient-to-r from-emerald-500 to-emerald-600 text-black shadow-lg shadow-emerald-500/25'
            }`}
          >
            {showAddForm ? (
              <>
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
                </svg>
                Cancel
              </>
            ) : (
              <>
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" />
                </svg>
                Add Task
              </>
            )}
          </button>
        </div>

        {/* Add Task Form */}
        {showAddForm && (
          <form onSubmit={handleCreateTask} className="mb-6 p-6 bg-gray-900/50 backdrop-blur border border-gray-800/50 rounded-2xl">
            <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
              <svg className="w-5 h-5 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" />
              </svg>
              Create New Task
            </h3>
            <div className="space-y-4">
              <input
                type="text"
                value={newTask.title}
                onChange={(e) => setNewTask({ ...newTask, title: e.target.value })}
                placeholder="Task title..."
                className="w-full px-4 py-3 bg-gray-800/50 border border-gray-700/50 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:border-emerald-500/50"
                autoFocus
              />
              <textarea
                value={newTask.description}
                onChange={(e) => setNewTask({ ...newTask, description: e.target.value })}
                placeholder="Description (optional)..."
                rows={2}
                className="w-full px-4 py-3 bg-gray-800/50 border border-gray-700/50 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:border-emerald-500/50 resize-none"
              />
              <button
                type="submit"
                disabled={isSubmitting || !newTask.title.trim()}
                className="w-full flex items-center justify-center gap-2 px-5 py-3 bg-gradient-to-r from-emerald-500 to-emerald-600 text-black font-semibold rounded-xl disabled:opacity-50"
              >
                {isSubmitting ? 'Creating...' : 'Create Task'}
              </button>
            </div>
          </form>
        )}

        {/* Edit Task Modal */}
        {editingTask && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
            <form onSubmit={handleUpdateTask} className="w-full max-w-md p-6 bg-gray-900 border border-gray-800 rounded-2xl">
              <h3 className="text-lg font-semibold text-white mb-4">Edit Task</h3>
              <div className="space-y-4">
                <input
                  type="text"
                  value={editingTask.title}
                  onChange={(e) => setEditingTask({ ...editingTask, title: e.target.value })}
                  className="w-full px-4 py-3 bg-gray-800/50 border border-gray-700/50 rounded-xl text-white focus:outline-none focus:border-emerald-500/50"
                />
                <textarea
                  value={editingTask.description || ''}
                  onChange={(e) => setEditingTask({ ...editingTask, description: e.target.value })}
                  rows={3}
                  className="w-full px-4 py-3 bg-gray-800/50 border border-gray-700/50 rounded-xl text-white focus:outline-none focus:border-emerald-500/50 resize-none"
                />
                <div className="flex gap-3">
                  <button
                    type="submit"
                    disabled={isSubmitting}
                    className="flex-1 px-5 py-3 bg-emerald-500 text-black font-semibold rounded-xl"
                  >
                    {isSubmitting ? 'Saving...' : 'Save'}
                  </button>
                  <button
                    type="button"
                    onClick={() => setEditingTask(null)}
                    className="flex-1 px-5 py-3 bg-gray-800 text-gray-300 font-semibold rounded-xl"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            </form>
          </div>
        )}

        {/* Task List */}
        <div className="space-y-3">
          {filteredAndSortedTasks.length === 0 ? (
            <div className="text-center py-20">
              <div className="w-20 h-20 mx-auto mb-6 rounded-full bg-gray-900/50 border border-gray-800/50 flex items-center justify-center">
                <svg className="w-10 h-10 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold text-white mb-2">
                {filter === 'all' ? 'No tasks yet' : `No ${filter} tasks`}
              </h3>
              <p className="text-gray-500 mb-6">
                {filter === 'all' ? 'Create your first task to get started' : `You don't have any ${filter} tasks`}
              </p>
              {filter === 'all' && !showAddForm && (
                <button
                  onClick={() => setShowAddForm(true)}
                  className="inline-flex items-center gap-2 px-5 py-2.5 bg-emerald-500 text-black font-medium rounded-xl"
                >
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" />
                  </svg>
                  Create Task
                </button>
              )}
            </div>
          ) : (
            filteredAndSortedTasks.map((task) => {
              const completed = isTaskCompleted(task);
              return (
                <div
                  key={task.id}
                  className={`group p-5 bg-gray-900/50 backdrop-blur border rounded-2xl transition-all ${
                    completed
                      ? 'border-gray-800/30 opacity-60'
                      : 'border-gray-800/50 hover:border-emerald-500/30'
                  }`}
                >
                  <div className="flex items-start gap-4">
                    {/* Checkbox */}
                    <button
                      onClick={() => handleToggleTask(task.id)}
                      className={`flex-shrink-0 w-6 h-6 rounded-full border-2 transition-all ${
                        completed
                          ? 'bg-emerald-500 border-emerald-500'
                          : 'border-gray-600 hover:border-emerald-500'
                      }`}
                    >
                      {completed && (
                        <svg className="w-full h-full p-1 text-black" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={3}>
                          <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                        </svg>
                      )}
                    </button>

                    {/* Content */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-start justify-between gap-4">
                        <div>
                          <h3 className={`font-semibold ${completed ? 'text-gray-500 line-through' : 'text-white'}`}>
                            {task.title}
                          </h3>
                          {task.description && (
                            <p className={`mt-1 text-sm ${completed ? 'text-gray-600' : 'text-gray-400'}`}>
                              {task.description}
                            </p>
                          )}
                        </div>

                        {/* Actions */}
                        <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                          <button
                            onClick={() => setEditingTask(task)}
                            className="p-2 text-gray-500 hover:text-emerald-400 hover:bg-emerald-500/10 rounded-lg transition-colors"
                          >
                            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                              <path strokeLinecap="round" strokeLinejoin="round" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                            </svg>
                          </button>
                          <button
                            onClick={() => handleDeleteTask(task.id)}
                            className="p-2 text-gray-500 hover:text-red-400 hover:bg-red-500/10 rounded-lg transition-colors"
                          >
                            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                              <path strokeLinecap="round" strokeLinejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                            </svg>
                          </button>
                        </div>
                      </div>

                      {/* Footer */}
                      <div className="mt-3 flex items-center gap-3">
                        <span className={`inline-flex items-center gap-1.5 text-xs font-medium px-2.5 py-1 rounded-full ${
                          completed
                            ? 'bg-emerald-500/10 text-emerald-400'
                            : 'bg-amber-500/10 text-amber-400'
                        }`}>
                          <span className={`w-1.5 h-1.5 rounded-full ${completed ? 'bg-emerald-400' : 'bg-amber-400'}`} />
                          {completed ? 'Completed' : 'Pending'}
                        </span>
                        <span className="text-xs text-gray-600">{formatDate(task.created_at)}</span>
                      </div>
                    </div>
                  </div>
                </div>
              );
            })
          )}
        </div>
      </main>
    </div>
  );
}
