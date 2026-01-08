# Research: TaskFlow UI/UX Upgrade

**Feature**: 002-taskflow-ux-upgrade
**Date**: 2026-01-08
**Status**: Complete

---

## Research Summary

This document captures technology decisions, best practices research, and resolved clarifications for the TaskFlow UI/UX upgrade implementation.

---

## Technology Stack Decisions

### Decision 1: Frontend Framework

**Decision**: React 18+ with TypeScript

**Rationale**:
- Component-based architecture ideal for reusable UI components (Task Card, Sidebar, Command Palette)
- Strong TypeScript support for type-safe development
- Large ecosystem for drag-and-drop, animations, and accessibility libraries
- Virtual DOM enables efficient list rendering for 1000+ tasks performance target

**Alternatives Considered**:
| Alternative | Reason Rejected |
|-------------|-----------------|
| Vue.js | Smaller ecosystem for advanced drag-and-drop libraries |
| Svelte | Less mature accessibility tooling |
| Vanilla JS | Increased complexity for state management and reactivity |

---

### Decision 2: State Management

**Decision**: React Context + useReducer for global state; local state for component-specific concerns

**Rationale**:
- Sufficient for single-user, client-side application
- No server synchronization complexity (no Redux overhead needed)
- Easy to understand and debug for small-to-medium state graphs
- Tasks, views, and UI state can be cleanly separated

**Alternatives Considered**:
| Alternative | Reason Rejected |
|-------------|-----------------|
| Redux | Overhead not justified for single-user local app |
| Zustand | Additional dependency not necessary for scope |
| MobX | Reactive patterns add complexity without clear benefit |

---

### Decision 3: Data Persistence

**Decision**: localStorage for MVP; IndexedDB upgrade path for larger datasets

**Rationale**:
- localStorage sufficient for hundreds of tasks
- No backend required (aligns with single-user assumption)
- IndexedDB provides upgrade path for 1000+ tasks without app rewrite
- Offline-first by default

**Alternatives Considered**:
| Alternative | Reason Rejected |
|-------------|-----------------|
| Backend API | Out of scope; adds deployment complexity |
| SQLite (WASM) | Overkill for MVP; consider for future phases |
| Firebase | Adds external dependency and potential costs |

---

### Decision 4: Styling Approach

**Decision**: CSS Modules or Tailwind CSS (team preference)

**Rationale**:
- CSS Modules: Scoped styles, no runtime cost, works with design system tokens
- Tailwind: Utility-first, rapid prototyping, consistent spacing/colors
- Both support the 4px/8px grid system specified in design language

**Alternatives Considered**:
| Alternative | Reason Rejected |
|-------------|-----------------|
| Styled-components | Runtime CSS-in-JS adds bundle size and performance overhead |
| Sass/SCSS | Global styles harder to maintain at scale |
| Plain CSS | No scoping; naming collisions likely |

---

### Decision 5: Drag and Drop Library

**Decision**: @dnd-kit/core

**Rationale**:
- Modern, lightweight, accessible drag-and-drop
- Built-in keyboard navigation support (aligns with accessibility requirements)
- Smooth animations and customizable drop zones
- Active maintenance and React 18 compatibility

**Alternatives Considered**:
| Alternative | Reason Rejected |
|-------------|-----------------|
| react-beautiful-dnd | Deprecated by Atlassian; no longer maintained |
| react-dnd | Lower-level API requires more boilerplate |
| Native HTML5 DnD | Poor accessibility; inconsistent mobile support |

---

### Decision 6: Animation Library

**Decision**: Framer Motion

**Rationale**:
- Declarative animation API integrates well with React
- Built-in support for layout animations (task reordering)
- Exit animations for completed tasks
- Respects prefers-reduced-motion by default

**Alternatives Considered**:
| Alternative | Reason Rejected |
|-------------|-----------------|
| CSS transitions only | Limited for complex choreographed animations |
| react-spring | Steeper learning curve for common use cases |
| GSAP | Overkill; adds significant bundle size |

