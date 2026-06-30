import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: "class",
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ["'Space Grotesk'", "sans-serif"],
        display: ["'DM Serif Display'", "serif"]
      },
      colors: {
        base: {
          950: "#0B1020",
          900: "#121B2E",
          800: "#1E2A44"
        },
        accent: {
          400: "#3ECF8E",
          500: "#2DBF7F",
          600: "#22A36B"
        },
        signal: {
          amber: "#F0B429",
          red: "#F66D6D",
          blue: "#38BDF8"
        }
      }
    }
  },
  plugins: []
};

export default config;
