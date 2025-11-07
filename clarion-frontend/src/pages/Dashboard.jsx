import { useEffect, useState } from 'react'
import { api } from '../api/client'
import PostCard from '../components/PostCard'
import Loader from '../components/Loader'

export default function Dashboard(){
  const [platform, setPlatform] = useState('reddit') // default prefer Reddit
  const [posts, setPosts] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(()=>{
    let ignore=false
    async function fetchTop(){
      setLoading(true); setError(null)
      try{
        const {data} = await api.get('/top', { params: { platform }})
        if(!ignore) setPosts(data)
      }catch(e){
        if(!ignore) setError('Failed to load top posts')
      }finally{
        if(!ignore) setLoading(false)
      }
    }
    fetchTop()
    return ()=>{ ignore=true }
  },[platform])

  return (
    <div>
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Today’s Top Posts</h2>
        <div className="glass px-2 py-1 flex gap-2">
          <button onClick={()=>setPlatform('reddit')}
            className={`px-3 py-1 rounded ${platform==='reddit'?'bg-black/80 text-white dark:bg-white/90 dark:text-black':''}`}>
            Reddit
          </button>
          <button onClick={()=>setPlatform('twitter')}
            className={`px-3 py-1 rounded ${platform==='twitter'?'bg-black/80 text-white dark:bg-white/90 dark:text-black':''}`}>
            Twitter
          </button>
        </div>
      </div>

      <div className="mt-4 grid md:grid-cols-2 xl:grid-cols-3 gap-4">
        {loading && <div className="glass p-6"><Loader/> Loading…</div>}
        {error && <div className="glass p-6 text-red-500">{error}</div>}
        {!loading && !error && posts.map(p=>(
          <PostCard key={p.id} post={p} />
        ))}
      </div>
    </div>
  )
}
 