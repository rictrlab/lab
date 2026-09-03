/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class',
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./lib/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        rictr: {
          bg: "#fafafa",
          card: "#ffffff",
          border: "#e4e4e7",
          accent: "#000000",
          muted: "#71717a",
        },
      },
    },
  },
  plugins: [],
};
