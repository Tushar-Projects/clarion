/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: ['./index.html', './src/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        glass: 'rgba(255,255,255,0.08)',
        ink: '#0a0a0a',
      },
      backdropBlur: { xl: "24px", '2xl': '40px' },
       boxShadow: {
        glass: "0 20px 40px rgba(0,0,0,0.15)",
         glow: "0 0 80px rgba(255,255,255,0.25)"
      },
    },
  },
  plugins: [],
};
