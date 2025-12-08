/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: ["light", "dark"],
  },
  plugins: [
    require("daisyui"), "@tailwindcss/postcss", "postcss-import"
  ],
}
