import React from 'react'

export default function ThemeToggle({ dark, setDark }) {
  return (
    <button
      onClick={() => setDark(v => !v)}
      className="ml-2 px-3 py-1 rounded-lg bg-white/20 dark:bg-white/10 border border-white/10"
      title="Toggle theme"
    >
      {dark ? '🌙' : '☀️'}
    </button>
  )
}
