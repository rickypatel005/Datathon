/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Stitch Precision Scientific Design Tokens
        "surface-container-lowest": "#060e20",
        "surface-container-low": "#131b2e",
        "surface-container": "#171f33",
        "surface-container-high": "#222a3d",
        "surface-container-highest": "#2d3449",
        "surface-dim": "#0b1326",
        "surface-bright": "#31394d",
        "surface-variant": "#2d3449",
        "on-surface": "#dae2fd",
        "on-surface-variant": "#c7c4d7",
        "inverse-surface": "#dae2fd",
        "inverse-on-surface": "#283044",
        "outline": "#908fa0",
        "outline-variant": "#464554",

        // Primary Indigo Accents
        "primary": "#8083ff",
        "primary-light": "#c0c1ff",
        "primary-container": "#494bd6",
        "on-primary": "#1000a9",
        "on-primary-container": "#e1e0ff",

        // Secondary Cyan Telemetry
        "secondary": "#7bd0ff",
        "secondary-container": "#00a6e0",
        "on-secondary": "#00354a",
        "on-secondary-container": "#00374d",

        // Tertiary Model Amethyst
        "tertiary": "#ddb7ff",
        "tertiary-container": "#b76dff",
        "on-tertiary": "#490080",
        "on-tertiary-container": "#400071",

        // Semantic Alerts
        "error": "#ffb4ab",
        "error-container": "#93000a",
        "on-error": "#690005",

        // Legacy compatibility
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        card: "hsl(var(--card))",
        "card-foreground": "hsl(var(--card-foreground))",
        border: "hsl(var(--border))",
        muted: "hsl(var(--muted))",
        "muted-foreground": "hsl(var(--muted-foreground))",
        accent: "hsl(var(--accent))",
        "accent-foreground": "hsl(var(--accent-foreground))",
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        display: ['Space Grotesk', 'sans-serif'],
        headline: ['Space Grotesk', 'sans-serif'],
        body: ['Inter', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      spacing: {
        "panel-padding": "1.25rem",
        "gutter-default": "1rem",
        "gutter-compact": "0.75rem",
      }
    },
  },
  plugins: [
    require('@tailwindcss/typography'),
  ],
}
