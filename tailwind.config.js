/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        blood: {
          50:  '#fff1f1',
          100: '#ffe1e1',
          200: '#ffc9c9',
          300: '#ff9d9d',
          400: '#ff6262',
          500: '#ff2c2c',
          600: '#e74c3c',
          700: '#c0392b',
          800: '#9b2226',
          900: '#7b241c',
          950: '#450a0a',
        },
        crimson: '#c0392b',
        'blood-bright': '#e74c3c',
      },
      fontFamily: {
        heading: ['Figtree', 'system-ui', 'sans-serif'],
        body:    ['Noto Sans', 'system-ui', 'sans-serif'],
        mono:    ['JetBrains Mono', 'monospace'],
      },
      backgroundImage: {
        'hero-gradient': 'radial-gradient(ellipse 80% 50% at 50% -20%, rgba(192,57,43,0.18) 0%, transparent 70%)',
        'card-glass': 'linear-gradient(135deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.02) 100%)',
      },
      boxShadow: {
        'blood': '0 0 20px rgba(192,57,43,0.35)',
        'card': '0 4px 24px rgba(0,0,0,0.4)',
        'card-hover': '0 8px 40px rgba(0,0,0,0.55)',
        'glow-red': '0 0 30px rgba(231,76,60,0.4)',
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4,0,0.6,1) infinite',
        'float': 'float 6s ease-in-out infinite',
        'heartbeat': 'heartbeat 1.5s ease-in-out infinite',
      },
      keyframes: {
        float: {
          '0%,100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-10px)' },
        },
        heartbeat: {
          '0%,100%': { transform: 'scale(1)' },
          '14%': { transform: 'scale(1.1)' },
          '28%': { transform: 'scale(1)' },
          '42%': { transform: 'scale(1.1)' },
          '70%': { transform: 'scale(1)' },
        },
      },
    },
  },
  plugins: [],
}
