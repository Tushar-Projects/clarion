// src/store/uiStore.js
import { create } from "zustand";

export const useUI = create((set) => ({
  mode: "menu",        // "menu" (orb + orbit menu) or "page" (section content)
  activePage: null,    // "top" | "check" | "history" | "settings" | etc.

  // When user selects a function orbit item
  enterPage: (page) =>
    set(() => ({
      mode: "page",
      activePage: page,
    })),

  // When user clicks "Return to Menu" or the orb
  returnToMenu: () =>
    set(() => ({
      mode: "menu",
      activePage: null,
    })),
  
  // Orb dynamic color (future post-scoring)
  orbColor: "#a38bff",
  setOrbColor: (c) => set({ orbColor: c }),
}));
