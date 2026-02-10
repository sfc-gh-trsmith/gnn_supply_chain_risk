/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        snowflake: {
          blue: '#29B5E8',
          dark: '#0f172a',
        },
        risk: {
          critical: '#dc2626',
          high: '#ea580c',
          medium: '#f59e0b',
          low: '#10b981',
        }
      },
    },
  },
  plugins: [],
}
