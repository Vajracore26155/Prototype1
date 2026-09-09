# Glassmorphism Visual Language Guide
## Sophisticated & Restrained Glass Effects

This document outlines the glassmorphism design system applied selectively throughout the interface to create premium visual depth while maintaining excellent readability.

---

## Design Philosophy

**Core Principle:** Glassmorphism is used **selectively and purposefully**, not everywhere.

### Where Glass is Applied:
✅ Important KPI cards (hero metrics)  
✅ Header/navigation (floating feel)  
✅ Status badges (System Active)  
✅ Alert banners (elevated importance)  
✅ Risk analysis cards (visual richness)  
✅ Upload dropzone (interactive surface)  
✅ Icon backgrounds (depth treatment)  
✅ Success/error messages (contextual elevation)  

### Where Glass is NOT Applied:
❌ Regular content cards  
❌ Simple lists  
❌ Table rows  
❌ Footer  
❌ Standard buttons  
❌ Body text containers  

---

## Glass Effect Components

### 1. Card Glass (`.card-glass`)
**Usage:** Important cards, secondary KPIs, interactive surfaces

**Properties:**
```css
background: rgba(255, 255, 255, 0.80)
backdrop-filter: blur(12px)
border: 1px solid rgba(255, 255, 255, 0.60)
box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.08)
border-radius: 1rem (16px)
```

**Hover State:**
```css
box-shadow: 0 16px 48px 0 rgba(0, 0, 0, 0.10)
transform: translateY(-2px)
transition: all 300ms
```

**When to Use:**
- Secondary KPI cards (Configurations, Audits Run)
- Upload area container
- Highlighted content blocks

---

### 2. Panel Glass (`.panel-glass`)
**Usage:** Floating panels, modals, dropdowns

**Properties:**
```css
background: rgba(255, 255, 255, 0.90)
backdrop-filter: blur(12px)
border: 1px solid rgba(255, 255, 255, 0.70)
box-shadow: 0 16px 48px 0 rgba(0, 0, 0, 0.10)
border-radius: 1.5rem (24px)
```

**When to Use:**
- Modal overlays
- Dropdown menus
- Floating action panels
- Sidebar panels

---

### 3. Elevated Glass (`.elevated-glass`)
**Usage:** Alert banners, important notifications

**Properties:**
```css
background: rgba(255, 255, 255, 0.85)
backdrop-filter: blur(12px)
border: 1px solid rgba(255, 255, 255, 0.60)
box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.08)
border-radius: 1rem (16px)
```

**When to Use:**
- Critical alert banner
- Human review required banner
- System notifications
- Important status messages

---

### 4. Header Glass (`.header-glass`)
**Usage:** Top navigation header

**Properties:**
```css
background: rgba(255, 255, 255, 0.95)
backdrop-filter: blur(12px)
border-bottom: 1px solid rgba(255, 255, 255, 0.60)
box-shadow: 0 4px 16px 0 rgba(0, 0, 0, 0.06)
position: sticky
top: 0
z-index: 50
```

**Why:**
- Creates floating navigation feel
- Maintains header legibility
- Subtle elevation without weight
- Modern SaaS aesthetic

---

### 5. Floating Glass (`.floating-glass`)
**Usage:** CTAs, quick action cards

**Properties:**
```css
background: rgba(255, 255, 255, 0.90)
backdrop-filter: blur(12px)
border: 1px solid rgba(255, 255, 255, 0.70)
box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.08)
border-radius: 1rem (16px)
```

**Hover State:**
```css
box-shadow: 0 16px 48px 0 rgba(0, 0, 0, 0.10)
transform: translateY(-4px)
transition: all 300ms
```

**When to Use:**
- Quick action cards
- Floating CTAs
- Interactive tiles

---

## Shadow System

### Glass Shadows (Soft & Diffused)

```css
shadow-glass-sm:  0 4px 16px 0 rgba(0, 0, 0, 0.06)
shadow-glass:     0 8px 32px 0 rgba(0, 0, 0, 0.08)
shadow-glass-lg:  0 16px 48px 0 rgba(0, 0, 0, 0.10)
```

### Standard Shadows (Non-Glass)

