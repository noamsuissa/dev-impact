/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        terminal: {
          bg: '#2d2d2d',
          'bg-light': '#2a2a2a',
          'bg-lighter': '#3a3a3a',
          border: '#5a5a5a',
          text: '#e8e6e3',
          'text-dim': '#c9c5c0',
          gray: '#999999',
          orange: '#ff8c42',
          'orange-dark': '#cc6f35',
          'orange-light': '#ffaa66',
          green: '#4ade80',
        },
      },
      fontFamily: {
        mono: ['JetBrains Mono', 'Courier New', 'monospace'],
      },
    },
  },
  plugins: [],
}

