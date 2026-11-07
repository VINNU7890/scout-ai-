/** @type {import('tailwindcss').Config} */
export default {
  darkMode: "class",
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        dark: {
          bg: "#0B0D12",
          surface: "#12151C",
          elevated: "#181C25",
          border: "rgba(255, 255, 255, 0.08)",
          subtle: "rgba(255, 255, 255, 0.04)",
        },
        light: {
          bg: "#F7F8FA",
          surface: "#FFFFFF",
          elevated: "#F1F3F7",
          border: "rgba(0, 0, 0, 0.08)",
          subtle: "rgba(0, 0, 0, 0.03)",
        },
        primary: {
          DEFAULT: "#6366F1",
          hover: "#4F46E5",
          accent: "#8B5CF6",
        },
        success: {
          DEFAULT: "#14B8A6",
          light: "#CCFBF1",
          dark: "#0F766E",
        },
        warning: {
          DEFAULT: "#F59E0B",
          light: "#FEF3C7",
          dark: "#B45309",
        },
      },
      fontFamily: {
        sans: ["Inter", "-apple-system", "BlinkMacSystemFont", "Segoe UI", "Roboto", "sans-serif"],
        mono: ["JetBrains Mono", "SFMono-Regular", "Menlo", "Monaco", "Consolas", "monospace"],
      },
      borderRadius: {
        xl: "14px",
        "2xl": "16px",
      },
      animation: {
        "pulse-slow": "pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite",
        "live-glow": "glow 2s ease-in-out infinite alternate",
      },
      keyframes: {
        glow: {
          "0%": { boxShadow: "0 0 5px rgba(99, 102, 241, 0.4)" },
          "100%": { boxShadow: "0 0 15px rgba(139, 92, 246, 0.8)" },
        },
      },
    },
  },
  plugins: [],
};