```css
shadow-sm-light:  0 1px 2px 0 rgba(0, 0, 0, 0.03)
shadow-light:     0 1px 3px 0 rgba(0, 0, 0, 0.06), 0 1px 2px -1px rgba(0, 0, 0, 0.04)
shadow-md-light:  0 4px 6px -1px rgba(0, 0, 0, 0.06), 0 2px 4px -2px rgba(0, 0, 0, 0.04)
shadow-lg-light:  0 10px 15px -3px rgba(0, 0, 0, 0.06), 0 4px 6px -4px rgba(0, 0, 0, 0.04)
shadow-xl-light:  0 20px 25px -5px rgba(0, 0, 0, 0.06), 0 8px 10px -6px rgba(0, 0, 0, 0.04)
```

### Usage Guidelines:
- **Glass shadows**: Use with glass effects (softer, larger)
- **Standard shadows**: Use with solid cards (sharper, smaller)
- **Hover states**: Increase shadow size + translate element up
- **Never mix**: Don't use glass shadows on non-glass elements

---

## Backdrop Blur

```css
backdrop-blur-xs:    2px  (minimal blur)
backdrop-blur-glass: 12px (glass effect)
backdrop-blur-lg:    16px (strong glass)
```

### Implementation:
```css
backdrop-filter: blur(12px);
-webkit-backdrop-filter: blur(12px); /* Safari support */
```

### Browser Support:
- Chrome/Edge: Full support
- Firefox: Full support
- Safari: Requires `-webkit-` prefix
- Fallback: Semi-transparent background still visible

---

## Border Treatment

### Glass Borders
```css
border: 1px solid rgba(255, 255, 255, 0.60)  /* Standard glass */
border: 1px solid rgba(255, 255, 255, 0.70)  /* Panel glass */
border: 2px solid rgba(border-color, 0.60)   /* Status glass */
```

### Principles:
- Always translucent (never fully opaque)
- Subtle definition without harsh edges
- Lighter borders on lighter backgrounds
- Status borders maintain color but reduce opacity

---

## Border Radius System

```css
rounded-lg:   0.5rem   (8px)   - Buttons, controls
rounded-xl:   0.75rem  (12px)  - Small cards
rounded-2xl:  1rem     (16px)  - Standard cards, glass cards
rounded-3xl:  1.5rem   (24px)  - Large containers, panels
rounded-4xl:  2rem     (32px)  - Hero sections
```

### Usage:
- **Buttons**: `rounded-lg`
- **Cards**: `rounded-2xl`
- **Panels**: `rounded-3xl`
- **Icon backgrounds**: `rounded-xl` to `rounded-3xl`
- **Badge/pills**: `rounded-md` to `rounded-lg`

### Avoid:
- Excessive rounding (not every element needs to be circular)
- Inconsistent radius (stick to system values)
- Too sharp corners on glass elements

---

## Gradient Backgrounds with Glass

### Hero Compliance Card
```css
background: linear-gradient(to bottom right, rgba(255,255,255,0.90), rgba(240,247,255,0.80))
backdrop-filter: blur(12px)
border: 1px solid rgba(255,255,255,0.60)
```

### Risk Severity Cards
```css
/* Critical */
background: linear-gradient(to bottom right, rgba(254,242,242,0.80), rgba(255,255,255,0.90))

/* High */
background: linear-gradient(to bottom right, rgba(255,247,237,0.80), rgba(255,255,255,0.90))

/* Medium */
background: linear-gradient(to bottom right, rgba(254,252,232,0.80), rgba(255,255,255,0.90))

/* Low */
background: linear-gradient(to bottom right, rgba(240,253,244,0.80), rgba(255,255,255,0.90))
```

### Principles:
- Gradient from status color → white
- Maintain transparency (0.80 to 0.90)
- Combine with backdrop-blur
- Subtle, not dramatic

---

## Hover & Interactive States

### Glass Card Hover
```css
.card-glass:hover {
  box-shadow: 0 16px 48px 0 rgba(0, 0, 0, 0.10);
  transform: translateY(-2px);
  transition: all 300ms ease-out;
}
```

### Risk Card Hover
```css
.risk-card:hover {
  box-shadow: 0 16px 48px 0 rgba(0, 0, 0, 0.10);
  transform: translateY(-4px);
  transition: all 300ms ease-out;
}
```

### Floating Action Hover
```css
.floating-glass:hover {
  box-shadow: 0 16px 48px 0 rgba(0, 0, 0, 0.10);
  transform: translateY(-4px);
  transition: all 300ms ease-out;
}
```

