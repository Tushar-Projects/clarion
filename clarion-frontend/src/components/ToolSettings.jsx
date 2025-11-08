import React, { useState } from 'react'

export default function ToolSettings() {
  const [preferred, setPreferred] = useState('reddit')
  return (
    <div className="grid md:grid-cols-2 gap-4">
      <div className="glass p-4">
        <div className="font-medium mb-2">Preferred Source</div>
        <div className="flex gap-2">
          {['reddit','twitter','news'].map(k => (
            <button
              key={k}
              onClick={() => setPreferred(k)}
              className={`px-3 py-2 rounded-xl border border-white/20 ${preferred===k?'bg-white/30 dark:bg-white/10':''}`}
            >
              {k}
            </button>
          ))}
        </div>
      </div>

      <div className="glass p-4">
        <div className="font-medium mb-2">Theme</div>
        <div className="opacity-70 text-sm">Use the toggle in the top bar.</div>
      </div>
    </div>
  )
}
