# Motion & Interaction System
## Refined Animation & Microinteractions

This document outlines the motion design system that makes the interface feel smooth, responsive, and premium without unnecessary animations.

---

## Design Philosophy

**Core Principle:** Motion should communicate, not decorate.

### Objectives:
✅ **Responsive** - Immediate feedback to user actions  
✅ **Smooth** - Natural transitions without jank  
✅ **Polished** - Premium feel through subtle refinement  
✅ **Calm** - Never distracting or overwhelming  
✅ **Fast** - Doesn't slow users down  

### Anti-Patterns:
❌ Decorative animations  
❌ Slow transitions that create wait time  
❌ Aggressive scaling  
❌ Excessive bounce/spring effects  
❌ Animation for animation's sake  

---

## Timing System

### CSS Variables (Defined in `:root`)
```css
--transition-fast:   150ms  /* Quick feedback */
--transition-base:   200ms  /* Standard transitions */
--transition-medium: 300ms  /* Glass cards, complex states */
--transition-slow:   500ms  /* Page transitions, large changes */
```

### Easing Functions
```css
--ease-in-out: cubic-bezier(0.4, 0, 0.2, 1)     /* Standard */
--ease-out:    cubic-bezier(0, 0, 0.2, 1)       /* Entrances */
--ease-in:     cubic-bezier(0.4, 0, 1, 1)       /* Exits */
--ease-spring: cubic-bezier(0.34, 1.56, 0.64, 1) /* Playful (use sparingly) */
```

### Usage Guidelines:
- **150ms** - Hover states, button presses, badges
- **200ms** - Card hovers, links, standard interactions
- **300ms** - Glass effects, smooth elevations
- **500ms** - Page enter, complex animations

---

## Reduced Motion Support

### Implementation
```css
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```

### Accessibility First
- Respects user's system preference
- Instant state changes instead of transitions
- No vestibular disturbance
- Full functionality preserved

### Testing:
- **macOS**: System Preferences → Accessibility → Display → Reduce motion
- **Windows**: Settings → Ease of Access → Display → Show animations
- **Dev Tools**: Can simulate in Chrome/Firefox

---

## Button States

### Primary Button
```css
.btn-primary {
  transition: all 200ms;
}

/* Hover */
.btn-primary:hover {
  background: brand-700;
  box-shadow: light;
}

/* Active */
.btn-primary:active {
  background: brand-800;
  transform: scale(0.98);
}

/* Focus (keyboard) */
.btn-primary:focus-visible {
  outline: none;
  ring: 2px brand-500;
  ring-offset: 2px;
}

/* Disabled */
.btn-primary:disabled {
  background: neutral-300;
  cursor: not-allowed;
  box-shadow: none;
}
```

### Microinteractions:
- ✅ Subtle scale on active (98%, not 95%)
- ✅ Shadow elevation on hover
- ✅ Color darkening
- ✅ Clear focus ring for keyboard users

---

## Card Interactions

### Standard Card Hover
```css
.card {
  transition: all 200ms;
}

.card:hover {
  box-shadow: md-light;
}
```

### Interactive Card
```css
.card-interactive {
  transition: all 200ms;
  cursor: pointer;
}

.card-interactive:hover {
  box-shadow: lg-light;
  transform: translateY(-1px);
  border-color: neutral-300;
}

.card-interactive:active {
  transform: scale(0.99);
}
```

### Glass Card Hover
```css
.card-glass:hover {
  box-shadow: glass-lg;
  transform: translateY(-2px);
  transition: all 300ms;
}
```

### Principles:
- Slight elevation (1-2px, not 10px)
- Shadow intensification
- Border color shift (subtle)
- Scale on active (feedback)

---

## Icon Microinteractions

### Arrow Icons (CTAs)
```tsx
<ArrowUpRight className="group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform duration-200" />
```

**Effect:** Diagonal movement suggests forward motion

### Play Icons (Actions)
```tsx
<Play className="group-hover:scale-110 transition-transform duration-200" />
```

**Effect:** Slight grow indicates readiness

### Back Arrow (Navigation)
```tsx
<ArrowLeft className="hover:scale-110" />
```

**Effect:** Emphasis on interactive nature

### Principles:
- Subtle movement (0.5-1rem)
- Contextual direction
- Scale 1.05-1.10 max
- Always within `group` context

---

## Page Transitions

### Page Enter Animation
```css
.page-enter {
  animation: fadeIn 300ms var(--ease-out);
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}
```

**Usage:**
```tsx
<div className="space-y-8 page-enter">
  {/* Page content */}
</div>
```

**Why Simple:**
- Fast (300ms)
- Imperceptible but smooth
- No layout shift
- CPU-friendly (opacity only)

### Alternative: Fade In Up
```css
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
```

**Usage:** Empty state icon entrance

---

## Stagger Animations

