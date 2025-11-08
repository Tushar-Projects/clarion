import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import OrbCanvas from "./components/OrbCanvas";
import OrbMenuOrbit from "./components/OrbMenuOrbit";
import SectionTopToday from "./pages/SectionTopToday";
import SectionCheck from "./pages/SectionCheck";
import SectionHistory from "./pages/SectionHistory";
import SectionSettings from "./pages/SectionSettings";

export default function App() {
  const [dark, setDark] = useState(() => localStorage.getItem("clarion-theme") === "dark");
  const [active, setActive] = useState(null); // null = hero shown

  useEffect(() => {
    const root = document.documentElement;
    if (dark) { root.classList.add("dark"); localStorage.setItem("clarion-theme", "dark"); }
    else { root.classList.remove("dark"); localStorage.setItem("clarion-theme", "light"); }
  }, [dark]);

  const orbitItems = [
    { id: "top", label: "Top Posts Today", onClick: () => setActive("top") },
    { id: "check", label: "Check a Post", onClick: () => setActive("check") },
    { id: "history", label: "History", onClick: () => setActive("history") },
    { id: "settings", label: "Settings", onClick: () => setActive("settings") },
    { id: "theme", label: dark ? "Light Mode" : "Dark Mode", onClick: () => setDark(v => !v) },
  ];

  return (
    <main className="min-h-screen text-zinc-900 dark:text-zinc-100 bg-gradient-to-b from-white to-zinc-50 dark:from-[#0a0b0e] dark:to-black">
      {/* top bar brand only (no theme switch here) */}
      <div className="fixed inset-x-0 top-0 z-50 px-6 py-4">
        <div className="glass max-w-6xl mx-auto flex items-center justify-between px-4 py-2 rounded-2xl">
          <div className="font-semibold tracking-wide">Clarion Intelligence Console</div>
        </div>
      </div>

      {/* HERO */}
      <section id="hero" className="min-h-[88vh] md:min-h-screen flex items-center justify-center relative pt-20">
        {/* Orb */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7 }}
          className="absolute inset-0"
        >
          <OrbCanvas />
        </motion.div>

        {/* Title (fades out after selection) */}
        <AnimatePresence>
          {!active && (
            <motion.div
              key="title"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.45 }}
              className="relative z-10 w-full max-w-5xl mx-auto px-6"
            >
              <div className="text-center mb-6">
                <h1 className="text-4xl md:text-6xl font-semibold tracking-tight">
                  Clarion<span className="opacity-60"> — see truth clearly.</span>
                </h1>
                <p className="mt-3 opacity-80">Hover the orb to explore. Click a mode to continue.</p>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Radial orbit menu (slow) */}
        <OrbMenuOrbit items={orbitItems} radius={220} speed="slow" />
      </section>

      {/* Sections (only show selected) */}
      {active === "top" && <SectionTopToday />}
      {active === "check" && <SectionCheck />}
      {active === "history" && <SectionHistory />}
      {active === "settings" && <SectionSettings />}

      <footer className="py-10 text-center opacity-60 text-sm">
        © {new Date().getFullYear()} Clarion
      </footer>
    </main>
  );
}
