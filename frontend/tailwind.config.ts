import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: ["class"],
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        // Green Cast brand palette
        gc: {
          green:   "#2E7D32",  // forest green — primary
          teal:    "#0F766E",  // muted teal — accent
          red:     "#B91C1C",  // risk red — alerts only
          bg:      "#FAFAF7",  // off-white background
          text:    "#1F2937",  // charcoal text
          border:  "#E5E7EB",
          muted:   "#6B7280",
          surface: "#FFFFFF",
          dark:    "#0a1a0d",  // hero background — deep forest
        },
      },
      fontFamily: {
        sans:  ["Inter", "system-ui", "sans-serif"],
        mono:  ["JetBrains Mono", "Menlo", "monospace"],
      },
      borderRadius: {
        lg: "0.5rem",
        md: "0.375rem",
        sm: "0.25rem",
      },
      keyframes: {
        "pulse-risk": {
          "0%, 100%": {
            boxShadow: "0 0 0 0 rgba(185, 28, 28, 0)",
          },
          "50%": {
            boxShadow: "0 0 0 4px rgba(185, 28, 28, 0.18)",
          },
        },
        "fade-up": {
          "0%": {
            opacity: "0",
            transform: "translateY(16px)",
          },
          "100%": {
            opacity: "1",
            transform: "translateY(0)",
          },
        },
        "fade-in": {
          "0%":   { opacity: "0" },
          "100%": { opacity: "1" },
        },
        shimmer: {
          "0%":   { backgroundPosition: "-200% center" },
          "100%": { backgroundPosition: "200% center" },
        },
      },
      animation: {
        "pulse-risk": "pulse-risk 2.4s ease-in-out infinite",
        "fade-up":    "fade-up 0.5s ease-out both",
        "fade-in":    "fade-in 0.4s ease-out both",
        shimmer:      "shimmer 2s linear infinite",
      },
    },
  },
  plugins: [],
};

export default config;