### Principles:
- **Subtle translation**: -2px to -4px (not -10px+)
- **Shadow elevation**: Increase shadow spread
- **Smooth transition**: 200-300ms
- **No dramatic scaling**: Avoid scale(1.05)

---

## Visual Depth Layers

```
Layer 6: Modals            (shadow-glass-lg, high z-index)
Layer 5: Floating Elements (shadow-glass, translate-y)
Layer 4: Elevated Cards    (elevated-glass, shadow-glass)
Layer 3: Glass Cards       (card-glass, shadow-glass)
Layer 2: Standard Cards    (card, shadow-light)
Layer 1: Surface           (bg-white)
Layer 0: Background        (bg-neutral-50)
```

### Implementation:
- Each layer has distinct shadow + blur
- Higher layers have stronger blur
- Maintain logical stacking
- Use z-index appropriately

---

## Readability & Contrast

### Text on Glass Surfaces

✅ **Good Contrast:**
```css
/* Dark text on light glass */
color: #1f2937 (neutral-900) on rgba(255,255,255,0.80)

/* Status text on status glass */
color: #b91c1c (critical-text) on rgba(254,242,242,0.80)
```

❌ **Avoid:**
```css
/* Light text on light glass (poor contrast) */
color: #d1d5db on rgba(255,255,255,0.80)

/* Pure white text on glass (harsh) */
color: #ffffff on rgba(255,255,255,0.90)
```

### Contrast Requirements:
- Body text: Minimum 4.5:1 (WCAG AA)
- Large text (18px+): Minimum 3:1
- Interactive elements: Minimum 3:1

### Testing:
- View on different backgrounds
- Test with backdrop content visible
- Ensure KPI numbers remain highly readable
- Verify status colors maintain meaning

---

## Background Pattern (Subtle)

### Radial Gradient Overlay
```css
body::before {
  content: '';
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: 
    radial-gradient(circle at 20% 50%, rgba(1, 109, 197, 0.03) 0%, transparent 50%),
    radial-gradient(circle at 80% 80%, rgba(1, 109, 197, 0.02) 0%, transparent 50%);
  pointer-events: none;
  z-index: 0;
}
```

### Purpose:
- Adds subtle visual interest
- Creates depth without distraction
- Complements glass effects
- Brand color integration (very subtle)

### Opacity:
- 0.02 to 0.03 (barely visible)
- Should not interfere with content
- Enhances glass effect perception

---

## Icon Backgrounds with Glass

### Small Icon Containers
```css
padding: 0.75rem (12px)
background: rgba(255, 255, 255, 0.80)
backdrop-filter: blur(2px)
border: 1px solid rgba(255, 255, 255, 0.60)
border-radius: 0.75rem (12px)
box-shadow: 0 4px 16px 0 rgba(0, 0, 0, 0.06)
```

### Medium Icon Containers
```css
padding: 1rem (16px)
background: rgba(255, 255, 255, 0.90)
backdrop-filter: blur(2px)
border: 1px solid rgba(255, 255, 255, 0.60)
border-radius: 1rem (16px)
box-shadow: 0 4px 16px 0 rgba(0, 0, 0, 0.06)
```

### Usage:
- Header logo background
- System Active badge background
- Alert icon backgrounds
- KPI icon containers (optional)

---

## Status Messages with Glass

### Success Message
```css
background: rgba(236, 253, 245, 0.80)
backdrop-filter: blur(12px)
border: 2px solid rgba(167, 243, 208, 0.60)
```

### Error Message
```css
background: rgba(254, 242, 242, 0.80)
backdrop-filter: blur(12px)
border: 2px solid rgba(254, 202, 202, 0.60)
```

### Warning Message
```css
background: rgba(254, 252, 232, 0.80)
backdrop-filter: blur(12px)
border: 2px solid rgba(253, 230, 138, 0.60)
```

---

## Performance Considerations

### Backdrop Filter Performance
- **Good:** Used sparingly on key elements
- **Bad:** Applied to hundreds of elements
- **Optimization:** Limit blur to visible viewport

### Best Practices:
1. Use glass effects on < 20 elements per page
2. Avoid animating `backdrop-filter`
3. Use `will-change: transform` for hover effects
4. Test on lower-end devices
5. Provide fallback without blur

