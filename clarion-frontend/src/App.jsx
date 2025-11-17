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
  const [orbitEpoch, setOrbitEpoch] = useState(0); // to reset orbit position on source change
  const [active, setActive] = useState(null); // null = hero
  const [source, setSource] = useState("all");
  const [showSourcesSub, setShowSourcesSub] = useState(false);

  const isHero = active === null;

  // prevent scroll on hero (no layout shifts)
  useEffect(() => {
    const prev = document.body.style.overflow;
    document.body.style.overflow = isHero ? "hidden" : "";
    return () => { document.body.style.overflow = prev; };
  }, [isHero]);

  const openSection = (key) => {
    setActive(key);
    setShowSourcesSub(false);
    requestAnimationFrame(() => window.scrollTo({ top: 0, behavior: "smooth" }));
  };

  const backToHero = () => {
    window.scrollTo({ top: 0, behavior: "auto" });
    setOrbitEpoch((e) => e + 1);
    setActive(null);
  };

  const orbitItems = useMemo(
    () => [
      { id: "top",      label: "Top Posts Today", onClick: () => openSection("top") },
      { id: "check",    label: "Check a Post",    onClick: () => openSection("check") },
      { id: "history",  label: "History",         onClick: () => openSection("history") },
      { id: "settings", label: "Settings",        onClick: () => openSection("settings") },
      { id: "sources",  label: "Sources",         onClick: () => setShowSourcesSub(v => !v) },
      { id: "theme",    label: dark ? "Light Mode" : "Dark Mode", onClick: () => setDark(v => !v) },
    ],
    [dark]
  );

  const brandVariants = {
    hidden: { opacity: 0, y: -12 },
    show:   { opacity: 1, y: 0, transition: { duration: 0.6, ease: "easeOut" } }
  };

  const titleVariants = {
    hidden: { opacity: 0, y: 16 },
    show:   { opacity: 1, y: 0, transition: { duration: 0.6, ease: "easeOut" } },
    exit:   { opacity: 0, y: -16, transition: { duration: 0.45, ease: "easeIn" } }
  };

  // Section enter/exit
  const sectionEnter = { opacity: 1, y: 0, transition: { duration: 0.45, ease: "easeOut" } };
  const sectionExit  = { opacity: 0, y: -14, transition: { duration: 0.35, ease: "easeIn" } };

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

      {/* ORB ALWAYS MOUNTED */}
<div className="fixed inset-0 z-[40] pointer-events-none">
  
  <OrbCanvas
    inCorner={!isHero}
    cornerOffset={{ top: 16, right: 36 }}
    cornerScale={0.4}
    onClickCorner={backToHero}
    fixed
    tint="purple"
  />

  {/* Title only on hero */}
  <AnimatePresence>
    {isHero && (
      <motion.div
        key="title"
        className="absolute left-1/2 -translate-x-1/2 top-[58vh] z-[30] text-center px-6 pointer-events-none"
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

  {/* Orbiting buttons — ONLY visible on hero */}
  <AnimatePresence>
    {isHero && (
      <div className="absolute inset-0 pointer-events-auto">
        <OrbMenuOrbit
          key={`orbit-${orbitEpoch}`}
          items={orbitItems}
          radius={260}
          speed={0.09}
          showSourcesSub={showSourcesSub}
          onPickSource={(s) => { setSource(s); setShowSourcesSub(false); }}
          fixed
          active={active}
        />
      </div>
    )}
  </AnimatePresence>
</div>


      {/* Spacer that only occupies flow when a section is open (prevents content jumping under the fixed overlay) */}
      {!isHero && <div className="h-[140px]" />}

      {/* =========================== */}
      {/* Sections */}
      {/* =========================== */}
      <AnimatePresence mode="wait">
        {active === "top" && (
          <motion.div
            key="top"
            initial={{ opacity: 0, y: 14 }}
            animate={sectionEnter}
            exit={sectionExit}
            className="pt-6"
          >
            <SectionTopToday source={source} />
          </motion.div>
        )}

        {active === "check" && (
          <motion.div
            key="check"
            initial={{ opacity: 0, y: 14 }}
            animate={sectionEnter}
            exit={sectionExit}
            className="pt-6"
          >
            <SectionCheck source={source} />
          </motion.div>
        )}

        {active === "history" && (
          <motion.div
            key="history"
            initial={{ opacity: 0, y: 14 }}
            animate={sectionEnter}
            exit={sectionExit}
            className="pt-6"
          >
            <SectionHistory source={source} />
          </motion.div>
        )}

        {active === "settings" && (
          <motion.div
            key="settings"
            initial={{ opacity: 0, y: 14 }}
            animate={sectionEnter}
            exit={sectionExit}
            className="pt-6"
          >
            <SectionSettings source={source} />
          </motion.div>
        )}
      </AnimatePresence>

      <footer className="py-10 text-center opacity-60 text-sm">
        © {new Date().getFullYear()} Clarion
      </footer>
    </main>
  );
}
