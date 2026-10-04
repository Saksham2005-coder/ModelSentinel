/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: {
          primary: '#0a0a0b',
          secondary: '#121214',
          elevated: '#1a1a1d',
          surface: '#242428',
          hover: '#2d2d32',
          overlay: 'rgba(0, 0, 0, 0.6)',
        },
        text: {
          primary: '#f8f8f8',
          secondary: '#a1a1aa',
          muted: '#71717a',
          disabled: '#52525b',
        },
        border: {
          default: '#27272a',
          subtle: '#18181b',
          focus: '#3b82f6',
        },
        brand: {
          primary: '#3b82f6',
          secondary: '#8b5cf6',
          accent: '#06b6d4',
        },
        status: {
          success: '#10b981',
          warning: '#f59e0b',
          danger: '#ef4444',
          info: '#3b82f6',
        },
        chart: {
          production: '#3b82f6',
          baseline: '#8b5cf6',
          validation: '#10b981',
          incident: '#ef4444',
          drift: '#f59e0b',
          comparison: '#06b6d4',
        },
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
    },
  },
  plugins: [],
}
