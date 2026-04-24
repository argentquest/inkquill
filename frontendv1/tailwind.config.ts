import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}", "./lib/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: {
          50:  "#f7f4ef",
          100: "#efe7db",
          200: "#dfcfb4",
          300: "#cfb28a",
          400: "#bd9560",
          500: "#a87a42",
          600: "#855f34",
          700: "#634829",
          800: "#43311f",
          900: "#231913"
        },
        mist:   "#dce5e2",
        ember:  "#d86c3d",
        forest: "#1f3b36",
        paper:  "#f6f1e8",
        "paper-2": "#efe7db",
        success: {
          bg:     "rgba(31,59,54,0.10)",
          fg:     "#1f3b36",
          border: "rgba(31,59,54,0.28)"
        },
        warning: {
          bg:     "rgba(216,108,61,0.12)",
          fg:     "#8b3a0f",
          border: "rgba(216,108,61,0.35)"
        },
        danger: {
          bg:     "rgba(198,83,83,0.12)",
          fg:     "#8b2222",
          border: "rgba(198,83,83,0.30)"
        },
        info: {
          bg:     "rgba(220,229,226,0.50)",
          fg:     "#1f3b36",
          border: "rgba(31,59,54,0.22)"
        }
      },
      fontFamily: {
        sans:    ["var(--font-sans)", "Lora", "Georgia", "Cambria", "serif"],
        display: ["var(--font-display)", "EB Garamond", "Garamond", "Georgia", "serif"],
        mono:    ["\"Courier New\"", "Courier", "monospace"]
      },
      borderRadius: {
        "2xl":  "20px",
        "3xl":  "24px",
        "4xl":  "28px",
        "5xl":  "32px"
      },
      boxShadow: {
        soft:  "0 2px 8px rgba(35,25,19,0.08)",
        panel: "0 20px 60px rgba(19,22,26,0.12)"
      }
    }
  },
  plugins: []
};

export default config;
