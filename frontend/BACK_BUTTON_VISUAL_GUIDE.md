# Back Button Visual Reference Guide

## Component Appearance

```
┌─────────────────────────────────┐
│  ←  Dashboard                   │  ← Back Button (subtle glass effect)
└─────────────────────────────────┘
```

## States Visual Comparison

### Default State
```
┌─────────────────────────────────┐
│  ←  Dashboard                   │  bg: white/70, border: neutral-200/80
└─────────────────────────────────┘  text: neutral-700, subtle blur
```

### Hover State
```
┌─────────────────────────────────┐
│ ←   Dashboard                   │  bg: white/90, border: neutral-300
└─────────────────────────────────┘  text: neutral-900, slight shadow
    ↑ Arrow slides left            icon moves -2px left on hover
```

### Active State
```
┌───────────────────────────────┐
│  ←  Dashboard                 │    Slightly smaller (scale 0.97)
└───────────────────────────────┘    Provides tactile feedback
```

### Focus State (Keyboard)
```
  ╔═════════════════════════════════╗
  ║  ←  Dashboard                   ║  Blue ring (brand-500)
  ╚═════════════════════════════════╝  2px ring with 2px offset
      ↑ Focus ring visible
```

## Page Layout Examples

### Upload Page Layout
```
┌───────────────────────────────────────────────────────────┐
│                                                           │
│  ┌─────────────────┐                                     │
│  │  ←  Dashboard   │  ← Back button (top-left)          │
│  └─────────────────┘                                     │
│                                                           │
│  Upload Configuration                ← Page title        │
│  Upload network device configurations for security...    │
│                                                           │
│  ┌─────────────────────────────────────────────────┐    │
│  │                                                  │    │
│  │         [Upload Area - Glass Card]              │    │
│  │                                                  │    │
│  └─────────────────────────────────────────────────┘    │
│                                                           │
└───────────────────────────────────────────────────────────┘
```

### Configurations Page Layout
```
┌───────────────────────────────────────────────────────────┐
│                                                           │
│  ┌─────────────────┐                  ┌──────────────┐  │
│  │  ←  Dashboard   │                  │ Upload New ▲ │  │
│  └─────────────────┘                  └──────────────┘  │
│                                        ↑ Action button   │
│  Configurations                       on the right       │
│  Uploaded network device configurations                  │
│                                                           │
│  ┌─────────────────────────────────────────────────┐    │
│  │  Configuration Cards...                          │    │
│  └─────────────────────────────────────────────────┘    │
│                                                           │
└───────────────────────────────────────────────────────────┘
```

### Audit Results Page Layout
```
┌───────────────────────────────────────────────────────────┐
│                                                           │
│  ┌──────────────────────┐            ┌────────────────┐ │
│  │  ←  Configurations   │            │ Download Report│ │
│  └──────────────────────┘            └────────────────┘ │
│                                       ↑ Action button    │
│  Audit Results                       on the right        │
│  cisco_config.cfg (Cisco)                                │
│                                                           │
│  ┌─────────────────────────────────────────────────┐    │
│  │  Audit Summary Cards...                          │    │
│  └─────────────────────────────────────────────────┘    │
│                                                           │
└───────────────────────────────────────────────────────────┘
```

## Size Comparison

```
Regular Button:      ┌──────────────────┐
                     │   Regular Button │  (Taller, more prominent)
                     └──────────────────┘

Back Button:         ┌────────────────┐
                     │  ←  Dashboard  │   (Compact, subtle)
                     └────────────────┘

Icon Size: 16×16px   ←  (w-4 h-4)
Text Size: 14px      Dashboard (text-sm)
Padding: 8×12px      (py-2 px-3)
```

## Color Palette

### Background
- **Default:** `rgba(255, 255, 255, 0.70)` - 70% white
- **Hover:** `rgba(255, 255, 255, 0.90)` - 90% white
- **Backdrop:** `blur(2px)` - Subtle glass effect

### Border
- **Default:** `rgba(156, 163, 175, 0.80)` - Translucent neutral-400
- **Hover:** `rgb(209, 213, 219)` - neutral-300 (more opaque)

