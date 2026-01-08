'use client';

import React, { useState } from 'react';
import { Task as TaskType, isTaskCompleted } from '../types/task';

interface TaskProps {
  task: TaskType;
  onToggle: (id: string) => void;
  onDelete: (id: string) => void;
  onEdit: (task: TaskType) => void;
}

const Task: React.FC<TaskProps> = ({ task, onToggle, onDelete, onEdit }) => {
  const [isDeleting, setIsDeleting] = useState(false);
  const [isToggling, setIsToggling] = useState(false);
  const completed = isTaskCompleted(task);

  const handleToggle = async () => {
    setIsToggling(true);
    await onToggle(task.id);
    setIsToggling(false);
  };

  const handleDelete = async () => {
    setIsDeleting(true);
    await onDelete(task.id);
  };

  const handleEdit = () => {
    onEdit(task);
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

  return (
    <div
      className={`group relative bg-white rounded-2xl border transition-all duration-300 ease-out
        ${completed
          ? 'border-gray-100 bg-gray-50/50'
          : 'border-gray-200 hover:border-indigo-200 hover:shadow-lg hover:shadow-indigo-100/50'
        }
        ${isDeleting ? 'opacity-50 scale-95' : 'opacity-100 scale-100'}
      `}
    >
      <div className="p-5">
        <div className="flex items-start gap-4">
          {/* Custom Checkbox */}
          <button
            onClick={handleToggle}
            disabled={isToggling}
            className={`relative flex-shrink-0 w-6 h-6 rounded-full border-2 transition-all duration-200
              ${completed
                ? 'bg-gradient-to-br from-emerald-400 to-emerald-500 border-emerald-500'
                : 'border-gray-300 hover:border-indigo-400 hover:bg-indigo-50'
              }
              ${isToggling ? 'animate-pulse' : ''}
            `}
          >
            {completed && (
              <svg className="absolute inset-0 w-full h-full p-1 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={3}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
              </svg>
            )}
          </button>

          {/* Content */}
          <div className="flex-1 min-w-0">
            <div className="flex items-start justify-between gap-3">
              <div className="flex-1 min-w-0">
                <h3 className={`text-base font-semibold leading-tight transition-all duration-200
                  ${completed
                    ? 'text-gray-400 line-through decoration-2'
                    : 'text-gray-900'
                  }`}
                >
                  {task.title}
                </h3>
                {task.description && (
                  <p className={`mt-1.5 text-sm leading-relaxed transition-colors duration-200
                    ${completed ? 'text-gray-400' : 'text-gray-600'}
                  `}>
                    {task.description}
                  </p>
                )}
              </div>

              {/* Actions */}
              <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
                <button
                  onClick={handleEdit}
                  className="p-2 rounded-xl text-gray-400 hover:text-indigo-600 hover:bg-indigo-50 transition-colors"
                  title="Edit task"
                >
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                  </svg>
                </button>
                <button
                  onClick={handleDelete}
                  disabled={isDeleting}
                  className="p-2 rounded-xl text-gray-400 hover:text-red-600 hover:bg-red-50 transition-colors"
                  title="Delete task"
                >
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                </button>
              </div>
            </div>

            {/* Footer */}
            <div className="mt-3 flex items-center gap-3">
              <span className={`inline-flex items-center gap-1.5 text-xs font-medium px-2.5 py-1 rounded-full
                ${completed
                  ? 'bg-emerald-50 text-emerald-600'
                  : 'bg-amber-50 text-amber-600'
                }`}
              >
                <span className={`w-1.5 h-1.5 rounded-full ${completed ? 'bg-emerald-500' : 'bg-amber-500'}`}></span>
                {completed ? 'Completed' : 'In Progress'}
              </span>
              <span className="text-xs text-gray-400">
                {formatDate(task.created_at)}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Task;
