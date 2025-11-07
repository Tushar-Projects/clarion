import { useTheme } from '../theme/ThemeProvider'
import { useAuth } from '../store/authStore'
import { Link, useLocation } from 'react-router-dom'

export default function Navbar(){
  const { theme, toggle } = useTheme()
  const { user, logout } = useAuth()
  const loc = useLocation()
  return (
    <div className="glass px-4 py-3 flex items-center justify-between">
      <div className="flex items-center gap-3">
        <div className="w-8 h-8 rounded-xl bg-black/80 dark:bg-white/80" />
        <div>
          <div className="text-sm uppercase tracking-widest opacity-70">Clarion</div>
          <div className="font-semibold">Clarion Intelligence Console</div>
        </div>
      </div>
      <div className="flex items-center gap-4">
        <Link className={`text-sm ${loc.pathname==='/'?'font-semibold':''}`} to="/">Dashboard</Link>
        <Link className={`text-sm ${loc.pathname==='/check'?'font-semibold':''}`} to="/check">Check a Post</Link>
        <button onClick={toggle} className="text-sm px-3 py-1 rounded-lg border border-white/20">
          {theme==='dark'?'Light':'Dark'}
        </button>
        {user && (
          <button onClick={logout} className="text-sm px-3 py-1 rounded-lg bg-black/80 text-white dark:bg-white/90 dark:text-black">
            Logout
          </button>
        )}
      </div>
    </div>
  )
}
