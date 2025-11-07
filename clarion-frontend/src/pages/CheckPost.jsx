import { useState } from 'react'
import { api } from '../api/client'
import PostCard from '../components/PostCard'
import Loader from '../components/Loader'

export default function CheckPost(){
  const [url,setUrl] = useState('')
  const [loading,setLoading] = useState(false)
  const [data,setData] = useState(null)
  const [error,setError] = useState(null)

  const onSubmit = async (e)=>{
    e.preventDefault()
    setLoading(true); setError(null); setData(null)
    try{
      const {data} = await api.post('/check_url', { url })
      setData(data)
    }catch(e){
      setError('Could not analyze this URL')
    }finally{ setLoading(false) }
  }

  return (
    <div className="space-y-4">
      <div className="glass p-4">
        <form onSubmit={onSubmit} className="flex gap-2">
          <input value={url} onChange={e=>setUrl(e.target.value)} placeholder="Paste Reddit/Twitter/News link…" className="flex-1 px-3 py-2 rounded bg-white/60 dark:bg-white/5 border border-white/30"/>
          <button className="px-4 py-2 rounded bg-black/80 text-white dark:bg-white/90 dark:text-black">Check</button>
        </form>
      </div>

      {loading && <div className="glass p-6"><Loader/> Analyzing…</div>}
      {error && <div className="glass p-6 text-red-500">{error}</div>}
      {data && <PostCard post={data} expanded />}
    </div>
  )
}
