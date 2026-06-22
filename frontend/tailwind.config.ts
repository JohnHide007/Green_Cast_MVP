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
    },
  },
  plugins: [],
};

export default config;
