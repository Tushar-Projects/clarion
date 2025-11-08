import { useState, useEffect } from "react";
import SectionCard from "./components/SectionCard";
import ToolCheck from "./components/ToolCheck";
import ToolTopToday from "./components/ToolTopToday";
import ToolHistory from "./components/ToolHistory";
import ToolSettings from "./components/ToolSettings";
import ThemeToggle from "./components/ThemeToggle";
import Hero from "./pages/Hero";
import Highlights from "./pages/Highlights";

export default function App() {
  const [dark, setDark] = useState(() => {
    return localStorage.getItem("clarion-theme") === "dark";
  });

  useEffect(() => {
    const root = document.documentElement;
    if (dark) {
      root.classList.add("dark");
      localStorage.setItem("clarion-theme", "dark");
    } else {
      root.classList.remove("dark");
      localStorage.setItem("clarion-theme", "light");
    }
  }, [dark]);

  return (
    <div className="scroll-snap">
      {/* NAVBAR */}
      <div className="fixed inset-x-0 top-0 z-50 px-6 py-4">
        <div className="glass max-w-6xl mx-auto flex items-center justify-between px-4 py-2">
          <div className="font-semibold tracking-wide">
            Clarion Intelligence Console
          </div>
          <div className="flex items-center gap-3 text-sm opacity-90">
            <a href="#top" className="hover:opacity-100">Home</a>
            <a href="#top-today" className="hover:opacity-100">Top Today</a>
            <a href="#check" className="hover:opacity-100">Check Post</a>
            <a href="#history" className="hover:opacity-100">History</a>
            <a href="#settings" className="hover:opacity-100">Settings</a>
            <ThemeToggle dark={dark} setDark={setDark} />
          </div>
        </div>
      </div>

      {/* HERO */}
      <section id="top" className="section flex items-center justify-center px-6">
        <Hero />
      </section>

      {/* TOP TODAY */}
      <section id="top-today" className="section px-6 flex items-center justify-center">
        <SectionCard title="Top Posts Today">
          <ToolTopToday />
        </SectionCard>
      </section>

      {/* CHECK A POST */}
      <section id="check" className="section px-6 flex items-center justify-center">
        <SectionCard title="Check a Post">
          <ToolCheck />
        </SectionCard>
      </section>

      {/* HISTORY */}
      <section id="history" className="section px-6 flex items-center justify-center">
        <SectionCard title="Your History">
          <ToolHistory />
        </SectionCard>
      </section>

      {/* SETTINGS */}
      <section id="settings" className="section px-6 flex items-center justify-center">
        <SectionCard title="Settings">
          <ToolSettings />
        </SectionCard>
      </section>

      {/* (OPTIONAL) Highlights Section */}
      <section className="section flex items-center justify-center px-6">
        <Highlights />
      </section>
    </div>
  );
}
