/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'ui-monospace', 'monospace'],
      },
      colors: {
        brand: {
          50: '#eef6ff',
          100: '#d9ecff',
          200: '#bcdeff',
          300: '#8ec8ff',
          400: '#59a8ff',
          500: '#3385fc',
          600: '#1c66f2',
          700: '#1551df',
          800: '#1843b4',
          900: '#1a3c8e',
          950: '#142656',
        },
        ink: {
          50: '#f6f7f9',
          100: '#eceef2',
          200: '#d5dae2',
          300: '#b0bac9',
          400: '#8595ab',
          500: '#667891',
          600: '#526076',
          700: '#434e60',
          800: '#3a4251',
          900: '#343a46',
          950: '#22262e',
        },
      },
      boxShadow: {
        card: '0 1px 2px rgba(16,24,40,0.06), 0 1px 3px rgba(16,24,40,0.04)',
        'card-hover': '0 4px 12px rgba(16,24,40,0.08), 0 2px 6px rgba(16,24,40,0.05)',
      },
    },
  },
  plugins: [],
};