### Fallback Strategy:
```css
.card-glass {
  background: rgba(255, 255, 255, 0.95); /* More opaque fallback */
  backdrop-filter: blur(12px);
}

@supports not (backdrop-filter: blur(12px)) {
  .card-glass {
    background: rgba(255, 255, 255, 1); /* Solid fallback */
  }
}
```

---

## Implementation Examples

### Dashboard Hero KPI
```tsx
<div className="lg:col-span-2 card-glass bg-gradient-to-br from-white/90 to-brand-50/80 border-white/60">
  {/* Content */}
</div>
```

### Secondary KPI Cards
```tsx
<div className="card-glass">
  {/* Content */}
</div>
```

### Alert Banner
```tsx
<div className="elevated-glass border-2 border-status-critical-border/60 bg-status-critical-bg/70 p-6">
  {/* Content */}
</div>
```

### Icon Background
```tsx
<div className="p-4 bg-white/90 backdrop-blur-sm rounded-2xl shadow-glass-sm border border-white/60">
  <CheckCircle className="w-10 h-10 text-brand-600" />
</div>
```

### Risk Severity Card
```tsx
<div className="rounded-2xl border-2 border-status-critical-border/60 bg-gradient-to-br from-status-critical-bg/80 to-white/90 backdrop-blur-glass p-6 hover:shadow-glass-lg hover:translate-y-[-4px]">
  {/* Content */}
</div>
```

---

## Do's and Don'ts

### ✅ Do:
- Use glass selectively for emphasis
- Maintain excellent text contrast
- Apply consistent shadow system
- Test on multiple backgrounds
- Combine with subtle gradients
- Use appropriate border radius
- Implement smooth transitions
- Provide fallbacks

### ❌ Don't:
- Apply glass to every element
- Use excessive blur (>16px)
- Create low-contrast text
- Mix glass and non-glass shadows
- Over-animate hover states
- Use harsh borders
- Forget browser prefixes
- Sacrifice readability for aesthetics

---

## Browser Compatibility

### Backdrop Filter Support
- **Chrome/Edge 76+**: Full support
- **Firefox 103+**: Full support
- **Safari 9+**: Requires `-webkit-` prefix
- **iOS Safari 9+**: Requires `-webkit-` prefix

### Implementation:
```css
.glass-element {
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
}
```

### Graceful Degradation:
- Fallback to higher opacity backgrounds
- Maintain visual hierarchy
- Ensure readability without blur

---

## Testing Checklist

### Visual Testing:
- [ ] Glass effects visible but subtle
- [ ] Text remains highly readable
- [ ] Hover states work smoothly
- [ ] Shadow depths appear natural
- [ ] Gradients blend seamlessly
- [ ] Borders define edges clearly

### Cross-browser Testing:
- [ ] Chrome (Windows/Mac)
- [ ] Firefox (Windows/Mac)
- [ ] Safari (Mac/iOS)
- [ ] Edge (Windows)

### Performance Testing:
- [ ] No jank on scroll
- [ ] Smooth hover transitions
- [ ] Acceptable on mobile devices
- [ ] No layout shift

### Accessibility Testing:
- [ ] All text meets contrast ratios
- [ ] Focus states visible
- [ ] Screen reader compatible
- [ ] Keyboard navigation works

---

## Migration from Solid Cards

### Before (Solid Card):
```tsx
<div className="card">
  {/* Content */}
</div>
```

### After (Glass Card):
```tsx
<div className="card-glass">
  {/* Content */}
</div>
```

### When to Migrate:
- Important KPI cards → `card-glass`
- Hero sections → Add gradient + glass
- Alert banners → `elevated-glass`
- Interactive cards → `floating-glass`
- Status messages → Add glass + backdrop

### When NOT to Migrate:
- Standard content cards
- List items
- Table rows
- Footer sections
- Simple containers

---

## Maintenance Guidelines

### Adding New Glass Components:
1. Identify if glass effect is appropriate
2. Choose correct glass variant
3. Ensure text contrast is maintained
4. Test hover/interactive states
5. Verify cross-browser compatibility
6. Document the component

### Updating Existing Glass:
1. Check contrast ratios
2. Test performance impact
3. Verify consistency with system
4. Update documentation if pattern changes

---