---

### Decision 7: Testing Strategy

**Decision**: Vitest + React Testing Library + Playwright

**Rationale**:
- Vitest: Fast, Vite-native unit testing
- React Testing Library: User-centric component testing
- Playwright: Cross-browser E2E testing for keyboard navigation and accessibility
- Aligns with accessibility validation requirements (SC-009)

**Alternatives Considered**:
| Alternative | Reason Rejected |
|-------------|-----------------|
| Jest | Slower; Vitest provides same API with better performance |
| Cypress | Playwright has better cross-browser support |
| Enzyme | Deprecated; encourages implementation testing |

---

### Decision 8: Build Tooling

**Decision**: Vite

**Rationale**:
- Fast development server with HMR
- Optimized production builds
- Native TypeScript support
- Growing ecosystem and community

**Alternatives Considered**:
| Alternative | Reason Rejected |
|-------------|-----------------|
| Create React App | Slower; less configurable; deprecated maintenance model |
| Next.js | SSR overhead not needed for client-side SPA |
| Webpack | More configuration complexity; slower builds |

---

## Best Practices Research

### Keyboard Navigation Patterns

**Findings**:
- Use roving tabindex for task lists (one focusable item at a time)
- Arrow keys for list navigation; Tab for section changes
- Cmd/Ctrl+K command palette pattern widely adopted (VS Code, Linear, Notion)
- Escape key universally closes modals/overlays

**Implementation Guidance**:
- Implement custom useRovingFocus hook for task lists
- Register global keyboard shortcuts at app level
- Trap focus within command palette when open

---

### Accessibility Compliance (WCAG 2.1 AA)

**Findings**:
- All interactive elements need aria-label or visible text
- Focus indicators must have 3:1 contrast ratio
- Error messages must be announced via aria-live regions
- Animations must respect prefers-reduced-motion

**Implementation Guidance**:
- Use semantic HTML (button, checkbox, list) as foundation
- Test with screen readers (VoiceOver, NVDA) during development
- Integrate axe-core for automated accessibility testing

---

### Performance with Large Lists

**Findings**:
- Virtual scrolling required for 1000+ items
- React Window or TanStack Virtual recommended
- Avoid rendering off-screen tasks
- Debounce filter/sort operations

**Implementation Guidance**:
- Implement virtualized list for All Tasks view
- Keep Today/Focus views under 50 items (no virtualization needed)
- Lazy-load completed tasks view

---

### Command Palette Patterns

**Findings**:
- Fuzzy search for command matching (fuse.js or similar)
- Recent commands section improves discoverability
- Keyboard-only navigation is essential
- Actions grouped by category

**Implementation Guidance**:
- Build lightweight command registry
- Support both action commands and navigation commands
- Include search filtering with fuzzy matching

---

## Resolved Clarifications

| Topic | Clarification | Resolution |
|-------|---------------|------------|
| Data persistence | No backend specified | Use localStorage for MVP; IndexedDB for scale |
| Authentication | Single-user only | No auth required; local storage per browser |
| Offline support | Nice-to-have | Storage-first architecture enables offline by default |
| Dark mode priority | Secondary to light mode | Implement via CSS custom properties; ship light-only MVP |
| Focus Mode task count | 3-5 tasks | Default to 5; make configurable in future |

---

## Risk Mitigations

| Risk | Mitigation Strategy |
|------|---------------------|
| Keyboard shortcut conflicts | Test across browsers/OS; document known conflicts |
| Large list performance | Implement virtualization from start for All Tasks view |
| Accessibility gaps | Run axe-core in CI; manual screen reader testing |
| Animation jank | Use GPU-accelerated transforms; test on low-end devices |

---

## Next Steps

1. Proceed to data-model.md for entity design
2. Define API contracts (even for local storage abstraction)
3. Create quickstart.md with project setup instructions
