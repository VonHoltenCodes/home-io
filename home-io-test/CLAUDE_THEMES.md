# Theme System Documentation

## Overview

The application uses a theme system that supports multiple visual styles. Currently implemented themes:

1. **Default** - Clean, modern interface
2. **Night** - Dark theme with green accents inspired by terminal displays
3. **Retro** - Orange accents with vintage computer aesthetics

## Theme Implementation

Themes are implemented using CSS variables and class-based selectors.

### CSS Variables

The root variables are defined in `/src/theme.css`:

```css
:root {
  --bg-primary: #121212;
  --bg-secondary: #1e1e1e;
  --border-color: #333;
  --text-primary: #f5f5f5;
  --text-secondary: #aaa;
  --accent-color: #42a5f5;
  --tile-hover-shadow: #0003;
}

.theme-night {
  --bg-primary: #000;
  --bg-secondary: #0a0a0a; 
  --border-color: #0f0;
  --text-primary: #0f0;
  --text-secondary: #0c0;
  --accent-color: #0f0;
  --tile-hover-shadow: #00ff004d;
  /* Additional night theme variables */
}

.theme-retro {
  --bg-primary: #111;
  --bg-secondary: #181818;
  --border-color: #ff4500;
  --text-primary: #ff4500;
  --text-secondary: #ff8c69;
  --accent-color: #ff4500;
  --tile-hover-shadow: #ff45004d;
  /* Additional retro theme variables */
}
```

### Theme Context

Theme state is managed through React Context in `/src/utils/ThemeContext.js`:

- `useTheme()` - Hook for accessing the current theme
- `setTheme()` - Function to change the current theme

## Component Theming

Components use conditional styling based on the current theme:

1. **CSS Class Approach**: Most components use CSS selectors like `.theme-retro .component-name`
2. **Inline Conditional Approach**: Some components use the theme value directly for dynamic styling

### Example:

```jsx
// In component
const { theme } = useTheme();
const buttonClass = theme === 'retro' ? 'retro-button' : 'modern-button';

// In CSS
.theme-retro .vu-meter {
  /* Retro-specific styling */
}
```

## Special Theme Elements

### Retro Theme

- VU Meters - Bouncing needle with orange glow
- Angular cut design elements using clip-path
- Retro font usage (VT323, Press Start 2P)
- Subtle scanline effects

### Night Theme

- Terminal-inspired green text
- Grid overlays
- Glowing effects
- Monospace fonts