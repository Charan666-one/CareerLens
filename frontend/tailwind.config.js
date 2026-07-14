export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "var(--ink)",
        "ink-raised": "var(--ink-raised)",
        "ink-line": "var(--ink-line)",
        "ink-text": "var(--ink-text)",
        "ink-text-dim": "var(--ink-text-dim)",

        stone: "var(--stone)",
        "stone-raised": "var(--stone-raised)",
        "stone-line": "var(--stone-line)",
        text: "var(--text)",
        "text-dim": "var(--text-dim)",

        brass: "rgb(var(--brass-rgb) / <alpha-value>)",
        "brass-strong": "var(--brass-strong)",
        good: "rgb(var(--good-rgb) / <alpha-value>)",
        warn: "rgb(var(--warn-rgb) / <alpha-value>)",
      },
      fontFamily: {
        display: ["Iowan Old Style", "Palatino Linotype", "Palatino", "Georgia", "serif"],
        body: ["Helvetica Neue", "Helvetica", "Arial", "sans-serif"],
        mono: ["ui-monospace", "SF Mono", "Menlo", "Consolas", "monospace"],
      },
      borderRadius: {
        DEFAULT: "3px",
      },
    },
  },
  plugins: [],
}
