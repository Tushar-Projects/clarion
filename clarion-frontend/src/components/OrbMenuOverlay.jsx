import { motion, useMotionValue, useTransform } from "framer-motion";
import { useState, useEffect } from "react";
import clsx from "clsx";

const MENU_ITEMS = [
  { id: "top", label: "Top Posts Today", target: "#top-today" },
  { id: "check", label: "Check a Post", target: "#check" },
  { id: "history", label: "History", target: "#history" },
  { id: "settings", label: "Settings", target: "#settings" },
  { id: "theme", label: "Light / Dark", action: "toggleTheme" },
];

export default function OrbMenuOverlay({ onToggleTheme }) {
  const x = useMotionValue(0);

  // Loop left → right → left continuously
  useEffect(() => {
    const loop = () => {
      x.set(-1);
      x.animate(1, { duration: 18, repeat: Infinity, ease: "linear" });
    };
    loop();
  }, [x]);

  return (
    <div className="pointer-events-none absolute inset-0 flex items-center justify-center z-20">
      {MENU_ITEMS.map((item, i) => {
        // Spread items horizontally (phase shift per item)
        const phase = i * 0.35;

        // Horizontal movement
        const posX = useTransform(x, (v) => Math.sin(v + phase) * 200);

        // Vertical curvature for wrap-around effect
        const posY = useTransform(x, (v) => Math.cos(v + phase) * 90);

        // Scale based on proximity to front
        const scale = useTransform(x, (v) => 1 + Math.cos(v + phase) * 0.25);

        return (
          <motion.button
            key={item.id}
            style={{
              x: posX,
              y: posY,
              scale,
            }}
            onClick={(e) => {
              e.stopPropagation();
              if (item.action === "toggleTheme") onToggleTheme?.();
              else document.querySelector(item.target)?.scrollIntoView({ behavior: "smooth" });
            }}
            className={clsx(
              "pointer-events-auto absolute px-4 py-2 rounded-full backdrop-blur-xl text-sm",
              "bg-white/10 dark:bg-white/8 border border-white/25 text-white/90",
              "hover:bg-white/20 hover:scale-110 transition"
            )}
          >
            {item.label}
          </motion.button>
        );
      })}
    </div>
  );
}
