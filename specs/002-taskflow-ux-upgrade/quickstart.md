# Quickstart: TaskFlow UI/UX Upgrade

**Feature**: 002-taskflow-ux-upgrade
**Date**: 2026-01-08

---

## Prerequisites

- Node.js 18+ (LTS recommended)
- npm 9+ or pnpm 8+
- Modern browser (Chrome, Firefox, Safari, Edge - latest 2 versions)

---

## Project Setup

### 1. Initialize Project

```bash
# Create new Vite + React + TypeScript project
npm create vite@latest taskflow -- --template react-ts

# Navigate to project
cd taskflow

# Install dependencies
npm install
```

### 2. Install Core Dependencies

```bash
# State & Utilities
npm install uuid

# Drag and Drop
npm install @dnd-kit/core @dnd-kit/sortable @dnd-kit/utilities

# Animations
npm install framer-motion

# Date handling
npm install date-fns

# Type definitions
npm install -D @types/uuid
```

### 3. Install Development Dependencies

```bash
# Testing
npm install -D vitest @testing-library/react @testing-library/jest-dom jsdom
npm install -D @playwright/test

# Accessibility testing
npm install -D axe-core @axe-core/react

# Linting & Formatting
npm install -D eslint @typescript-eslint/eslint-plugin @typescript-eslint/parser
npm install -D prettier eslint-config-prettier
```

---

## Project Structure

```
taskflow/
├── src/
│   ├── components/
│   │   ├── common/           # Shared UI components
│   │   │   ├── Button.tsx
│   │   │   ├── Checkbox.tsx
│   │   │   ├── Input.tsx
│   │   │   └── Chip.tsx
│   │   ├── layout/           # Layout components
│   │   │   ├── Sidebar.tsx
│   │   │   ├── MainContent.tsx
│   │   │   └── AppShell.tsx
│   │   ├── task/             # Task-related components
│   │   │   ├── TaskCard.tsx
│   │   │   ├── TaskInput.tsx
│   │   │   ├── TaskList.tsx
│   │   │   └── TaskDetails.tsx
│   │   ├── navigation/       # Navigation components
│   │   │   ├── ViewList.tsx
│   │   │   ├── ProjectList.tsx
│   │   │   └── CommandPalette.tsx
│   │   └── empty-states/     # Empty state components
│   │       └── EmptyState.tsx
│   ├── hooks/                # Custom React hooks
│   │   ├── useKeyboardShortcuts.ts
│   │   ├── useRovingFocus.ts
│   │   ├── useLocalStorage.ts
│   │   └── useTasks.ts
│   ├── context/              # React Context providers
│   │   ├── AppContext.tsx
│   │   └── FocusModeContext.tsx
│   ├── services/             # Business logic & storage
│   │   ├── storage.ts
│   │   ├── taskService.ts
│   │   ├── projectService.ts
│   │   └── viewService.ts
│   ├── types/                # TypeScript type definitions
│   │   ├── task.ts
│   │   ├── project.ts
│   │   ├── tag.ts
│   │   └── view.ts
│   ├── utils/                # Utility functions
│   │   ├── date.ts
│   │   ├── validation.ts
│   │   └── id.ts
│   ├── styles/               # Global styles & design tokens
│   │   ├── tokens.css
│   │   ├── reset.css
│   │   └── global.css
│   ├── App.tsx
│   ├── main.tsx
│   └── vite-env.d.ts
├── tests/
│   ├── unit/                 # Unit tests
│   ├── integration/          # Integration tests
│   └── e2e/                  # Playwright E2E tests
├── public/
├── index.html
├── package.json
├── tsconfig.json
├── vite.config.ts
├── vitest.config.ts
└── playwright.config.ts
```

---

## Configuration Files

### vite.config.ts

```typescript
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './tests/setup.ts',
  },
});
```

### tsconfig.json (additions)

```json
{
  "compilerOptions": {
    "strict": true,
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"]
    }
  }
}
```

### playwright.config.ts

```typescript
import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './tests/e2e',
  use: {
    baseURL: 'http://localhost:5173',
  },
  webServer: {
    command: 'npm run dev',
    port: 5173,
  },
});
```

---

## Design Tokens

### styles/tokens.css

```css
:root {
  /* Spacing (4px grid) */
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-5: 20px;
  --space-6: 24px;
  --space-8: 32px;

  /* Colors - Light Mode */
  --color-bg: #FAFAFA;
  --color-surface: #FFFFFF;
  --color-border: #E5E5E5;
  --color-text-primary: #1A1A1A;
  --color-text-secondary: #6B7280;
  --color-text-muted: #9CA3AF;

  /* Priority Colors */
  --color-priority-high: #EF4444;
  --color-priority-medium: #F59E0B;
  --color-priority-low: #9CA3AF;

  /* Status Colors */
  --color-success: #10B981;
  --color-error: #EF4444;
  --color-overdue: #DC2626;

  /* Accent */
  --color-accent: #3B82F6;
  --color-accent-hover: #2563EB;

  /* Typography */
  --font-family: system-ui, -apple-system, sans-serif;
  --font-size-xs: 12px;
  --font-size-sm: 14px;
  --font-size-base: 16px;
  --font-size-lg: 18px;
  --font-size-xl: 24px;
  --font-size-2xl: 32px;

  /* Shadows */
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.1);
  --shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.1);

  /* Transitions */
  --transition-fast: 150ms ease;
  --transition-normal: 200ms ease;
  --transition-slow: 300ms ease;

  /* Focus */
  --focus-ring: 0 0 0 2px var(--color-accent);
}

/* Dark mode (future) */
@media (prefers-color-scheme: dark) {
  :root {
    /* Override for dark mode */
  }
}

/* Reduced motion */
@media (prefers-reduced-motion: reduce) {
  :root {
    --transition-fast: 0ms;
    --transition-normal: 0ms;
    --transition-slow: 0ms;
  }
}
```

---

## Running the Project

### Development

```bash
npm run dev
# Open http://localhost:5173
```

### Testing

```bash
# Unit & Integration tests
npm run test

# E2E tests
npx playwright test

# Accessibility audit
npm run test:a11y
```

### Build

```bash
npm run build
npm run preview
```

---

## Keyboard Shortcuts Reference

| Shortcut | Action |
|----------|--------|
| Enter | Create task (when input focused) |
| E | Edit selected task |
| Delete / Backspace | Delete selected task |
| Space | Toggle task completion |
| Cmd/Ctrl + K | Open command palette |
| Cmd/Ctrl + N | Focus task input |
| Up / Down | Navigate tasks |
| Escape | Close modal/exit Focus Mode |

---

## Next Steps

1. Implement core components following the structure above
2. Set up state management with React Context
3. Implement localStorage persistence
4. Add keyboard navigation and shortcuts
5. Implement drag-and-drop reordering
6. Add animations with Framer Motion
7. Run accessibility audit and fix issues
