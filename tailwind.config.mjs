/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{astro,html,js,jsx,md,mdx,svelte,ts,tsx,vue}'],
  theme: {
    extend: {
      colors: {
        pet: {
          50: '#F0FDFA',
          100: '#CCFBF1',
          200: '#99F6E4',
          300: '#5EEAD4',
          400: '#2DD4BF',
          500: '#14B8A6',
          600: '#0D9488',
          700: '#0F766E',
        },
        coral: {
          400: '#FB7185',
          500: '#F43F5E',
        },
        cta: {
          500: '#22C55E',
          600: '#16A34A',
        },
        surface: '#F9FAFB',
        cream: '#FFFBF5',
        star: '#FBBF24',
      },
      fontFamily: {
        sans: ['Sarabun', 'Inter', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
};