**Glassmorphism Version**: 1.0.0  
**Design System Version**: 1.0.0  
**Last Updated**: 2026-09-09  
**Maintained By**: SIH26155 Team


---

## Navigation Components

### Back Button (`.BackButton`)

**Usage:** Professional back navigation control for page hierarchy

**Component Path:** `src/components/BackButton.tsx`

**Properties:**
```tsx
interface BackButtonProps {
  to?: string;        // Optional: specific route to navigate to
  label?: string;     // Optional: button label (default: "Back")
  className?: string; // Optional: additional CSS classes
}
```

**Styling:**
```css
background: rgba(255, 255, 255, 0.70)
backdrop-filter: blur(2px)
border: 1px solid rgba(156, 163, 175, 0.80)
color: rgb(55, 65, 81) /* neutral-700 */
font-weight: 500
padding: 0.5rem 0.75rem (8px 12px)
border-radius: 0.5rem (8px)
```

**Hover State:**
```css
background: rgba(255, 255, 255, 0.90)
border: 1px solid rgb(209, 213, 219) /* neutral-300 */
color: rgb(17, 24, 39) /* neutral-900 */
box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.03)
transform: none
```

**Active State:**
```css
transform: scale(0.97)
```

**Focus State:**
```css
outline: none
ring: 2px solid rgb(1, 109, 197) /* brand-500 */
ring-offset: 2px
```

**Icon Behavior:**
- Arrow left icon (16px)
- Subtle slide left animation on hover (-2px translateX)
- Smooth 200ms transition

**Navigation Logic:**
1. If `to` prop provided: Navigate to specific route (logical parent)
2. If no `to` prop: Use browser history with fallback
3. Fallback to `/dashboard` if no history available (direct entry)

**When to Use:**
- Top-left of Upload page → Dashboard
- Top-left of Configurations page → Dashboard
- Top-left of Audit Results page → Configurations
- Any detail page requiring backward navigation

**Best Practices:**
- Always provide `to` prop for logical parent navigation
- Use descriptive labels (e.g., "Dashboard", "Configurations")
- Position consistently at top-left above page title
- Include appropriate spacing (space-x-3, mb-2)

**Accessibility:**
- Proper `aria-label` for screen readers
- Keyboard focusable
- Visible focus indicator
- Semantic button element

**Responsive Behavior:**
- Works identically on all screen sizes
- Touch-friendly tap target (minimum 44x44px)
- No layout shifts on different viewports

**Implementation Example:**
```tsx
import BackButton from '../components/BackButton';

// With logical parent route
<BackButton to="/dashboard" label="Dashboard" />

// With browser history
<BackButton label="Back" />

// With custom styling
<BackButton to="/configurations" label="Configurations" className="mb-4" />
```

**Page Integration Pattern:**
```tsx
<div className="space-y-8 page-enter">
  <div className="flex items-start justify-between gap-4">
    <div className="flex-1">
      <div className="flex items-center space-x-3 mb-2">
        <BackButton to="/parent-route" label="Parent Page" />
      </div>
      <h1 className="text-3xl font-bold mb-2 text-neutral-900">Current Page</h1>
      <p className="text-neutral-600">Page description</p>
    </div>
    {/* Optional: Action buttons on the right */}
  </div>
  {/* Rest of page content */}
</div>
```

**Navigation Hierarchy:**
```
Dashboard (/)
├── Upload (/upload)
│   └── Back → Dashboard
├── Configurations (/configurations)
│   └── Back → Dashboard
│   └── Audit Results (/audit/:id)
│       └── Back → Configurations
```

**Design Rationale:**
- **Subtle:** Glass effect provides depth without visual dominance
- **Professional:** Clean typography and consistent spacing
- **Compact:** Small footprint, doesn't overwhelm content
- **Recognizable:** Arrow icon with clear label
- **Consistent:** Matches glassmorphism design system
- **Non-intrusive:** Positioned naturally, not visually dominant

**Browser Compatibility:**
- All modern browsers support backdrop-filter
- Fallback to higher opacity background works seamlessly
- Arrow animation uses standard transforms

**Performance:**
- Minimal backdrop-blur (2px) for performance
- Single element, no nested complexity
- CSS transitions hardware-accelerated
- No layout recalculation on hover

---

**Back Button Version**: 1.0.0  
**Component Added**: 2026-09-09  
**Integrated Pages**: Upload, Configurations, AuditResults
