/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // TATVA pitch-black monochrome (reference: #1C1C1C matte black)
        'ink': {
          950: '#1C1C1C',
          900: '#1C1C1C',
          700: '#333333',
          500: '#6E6E6E',
        },
        'mist': {
          50: '#F7F7F8',
          100: '#EFEFEF',
          200: '#E2E2E2',
        },
        'line': '#D8D8D8',
        // Premium Light Theme Color System
        'brand': {
          50: '#f0f7ff',
          100: '#e0effe',
          200: '#b9ddfe',
          300: '#7cc4fd',
          400: '#36a7f9',
          500: '#0d8ae6',
          600: '#016dc5',
          700: '#0157a0',
          800: '#064a84',
          900: '#0b3e6d',
        },
        'surface': {
          DEFAULT: '#ffffff',
          secondary: '#f8f9fb',
          tertiary: '#f1f3f7',
          hover: '#e8ebf0',
        },
        'neutral': {
          50: '#fafbfc',
          100: '#f5f6f8',
          200: '#ebeef3',
          300: '#d8dce4',
          400: '#b4bac6',
          500: '#8a92a3',
          600: '#6c7489',
          700: '#525870',
          800: '#3a3f53',
          900: '#1f2937',
        },
        'status': {
          critical: {
            bg: '#fef2f2',
            border: '#fecaca',
            text: '#b91c1c',
            hover: '#fee2e2',
          },
          high: {
            bg: '#fff7ed',
            border: '#fed7aa',
            text: '#c2410c',
            hover: '#ffedd5',
          },
          medium: {
            bg: '#fefce8',
            border: '#fde68a',
            text: '#a16207',
            hover: '#fef9c3',
          },
          low: {
            bg: '#f0fdf4',
            border: '#bbf7d0',
            text: '#15803d',
            hover: '#dcfce7',
          },
          success: {
            bg: '#ecfdf5',
            border: '#a7f3d0',
            text: '#059669',
            hover: '#d1fae5',
          },
          info: {
            bg: '#eff6ff',
            border: '#bfdbfe',
            text: '#1d4ed8',
            hover: '#dbeafe',
          },
        },
      },
      boxShadow: {
        'sm-light': '0 1px 2px 0 rgba(0, 0, 0, 0.03)',
        'light': '0 1px 3px 0 rgba(0, 0, 0, 0.06), 0 1px 2px -1px rgba(0, 0, 0, 0.04)',
        'md-light': '0 4px 6px -1px rgba(0, 0, 0, 0.06), 0 2px 4px -2px rgba(0, 0, 0, 0.04)',
        'lg-light': '0 10px 15px -3px rgba(0, 0, 0, 0.06), 0 4px 6px -4px rgba(0, 0, 0, 0.04)',
        'xl-light': '0 20px 25px -5px rgba(0, 0, 0, 0.06), 0 8px 10px -6px rgba(0, 0, 0, 0.04)',
        // Glassmorphism shadows
        'glass': '0 8px 32px 0 rgba(0, 0, 0, 0.08)',
        'glass-sm': '0 4px 16px 0 rgba(0, 0, 0, 0.06)',
        'glass-lg': '0 16px 48px 0 rgba(0, 0, 0, 0.10)',
      },
      borderRadius: {
        '2xl': '1rem',
        '3xl': '1.5rem',
        '4xl': '2rem',
      },
    },
  },
  plugins: [],
}
