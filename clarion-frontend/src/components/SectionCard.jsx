import React from 'react'

export default function SectionCard({ title, children }) {
  return (
    <div className="glass w-full max-w-6xl mx-auto p-6 md:p-8">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl md:text-2xl font-semibold tracking-tight">{title}</h2>
      </div>
      <div>{children}</div>
    </div>
  )
}
