import { create } from 'zustand'
import { api } from '../api/client'

export const useAuth = create((set)=>({
  user: null,
  loading: false,
  error: null,
  login: async (email, password)=>{
    set({loading:true,error:null})
    try{
      const {data} = await api.post('/auth/login', {email,password})
      // expect: { token, user:{id,email,name} }
      localStorage.setItem('clarion-token', data.token)
      set({user: data.user, loading:false})
      return true
    }catch(e){
      set({error:'Invalid credentials', loading:false})
      return false
    }
  },
  register: async (name,email,password)=>{
    set({loading:true,error:null})
    try{
      await api.post('/auth/register', {name,email,password})
      set({loading:false})
      return true
    }catch(e){
      set({error:'Registration failed', loading:false})
      return false
    }
  },
  logout: ()=>{
    localStorage.removeItem('clarion-token')
    set({user:null})
  }
}))
 