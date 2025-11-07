import { useState } from 'react'
import { useAuth } from '../store/authStore'
import { Link, useNavigate } from 'react-router-dom'
import Loader from '../components/Loader'

export default function Register(){
  const [name,setName] = useState('')
  const [email,setEmail] = useState('')
  const [password,setPassword] = useState('')
  const { register, loading, error } = useAuth()
  const nav = useNavigate()

  const onSubmit = async (e)=>{
    e.preventDefault()
    const ok = await register(name,email,password)
    if(ok) nav('/login')
  }

  return (
    <div className="max-w-md mx-auto mt-12 glass p-6">
      <h1 className="text-xl font-semibold mb-2">Create your account</h1>
      <form onSubmit={onSubmit} className="space-y-4">
        <input className="w-full px-3 py-2 rounded-lg bg-white/60 dark:bg-white/5 border border-white/30"
               placeholder="Full name" value={name} onChange={e=>setName(e.target.value)} />
        <input className="w-full px-3 py-2 rounded-lg bg-white/60 dark:bg-white/5 border border-white/30"
               placeholder="Email" value={email} onChange={e=>setEmail(e.target.value)} />
        <input className="w-full px-3 py-2 rounded-lg bg-white/60 dark:bg-white/5 border border-white/30"
               placeholder="Password" type="password" value={password} onChange={e=>setPassword(e.target.value)} />
        {error && <div className="text-red-500 text-sm">{error}</div>}
        <button disabled={loading} className="w-full py-2 rounded-lg bg-black/80 text-white dark:bg-white/90 dark:text-black">
          {loading ? <Loader/> : 'Register'}
        </button>
      </form>
      <div className="text-sm mt-4">Already have an account? <Link className="underline" to="/login">Login</Link></div>
    </div>
  )
}
