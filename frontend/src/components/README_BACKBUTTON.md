# BackButton Component

A professional, accessible back navigation control with glassmorphism styling.

## Overview

The `BackButton` component provides a consistent, user-friendly way to navigate backward through the application hierarchy. It features subtle glassmorphism styling that matches the design system and provides intelligent navigation fallbacks.

## Usage

### Basic Usage

```tsx
import BackButton from '../components/BackButton';

// Navigate to specific route (recommended)
<BackButton to="/dashboard" label="Dashboard" />

// Use browser history
<BackButton label="Back" />
```

### Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `to` | `string` | `undefined` | Optional target route for navigation |
| `label` | `string` | `"Back"` | Button text label |
| `className` | `string` | `""` | Additional CSS classes |

## Navigation Hierarchy

```
Dashboard (/)
├── Upload (/upload) → Back to Dashboard
├── Configurations (/configurations) → Back to Dashboard
    └── Audit Results (/audit/:id) → Back to Configurations
```

## Accessibility

- Semantic `<button>` element
- Descriptive `aria-label` for screen readers
- Visible focus indicator
- Keyboard accessible (Tab to focus, Enter/Space to activate)
- Touch-friendly tap target

## Design

The component features:
- Semi-transparent white background with subtle blur
- Smooth hover/active/focus states
- Arrow icon with slide animation
- Compact, non-intrusive design
- Consistent with glassmorphism design system
