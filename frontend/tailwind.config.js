/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                // Deep, rich background tones
                background: "#0B0F19",
                surface: "#151B2B",
                "surface-highlight": "#1E293B",

                // Vibrant accents
                primary: "#6366f1", // Indigo-500
                "primary-hover": "#4f46e5", // Indigo-600
                secondary: "#94a3b8", // Slate-400
                accent: "#8b5cf6", // Violet-500

                // Functional colors
                success: "#10b981",
                error: "#ef4444",
                warning: "#f59e0b",
            },
            fontFamily: {
                sans: ['Inter', 'sans-serif'],
                heading: ['Outfit', 'sans-serif'],
                mono: ['Space Grotesk', 'monospace'],
            },
            animation: {
                'fade-in': 'fadeIn 0.5s ease-out',
                'slide-up': 'slideUp 0.5s ease-out',
                'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
            },
            keyframes: {
                fadeIn: {
                    '0%': { opacity: '0' },
                    '100%': { opacity: '1' },
                },
                slideUp: {
                    '0%': { transform: 'translateY(20px)', opacity: '0' },
                    '100%': { transform: 'translateY(0)', opacity: '1' },
                },
            },
            backgroundImage: {
                'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
                'hero-glow': 'conic-gradient(from 180deg at 50% 50%, #2a8af6 0deg, #a853ba 180deg, #e92a67 360deg)',
            }
        },
    },
    plugins: [],
}