### List Stagger
```css
.stagger-item {
  animation: fadeInUp 400ms var(--ease-out) backwards;
}

.stagger-item:nth-child(1) { animation-delay: 50ms; }
.stagger-item:nth-child(2) { animation-delay: 100ms; }
.stagger-item:nth-child(3) { animation-delay: 150ms; }
.stagger-item:nth-child(4) { animation-delay: 200ms; }
.stagger-item:nth-child(5) { animation-delay: 250ms; }
.stagger-item:nth-child(6) { animation-delay: 300ms; }
```

**Usage:**
```tsx
{configurations.map((config, index) => (
  <div 
    className="card stagger-item"
    style={{ animationDelay: `${index * 50}ms` }}
  >
    {/* Content */}
  </div>
))}
```

**Effect:** Cards appear sequentially, creating flow

**Limitations:**
- First 6 items only (performance)
- 50ms delay between items
- Stops feeling laggy beyond 6

---

## Loading States

### Spinner
```css
.spinner {
  animation: spin 1s linear infinite;
  border-bottom: 2px solid brand-600;
}
```

**Usage:**
```tsx
<div className="spinner h-12 w-12"></div>
```

### Skeleton Loader
```css
.skeleton {
  background: neutral-200;
  border-radius: 0.5rem;
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}
```

**Usage:**
```tsx
<div className="skeleton h-4 w-32"></div>
```

### Shimmer Effect
```css
.skeleton-shimmer::after {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(
    90deg,
    transparent,
    rgba(255, 255, 255, 0.6),
    transparent
  );
  animation: shimmer 2s infinite;
}

@keyframes shimmer {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(100%); }
}
```

**When to Use:**
- **Spinner**: Quick operations (<2s)
- **Skeleton**: Content loading (layout known)
- **Shimmer**: Premium loading feel

---

## Expand/Collapse

### Implementation
```tsx
const [expanded, setExpanded] = useState(false);

<div 
  onClick={() => setExpanded(!expanded)}
  className="cursor-pointer"
>
  <div className={`transition-transform duration-200 ${expanded ? 'rotate-180' : ''}`}>
    <ChevronDown className="w-5 h-5" />
  </div>
</div>

{expanded && (
  <div className="animate-[fadeIn_200ms_var(--ease-out)]">
    {/* Expanded content */}
  </div>
)}
```

**Effects:**
- Icon rotates 180° on expand
- Content fades in (no slide—too slow)
- Smooth icon rotation
- Fast content appearance

---

## Hover State Examples

### Link Hover
```css
.link {
  color: brand-600;
  transition: colors 150ms;
  text-decoration: none;
  text-underline-offset: 2px;
}

.link:hover {
  color: brand-700;
  text-decoration: underline;
}
```

### Input Hover & Focus
```css
.input-primary {
  border: 1px solid neutral-300;
  transition: all 200ms;
}

.input-primary:hover:not(:focus) {
  border-color: neutral-400;
}

.input-primary:focus {
  outline: none;
  ring: 2px brand-500;
  border-color: transparent;
}
```

### Badge Hover (if interactive)
```css
.badge {
  transition: all 150ms;
}

.badge:hover {
  transform: translateY(-1px);
  box-shadow: sm-light;
}
```

---

## Focus States (Keyboard Navigation)

### Global Focus Style
```css
*:focus-visible {
  outline: none;
  ring: 2px brand-500;
  ring-offset: 2px;
}
```

### Button Focus
```css
.btn-primary:focus-visible {
  ring: 2px brand-500;
  ring-offset: 2px;
  outline: none;
}

.btn-secondary:focus-visible {
  ring: 2px neutral-400;
  ring-offset: 2px;
  outline: none;
}
```

### Principles:
- Only show on keyboard focus (`:focus-visible`)
- Never remove outline without replacement
- Clear, high-contrast ring
- 2px offset for breathing room

---

## Performance Optimization

### Hardware-Accelerated Properties
✅ **Prefer:**
- `transform`
- `opacity`
- `filter` (with caution)

❌ **Avoid:**
- `width`, `height`
- `top`, `left`, `right`, `bottom`
- `margin`, `padding`
- `background-position`

### Will-Change
```css
.card-interactive:hover {
  will-change: transform;
}
```

**Usage:**
- Only on hover/active states
- Remove when not needed
- Don't apply globally

### Layers
```css
.floating-element {
  transform: translateZ(0);
  /* Forces GPU layer */
}
```

---

## Animation Keyframes Reference

### fadeIn
```css
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}
```
**Duration:** 300ms  
**Easing:** ease-out  
**Usage:** Page entrances

### fadeInUp
```css
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
```
**Duration:** 400ms  
**Easing:** ease-out  
**Usage:** Staggered lists, cards

### scaleIn
```css
@keyframes scaleIn {
  from {
    transform: scale(0.95);
    opacity: 0;
  }
  to {
    transform: scale(1);
    opacity: 1;
  }
}
```
**Duration:** 500ms  
**Easing:** ease-out  
**Usage:** Modal entrances, special emphasis

### shimmer
```css
@keyframes shimmer {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(100%); }
}
```
**Duration:** 2s  
**Easing:** linear  
**Usage:** Skeleton loaders

