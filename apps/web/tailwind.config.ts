import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        navy: {
          deep: "#001f45",
          DEFAULT: "#003366",
          mid: "#004d99",
          light: "#e0eaf5",
        },
        gold: "#FFD700",
        "page-bg": "#f0f4f8",
        "user-row": "#f7f9fc",
        "chat-border": "#d0dae8",
        "disclaimer-bg": "#fef9e7",
        "disclaimer-border": "#f5d87a",
      },
    },
  },
  plugins: [],
};
export default config;
