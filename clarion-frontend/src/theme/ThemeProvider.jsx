import { createContext, useContext, useEffect, useState } from 'react'

const ThemeCtx = createContext({ theme:'light', toggle:()=>{} })
export default function ThemeProvider({children}){
  const [theme,setTheme] = useState(() => localStorage.getItem('clarion-theme') || 'light')
  useEffect(()=>{
    document.documentElement.classList.toggle('dark', theme==='dark')
    localStorage.setItem('clarion-theme', theme)
  },[theme])
  const toggle = ()=> setTheme(t => t==='dark' ? 'light' : 'dark')
  return <ThemeCtx.Provider value={{theme,toggle}}>{children}</ThemeCtx.Provider>
}
export const useTheme = () => useContext(ThemeCtx)
 