### Text
- **Default:** `rgb(55, 65, 81)` - neutral-700
- **Hover:** `rgb(17, 24, 39)` - neutral-900 (darker)

### Focus Ring
- **Color:** `rgb(1, 109, 197)` - brand-500 (blue)
- **Width:** 2px
- **Offset:** 2px

## Spacing Guidelines

```
Page Container
│
├── Flex Container (items-start justify-between gap-4)
│   │
│   ├── Left Section (flex-1)
│   │   │
│   │   ├── Back Button Container (space-x-3 mb-2)
│   │   │   └── BackButton Component  ← 8px spacing from title below
│   │   │
│   │   ├── Page Title (text-3xl mb-2)  ← 8px spacing from description
│   │   │
│   │   └── Description (text-neutral-600)
│   │
│   └── Right Section (Optional Action Buttons)
│
└── Page Content (space-y-8)
```

## Typography

```
Component:  ←  Dashboard
            │  └── Label text
            └── Arrow icon

Icon:       Lucide React 'ArrowLeft'
            - Size: 16×16px (w-4 h-4)
            - Stroke width: 2px (default)
            - Color: Inherits text color

Label:      "Dashboard" / "Configurations"
            - Font size: 14px (text-sm)
            - Font weight: 500 (medium)
            - Color: neutral-700 → neutral-900 on hover
            - No text transform
```

## Responsive Breakpoints

### Mobile (< 640px)
```
┌─────────────────────┐
│  ←  Dashboard       │  Full label visible
│                     │  Touch-friendly size
│  Upload             │
│  Configuration      │
└─────────────────────┘
```

### Tablet (640px - 1023px)
```
┌───────────────────────────────┐
│  ←  Dashboard                 │  Identical to desktop
│                               │
│  Upload Configuration         │
└───────────────────────────────┘
```

### Desktop (≥ 1024px)
```
┌─────────────────────────────────────────┐
│  ←  Dashboard                           │  Full layout
│                                         │
│  Upload Configuration                   │
└─────────────────────────────────────────┘
```

## Animation Timing

```
Transition Timeline (200ms total):

0ms    ────┐                    Default State
           │  Hover/Click Event
50ms   ────┤  Background fades
           │  Border darkens
100ms  ────┤  Icon slides left (-2px)
           │  Shadow appears
150ms  ────┤  Text color darkens
           │
200ms  ────┘  Final State (Complete)

All transitions use: cubic-bezier(0.4, 0, 0.2, 1)
```

## Accessibility Indicators

### Visual Focus Indicator
```
  Normal:        ←  Dashboard

  Keyboard Focus:
  
  ╔═══════════════════════╗
  ║  ←  Dashboard         ║  ← 2px blue ring
  ╚═══════════════════════╝     High contrast
```

### Screen Reader Announcement
```
Role: button
Label: "Navigate back to dashboard"
State: Focusable, Pressable

Announcement: "Navigate back to dashboard, button"
```

## Integration Checklist

When adding to a new page:

- [ ] Import BackButton component
- [ ] Place in flex container with page title
- [ ] Provide `to` prop with parent route
- [ ] Provide descriptive `label` prop
- [ ] Add 8px bottom margin (mb-2)
- [ ] Position above page title
- [ ] Test keyboard navigation
- [ ] Verify hover states
- [ ] Check mobile layout

## Common Patterns

### Standard Page Header
```tsx
<div className="flex items-start justify-between gap-4">
  <div className="flex-1">
    <div className="flex items-center space-x-3 mb-2">
      <BackButton to="/parent" label="Parent" />
    </div>
    <h1 className="text-3xl font-bold mb-2 text-neutral-900">
      Page Title
    </h1>
    <p className="text-neutral-600">Description</p>
  </div>
</div>
```

### With Action Button
```tsx
<div className="flex items-start justify-between gap-4">
  <div className="flex-1">
    <div className="flex items-center space-x-3 mb-2">
      <BackButton to="/parent" label="Parent" />
    </div>
    <h1>Title</h1>
    <p>Description</p>
  </div>
  <button className="btn-primary">Action</button>
</div>
```

---

**Visual Guide Version:** 1.0.0  
**Last Updated:** September 9, 2026  
**Design System:** Glassmorphism v1.0.0
