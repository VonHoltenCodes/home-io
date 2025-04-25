# Styling Conventions

## CSS Organization

The project uses component-scoped CSS files with the following naming pattern:
- `ComponentName.css` - For each component's styles
- `theme.css` - For global theme variables and styles

## General Pattern

Each component has its own CSS file that follows this structure:

```
ComponentName.css
├── Base component styles
├── Child element styles
├── State-based styles (.active, .disabled, etc.)
├── Responsive media queries
└── Theme-specific styles (.theme-retro .component, etc.)
```

## CSS Class Naming

- Component root elements use kebab-case: `.device-tile`
- Child elements use descriptive names: `.device-tile-header`
- State modifiers use adjectives: `.active`, `.disabled`
- Theme variants use the theme name as a prefix on the root element: `.theme-retro body`

## Special Effects

### Retro Theme

1. **Clip-path** - Used for angular cut corners:
```css
.theme-retro .component {
  clip-path: polygon(
    0% 0%,
    100% 0%, 
    100% 85%,
    95% 100%,
    0% 100%
  );
}
```

2. **Text Shadows** - Used for glow effects:
```css
.theme-retro .component-label {
  text-shadow: 0 0 2px rgba(255, 102, 0, 0.6);
}
```

3. **Pseudo-elements** - Used for decorative elements:
```css
.theme-retro .component::before {
  content: 'LABEL';
  position: absolute;
  top: 5px;
  right: 10px;
  font-size: 10px;
}
```

### Night Theme

1. **Box Shadows** - Used for glow effects:
```css
.theme-night .component {
  box-shadow: inset 0 0 10px rgba(0, 0, 0, 0.8), 0 0 10px rgba(0, 255, 0, 0.1);
}
```

2. **Background Images** - Used for grid overlay:
```css
.theme-night body {
  background-image: var(--grid-overlay);
}
```

## Responsive Design

Media queries are used for responsive layouts:

```css
@media (max-width: 768px) {
  .component {
    flex-direction: column;
  }
}

@media (max-width: 480px) {
  .component {
    padding: 10px;
  }
}
```

## Animation Techniques

1. **CSS Transitions** - Used for smooth state changes:
```css
.component {
  transition: all 0.3s ease;
}
```

2. **CSS Animations** - Used for repeating effects:
```css
@keyframes blink {
  0%, 49% { opacity: 1; }
  50%, 100% { opacity: 0; }
}

.element {
  animation: blink 1s infinite;
}
```

3. **Canvas Animations** - Used for complex visualizations like VU meters

## Canvas Rendering Techniques

For components like RetroVUMeter, the project uses HTML5 Canvas:

1. **Get context** from canvas ref
2. **Clear canvas** on each animation frame
3. **Save and restore** context for transformations
4. Use **translate and rotate** for positioning elements
5. Apply **shadow effects** for glow
6. Use **gradient fills** for visual richness
7. Implement **animation loop** with requestAnimationFrame

Example from RetroVUMeter.js:
```javascript
// Set needle pivot point and rotation
ctx.save();
ctx.translate(width/2, height-10);
ctx.rotate((needleAngle * Math.PI) / 180);

// Orange glow effect
ctx.shadowColor = '#ff6600';
ctx.shadowBlur = 12;

// Draw the needle
ctx.fillStyle = needleGradient;
ctx.beginPath();
ctx.moveTo(-1, 0);
ctx.lineTo(1, 0);
ctx.lineTo(0.5, -needleLength);
ctx.lineTo(-0.5, -needleLength);
ctx.closePath();
ctx.fill();

ctx.restore();
```