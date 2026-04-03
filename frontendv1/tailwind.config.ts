import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}", "./lib/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: {
          50: "#f7f4ef",
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
        mist: "#dce5e2",
        ember: "#d86c3d",
        forest: "#1f3b36",
        paper: "#f6f1e8"
      },
      boxShadow: {
        panel: "0 20px 60px rgba(19, 22, 26, 0.12)"
      },
      fontFamily: {
        sans: ["Georgia", "Cambria", "\"Times New Roman\"", "serif"],
        display: ["Garamond", "Georgia", "serif"],
        mono: ["\"Courier New\"", "monospace"]
      }
    }
  },
  plugins: []
};

export default config;
