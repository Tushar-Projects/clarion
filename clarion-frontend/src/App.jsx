import { useEffect, useState, useMemo } from "react";
import { motion, AnimatePresence } from "framer-motion";
import OrbCanvas from "./components/OrbCanvas";
import OrbMenuOrbit from "./components/OrbMenuOrbit";

import SectionTopToday from "./pages/SectionTopToday";
import SectionCheck from "./pages/SectionCheck";
import SectionHistory from "./pages/SectionHistory";
import SectionSettings from "./pages/SectionSettings";

export default function App() {
  const [dark, setDark] = useState(() => localStorage.getItem("clarion-theme") === "dark");
  useEffect(() => {
    document.documentElement.classList.toggle("dark", dark);
    localStorage.setItem("clarion-theme", dark ? "dark" : "light");
  }, [dark]);

  const [active, setActive] = useState(null);        // null = hero, else "top" | "check" | "history" | "settings"
  const [source, setSource] = useState("all");
  const [showSourcesSub, setShowSourcesSub] = useState(false);

  const isHero = active === null;

  const openSection = (key) => {
    setActive(key);
    setShowSourcesSub(false);
    // ensure the section starts at the top every time
    requestAnimationFrame(() => window.scrollTo({ top: 0, behavior: "smooth" }));
  };

  const orbitItems = useMemo(() => ([
    { id: "top",      label: "Top Posts Today", onClick: () => openSection("top") },
    { id: "check",    label: "Check a Post",    onClick: () => openSection("check") },
    { id: "history",  label: "History",         onClick: () => openSection("history") },
    { id: "settings", label: "Settings",        onClick: () => openSection("settings") },
    { id: "sources",  label: "Sources",         onClick: () => setShowSourcesSub(v => !v) },
    { id: "theme",    label: dark ? "Light Mode" : "Dark Mode", onClick: () => setDark(v => !v) },
  ]), [dark]);

  const brandVariants = {
    hidden: { opacity: 0, y: -12 },
    show:   { opacity: 1, y: 0, transition: { duration: 0.6, ease: "easeOut" } }
  };

  const titleVariants = {
    hidden: { opacity: 0, y: 10 },
    show:   { opacity: 1, y: 0, transition: { duration: 0.5, ease: "easeOut" } },
    exit:   { opacity: 0, y: -8, transition: { duration: 0.35, ease: "easeIn" } }
  };

  return (
    <main className="min-h-screen text-zinc-900 dark:text-zinc-100 bg-gradient-to-b from-white to-zinc-50 dark:from-[#0a0b0e] dark:to-black">
      {/* Brand (stays) */}
      <motion.div
        className="fixed top-4 left-6 z-[60] px-4 py-2 rounded-xl glass"
        variants={brandVariants}
        initial="hidden"
        animate="show"
      >
        <span className="font-semibold tracking-wide">Clarion Intelligence Console</span>
      </motion.div>

      {/* Hero layer (fixed so scrolling doesn't affect orb/menu) */}
      <section className="min-h-[88vh] md:min-h-screen relative">
        {/* ORB */}
        <OrbCanvas
          inCorner={!isHero}
          cornerOffset={{ top: 80, right: 80 }}
          cornerScale={0.6}
          onClickCorner={() => setActive(null)}
          fixed={isHero}                // <— FIX: keep orb fixed while on hero
          tint="purple"                 // <— keep the purple glitch tint
        />

        {/* Title */}
        <AnimatePresence>
          {isHero && (
            <motion.div
              key="title"
              className="fixed left-1/2 -translate-x-1/2 top-[58vh] z-[30] text-center px-6"
              variants={titleVariants}
              initial="hidden"
              animate="show"
              exit="exit"
            >
              <h1 className="text-4xl md:text-6xl font-semibold tracking-tight">
                Clarion <span className="opacity-60">— see truth clearly.</span>
              </h1>
              <p className="mt-3 opacity-80">Hover the orb to explore. Click a mode to continue.</p>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Orbit menu */}
        <AnimatePresence>
          {isHero && (
            <OrbMenuOrbit
              key="orbit"
              items={orbitItems}
              radius={210}                  // ring safely inside orb
              speed={0.10}                  // slower rotation
              showSourcesSub={showSourcesSub}
              onPickSource={(s) => { setSource(s); setShowSourcesSub(false); }}
              fixed                            // <— FIX: menu fixed with orb
            />
          )}
        </AnimatePresence>
      </section>

      {/* Sections — add consistent top padding so content isn’t “too low” */}
      {active === "top"      && <div className="pt-6"><SectionTopToday source={source} /></div>}
      {active === "check"    && <div className="pt-6"><SectionCheck     source={source} /></div>}
      {active === "history"  && <div className="pt-6"><SectionHistory   source={source} /></div>}
      {active === "settings" && <div className="pt-6"><SectionSettings  source={source} /></div>}

      <footer className="py-10 text-center opacity-60 text-sm">© {new Date().getFullYear()} Clarion</footer>
    </main>
  );
}
