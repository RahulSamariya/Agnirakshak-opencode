/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        heatwave: {
          low: '#22c55e',
          medium: '#f59e0b',
          high: '#ef4444',
          extreme: '#7c2d12',
        },
      },
    },
  },
  plugins: [],
};
