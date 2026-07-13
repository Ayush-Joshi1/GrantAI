import type { Config } from "tailwindcss";

export default {
  darkMode: ["class"],
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: [
          "IBM Plex Sans",
          "ui-sans-serif",
          "system-ui",
          "-apple-system",
          "Segoe UI",
          "sans-serif"
        ]
      },
      colors: {
        ibm: {
          blue: "#0f62fe",
          "blue-dark": "#0043ce",
          cyan: "#1192e8",
          purple: "#6929c4",
          gray: {
            10: "#f4f4f4",
            50: "#878d96",
            90: "#21272a",
            100: "#161616"
          }
        }
      },
      boxShadow: {
        glass: "0 10px 30px rgba(0,0,0,0.35)",
        glow: "0 0 0 1px rgba(255,255,255,0.08), 0 12px 50px rgba(59,130,246,0.25)"
      },
      backdropBlur: {
        glass: "18px"
      },
      borderRadius: {
        xl2: "1.25rem"
      },
      keyframes: {
        shimmer: {
          "0%": { transform: "translateX(-40%)" },
          "100%": { transform: "translateX(120%)" }
        }
      },
      animation: {
        shimmer: "shimmer 1.4s ease-in-out infinite"
      }
    }
  },
  plugins: []
} satisfies Config;

