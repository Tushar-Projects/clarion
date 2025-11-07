import Navbar from './components/Navbar'
import AppRoutes from './routes'

export default function App(){
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-200 dark:from-[#0b1220] dark:to-[#0a0f1a]">
      <div className="max-w-7xl mx-auto p-4 sm:p-6">
        <Navbar/>
        <div className="mt-6">
          <AppRoutes/>
        </div>
      </div>
    </div>
  )
}
