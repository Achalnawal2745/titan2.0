# Design System Checklist

Complete checklist for establishing a cohesive design system during UX overhauls.

## Color Palette

### Primary Colors
- [ ] **Background** - Main page background color (e.g., `#0a1628` navy)
- [ ] **Foreground** - Main text color (e.g., `#ffffff` white)
- [ ] **Primary** - Brand accent color (e.g., `#00d4ff` electric blue)
- [ ] **Secondary** - Supporting accent color (optional)

### Semantic Colors
- [ ] **Card Background** - Card/panel background (e.g., `#1a2942`)
- [ ] **Border** - Divider and border color
- [ ] **Muted** - Secondary text color
- [ ] **Success** - Positive actions/states (green)
- [ ] **Warning** - Caution states (yellow/orange)
- [ ] **Error** - Destructive actions/errors (red)

### Color Format
- Use HSL for light/dark theme compatibility
- Use hex codes for fixed brand colors
- Document color tokens in `lib/design-tokens.ts`

## Typography

### Font Families
- [ ] **Primary Font** - Body text font (e.g., Inter, Roboto, Open Sans)
- [ ] **Heading Font** - Optional display font for headings
- [ ] **Monospace Font** - Code/technical content (e.g., Fira Code, JetBrains Mono)

### Font Loading
- [ ] Google Fonts CDN link in `index.html` OR
- [ ] Self-hosted fonts in `public/fonts/`
- [ ] Font display strategy (swap, fallback, optional)

### Type Scale
- [ ] **Base size** - 16px (1rem) for body text
- [ ] **Headings** - h1 (2.5rem), h2 (2rem), h3 (1.5rem), h4 (1.25rem)
- [ ] **Small text** - 0.875rem for captions, labels
- [ ] **Line height** - 1.5 for body, 1.2 for headings

## Spacing System

### Scale
- [ ] **Base unit** - 4px or 8px
- [ ] **Scale** - 0.5, 1, 2, 3, 4, 6, 8, 12, 16, 24, 32, 48, 64 (multiples of base)
- [ ] **Container padding** - Responsive (px-4 sm:px-6 lg:px-8)

### Layout
- [ ] **Max width** - Container max-width (e.g., 1280px, 1440px)
- [ ] **Gutter** - Gap between columns (e.g., 1rem, 1.5rem)
- [ ] **Section spacing** - Vertical spacing between major sections

## Shadows & Effects

### Shadows
- [ ] **Card shadow** - Subtle elevation (e.g., `0 4px 6px rgba(0, 0, 0, 0.1)`)
- [ ] **Glow effect** - Brand-colored glow (e.g., `0 0 20px rgba(0, 212, 255, 0.3)`)
- [ ] **Hover shadow** - Interactive element hover state

### Effects
- [ ] **Backdrop blur** - Glassmorphism effect (e.g., `backdrop-blur-sm`)
- [ ] **Transitions** - Duration (150ms, 300ms) and easing (ease-in-out)
- [ ] **Border radius** - Consistent rounding (e.g., 0.5rem, 0.75rem)

## Components

### Buttons
- [ ] **Primary** - Main CTA button styling
- [ ] **Secondary** - Alternative action styling
- [ ] **Outline** - Tertiary action styling
- [ ] **Ghost** - Minimal action styling
- [ ] **Sizes** - sm, md (default), lg
- [ ] **States** - Hover, active, disabled, loading

### Cards
- [ ] **Base card** - Background, padding, border radius
- [ ] **Card header** - Title, subtitle, actions
- [ ] **Card content** - Body content padding
- [ ] **Card footer** - Actions, metadata

### Navigation
- [ ] **Top nav** - Fixed header with logo, user menu
- [ ] **Bottom nav** - Mobile tab bar (if applicable)
- [ ] **Sidebar** - Desktop navigation (if applicable)
- [ ] **Active state** - Highlight for current page

### Forms
- [ ] **Input fields** - Text, number, email, password
- [ ] **Select dropdowns** - Single and multi-select
- [ ] **Checkboxes** - Boolean inputs
- [ ] **Radio buttons** - Single choice from options
- [ ] **Validation** - Error states and messages

## CSS Variables

### Implementation
- [ ] Define variables in `index.css` under `:root` and `.dark`
- [ ] Use semantic names (`--background`, `--foreground`, `--primary`)
- [ ] Support light/dark theme switching
- [ ] Document all variables in design tokens file

### Example Structure
```css
:root {
  --background: 222.2 84% 4.9%; /* HSL for dark navy */
  --foreground: 210 40% 98%;
  --primary: 190 100% 50%; /* Electric blue */
  --card: 222.2 47.4% 11.2%;
  --border: 217.2 32.6% 17.5%;
}
```

## Utilities

### Custom Utilities
- [ ] `.container` - Auto-center with responsive padding
- [ ] `.card` - Card styling with glow effect
- [ ] `.glow-blue` - Brand-colored glow effect
- [ ] `.flex` - Flex with min-width/min-height: 0

### Tailwind Extensions
- [ ] Extend theme in `tailwind.config.js`
- [ ] Add custom colors, spacing, fonts
- [ ] Configure plugins (forms, typography, etc.)

## Accessibility

### Color Contrast
- [ ] **Text on background** - Minimum 4.5:1 ratio
- [ ] **Large text** - Minimum 3:1 ratio
- [ ] **Interactive elements** - Clear focus states

### Keyboard Navigation
- [ ] All interactive elements focusable
- [ ] Visible focus rings (not removed)
- [ ] Logical tab order

### Screen Readers
- [ ] Semantic HTML (nav, main, aside, footer)
- [ ] ARIA labels where needed
- [ ] Alt text for images

## Responsive Design

### Breakpoints
- [ ] **Mobile** - Default (< 640px)
- [ ] **Tablet** - sm: 640px
- [ ] **Desktop** - md: 768px, lg: 1024px
- [ ] **Large** - xl: 1280px, 2xl: 1536px

### Mobile-First Approach
- [ ] Design for mobile first
- [ ] Progressive enhancement for larger screens
- [ ] Touch-friendly targets (min 44x44px)

## Brand Assets

### Logo
- [ ] **Primary logo** - Full color version
- [ ] **Logo variants** - Dark/light backgrounds
- [ ] **Favicon** - 16x16, 32x32, 192x192, 512x512

### Images
- [ ] **Hero images** - High-quality, on-brand
- [ ] **Icons** - Consistent style (outline, solid, custom)
- [ ] **Illustrations** - Optional decorative elements

## Documentation

### Files to Create/Update
- [ ] `client/src/index.css` - Global styles and CSS variables
- [ ] `client/src/lib/design-tokens.ts` - TypeScript color constants
- [ ] `client/index.html` - Font CDN links
- [ ] `tailwind.config.js` - Theme extensions
- [ ] `README.md` - Design system documentation

### Design Tokens File Example
```typescript
export const colors = {
  background: '#0a1628',
  foreground: '#ffffff',
  primary: '#00d4ff',
  card: '#1a2942',
  border: '#2a3f5f',
};

export const archetypeColors = {
  lamb: '#10b981', // green
  bull: '#ef4444', // red
  tiger: '#f59e0b', // orange
  owl: '#3b82f6', // blue
};
```

## Verification Checklist

- [ ] All colors defined in CSS variables
- [ ] Font loaded and applied globally
- [ ] Spacing system consistent across pages
- [ ] Shadows and effects applied to cards
- [ ] Navigation styled with active states
- [ ] Forms have validation states
- [ ] Responsive at all breakpoints
- [ ] Accessibility requirements met
- [ ] TypeScript compiles without errors
- [ ] No console warnings in browser
