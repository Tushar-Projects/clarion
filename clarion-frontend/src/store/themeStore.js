import { create } from 'zustand';

export const useTheme = create((set, get) => ({
  theme: 'light',
  init: () => {
    const saved = localStorage.getItem('clarion-theme');
    const next = saved || 'light';
    set({ theme: next });
    document.documentElement.classList.toggle('dark', next === 'dark');
  },
  toggle: () => {
    const next = get().theme === 'dark' ? 'light' : 'dark';
    set({ theme: next });
    document.documentElement.classList.toggle('dark', next === 'dark');
    localStorage.setItem('clarion-theme', next);
  }
}));
