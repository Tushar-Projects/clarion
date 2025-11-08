import React from 'react'

export default function ToolTopToday() {
  // placeholder cards (replace with API wiring later)
  const items = [
    { id: 1, title: 'Reddit — Sample Title', score: 0.78, badge: 'Legit' },
    { id: 2, title: 'News — Sample Title', score: 0.42, badge: 'Mixed' },
    { id: 3, title: 'Twitter — Sample Title', score: 0.15, badge: 'Low' },
  ]
  return (
    <div className="grid md:grid-cols-3 gap-4">
      {items.map(x => (
        <div key={x.id} className="glass p-4 hover:scale-[1.01] transition">
          <div className="text-sm opacity-70 mb-1">{x.badge}</div>
          <div className="font-medium">{x.title}</div>
          <div className="mt-2 text-sm opacity-70">Score: {x.score}</div>
        </div>
      ))}
    </div>
  )
}
