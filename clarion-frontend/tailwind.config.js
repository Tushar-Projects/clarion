/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html','./src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        // we’ll still compute colors dynamically in UI logic
      },
      boxShadow: {
        glass: '0 8px 32px rgba(31, 38, 135, 0.15)',
      },
      backdropBlur: {
        xs: '2px',
      }
    },
  },
  darkMode: 'class',
  plugins: [],
}

