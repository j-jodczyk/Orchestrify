import type { Config } from "tailwindcss";

export default {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        roboto: ["Roboto", "sans-serif"],
      },
      colors: {
        text: {
          50: "#f2f2f2",
          100: "#e6e6e6",
          200: "#cccccc",
          300: "#b3b3b3",
          400: "#999999",
          500: "#808080",
          600: "#666666",
          700: "#4d4d4d",
          800: "#333333",
          900: "#1a1a1a",
          950: "#0d0d0d",
        },
        background: {
          50: "#edecf9",
          100: "#dad8f3",
          200: "#b5b1e7",
          300: "#908bda",
          400: "#6b64ce",
          500: "#463dc2",
          600: "#38319b",
          700: "#2a2574",
          800: "#1c184e",
          900: "#0e0c27",
          950: "#070613",
        },
        primary: {
          50: "#ecebfa",
          100: "#d9d6f5",
          200: "#b4aeea",
          300: "#8e85e0",
          400: "#695dd5",
          500: "#4334cb",
          600: "#362aa2",
          700: "#281f7a",
          800: "#1b1551",
          900: "#0d0a29",
          950: "#070514",
        },
        secondary: {
          50: "#f0eff5",
          100: "#e1e0eb",
          200: "#c3c0d8",
          300: "#a4a1c4",
          400: "#8682b0",
          500: "#68629d",
          600: "#534f7d",
          700: "#3e3b5e",
          800: "#2a273f",
          900: "#15141f",
          950: "#0a0a10",
        },
        accent: {
          50: "#fcefe9",
          100: "#f8ded3",
          200: "#f1bda7",
          300: "#ea9c7b",
          400: "#e37b4f",
          500: "#dd5a22",
          600: "#b0481c",
          700: "#843615",
          800: "#58240e",
          900: "#2c1207",
          950: "#160903",
        },
      },
    },
  },
  plugins: [],
} satisfies Config;
