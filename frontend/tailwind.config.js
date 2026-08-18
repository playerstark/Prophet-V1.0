export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        gold: {
          50: '#fefef5',
          100: '#fdfce8',
          300: '#faf77d',
          500: '#d4af37',
          700: '#997f1a',
        },
        charcoal: {
          900: '#1a1a1a',
          800: '#2d2d2d',
          700: '#404040',
        },
      },
    },
  },
  plugins: [],
}