### slideInRight
```css
@keyframes slideInRight {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}
```
**Duration:** 300ms  
**Easing:** ease-out  
**Usage:** Sidebar, drawer entrances

---

## Implementation Checklist

### Adding Motion to New Component:

1. **Identify Purpose**
   - [ ] Does motion communicate state?
   - [ ] Does it provide feedback?
   - [ ] Does it enhance UX?

2. **Choose Timing**
   - [ ] Fast (150ms) for immediate feedback
   - [ ] Base (200ms) for standard transitions
   - [ ] Medium (300ms) for complex states
   - [ ] Slow (500ms) only for major changes

3. **Select Properties**
   - [ ] Prefer `transform` and `opacity`
   - [ ] Avoid layout-triggering properties
   - [ ] Use `will-change` on hover if needed

4. **Test Reduced Motion**
   - [ ] Enable reduced motion preference
   - [ ] Verify functionality preserved
   - [ ] Ensure instant state changes

5. **Test Performance**
   - [ ] No jank on scroll
   - [ ] Smooth on 60fps displays
   - [ ] Acceptable on mobile devices

---

## Common Patterns

### Button with Icon Microinteraction
```tsx
<button className="btn-primary group flex items-center space-x-2">
  <span>Action</span>
  <ArrowRight className="w-4 h-4 group-hover:translate-x-0.5 transition-transform duration-200" />
</button>
```

### Interactive Card
```tsx
<div className="card hover:border-brand-300 transition-all duration-200 cursor-pointer hover:shadow-lg-light hover:translate-y-[-2px]">
  {/* Content */}
</div>
```

### Loading Button
```tsx
<button className="btn-primary" disabled={loading}>
  {loading ? (
    <>
      <div className="spinner h-4 w-4 border-white"></div>
      <span>Loading...</span>
    </>
  ) : (
    <span>Submit</span>
  )}
</button>
```

### Collapsible Section
```tsx
<div className={`transition-transform duration-200 ${expanded ? 'rotate-180' : ''}`}>
  <ChevronDown />
</div>

{expanded && (
  <div className="animate-[fadeIn_200ms_var(--ease-out)]">
    {/* Content */}
  </div>
)}
```

---

## Do's and Don'ts

### ✅ Do:
- Use motion purposefully
- Keep transitions fast (< 300ms typically)
- Provide immediate feedback
- Respect reduced motion
- Test on actual devices
- Use hardware-accelerated properties
- Maintain consistent timing
- Focus on microinteractions

### ❌ Don't:
- Add decorative animations
- Use slow transitions (> 500ms)
- Animate layout properties
- Ignore accessibility
- Overuse spring/bounce
- Scale beyond 1.1x
- Create wait states
- Animate everything

---

## Browser Compatibility

### CSS Transitions
- **All modern browsers**: Full support
- **IE11**: Partial (no CSS variables)

### CSS Animations
- **All modern browsers**: Full support
- **Safari**: Requires `-webkit-` for some properties

### Backdrop Filter (with motion)
- **Chrome/Edge 76+**: Full support
- **Firefox 103+**: Full support
- **Safari 9+**: Requires prefix

### Will-Change
- **All modern browsers**: Full support
- **Use sparingly**: Can cause memory issues

---

## Testing Checklist

### Visual Testing:
- [ ] Transitions feel smooth
- [ ] No janky animations
- [ ] Hover states work on all interactive elements
- [ ] Focus states visible for keyboard users
- [ ] Loading states communicate progress
- [ ] Page transitions feel natural

### Performance Testing:
- [ ] 60fps on desktop
- [ ] Acceptable on mobile
- [ ] No excessive repaints
- [ ] GPU usage reasonable
- [ ] Memory usage stable

### Accessibility Testing:
- [ ] Reduced motion respected
- [ ] Keyboard navigation smooth
- [ ] Focus indicators visible
- [ ] No vestibular triggers
- [ ] Screen reader compatible

### Cross-browser Testing:
- [ ] Chrome/Edge (Windows/Mac)
- [ ] Firefox (Windows/Mac)
- [ ] Safari (Mac/iOS)
- [ ] Mobile browsers (iOS Safari, Chrome Android)

---

## Performance Metrics

### Target Metrics:
- **Frame Rate**: 60fps consistent
- **Animation Duration**: < 300ms average
- **First Contentful Paint**: No delay from animations
- **Interaction Latency**: < 100ms perceived response

### Monitoring:
```javascript
// Chrome DevTools Performance tab
// Look for:
// - Green frames (60fps)
// - No layout thrashing
// - Minimal paint operations
```

---

## Future Enhancements

**Potential Additions:**
- Skeleton loaders for data tables
- Optimistic UI updates
- Swipe gestures (mobile)
- Drag & drop animations
- Toast notifications with motion
- Modal enter/exit transitions

**Principles to Maintain:**
- Keep it subtle
- Performance first
- Accessibility always
- Purpose over decoration

---

**Motion System Version**: 1.0.0  
**Design System Version**: 1.0.0  
**Last Updated**: 2026-09-09  
**Maintained By**: SIH26155 Team
