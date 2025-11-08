import React, { useState } from 'react'

export default function ToolCheck() {
  const [url, setUrl] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)

  const onSubmit = async (e) => {
    e.preventDefault()
    setLoading(true); setResult(null)
    // TODO: wire to backend /check_url when you’re ready.
    setTimeout(() => {
      setResult({
        title: 'Demo Result',
        final_score: 0.62,
        platform: 'News',
      })
      setLoading(false)
    }, 900)
  }

  return (
    <div className="space-y-4">
      <form onSubmit={onSubmit} className="flex gap-3">
        <input
          className="w-full px-4 py-3 rounded-2xl bg-white/60 dark:bg-white/10 border border-white/20 outline-none"
          placeholder="Paste a Reddit/Twitter/News URL"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
        />
        <button className="px-5 py-3 rounded-2xl bg-white/80 dark:bg-white/10 border border-white/20">
          {loading ? 'Checking…' : 'Analyze'}
        </button>
      </form>

      {result && (
        <div className="glass p-4">
          <div className="text-sm opacity-70">{result.platform}</div>
          <div className="font-medium">{result.title}</div>
          <div className="mt-1 text-sm opacity-70">Score: {result.final_score}</div>
        </div>
      )}
    </div>
  )
}
