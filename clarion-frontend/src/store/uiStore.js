import { create } from 'zustand';

export const useUI = create((set, get) => ({
  // hover/click selection
  tools: [
    { key: 'top', label: 'Top Posts Today', hash: '#top-today' },
    { key: 'check', label: 'Check a Post', hash: '#check' },
    { key: 'history', label: 'History', hash: '#history' },
    { key: 'settings', label: 'Settings', hash: '#settings' },
  ],
  activeIndex: 0,
  setActiveIndex: (i) => set({ activeIndex: i }),

  // orb color (driven by credibility score)
  orbColor: '#a78bfa', // default purple (legit)
  setOrbColor: (c) => set({ orbColor: c }),

  // smooth scroll to target section
  goTo: (hash) => {
    const el = document.querySelector(hash);
    if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
  },
}));
