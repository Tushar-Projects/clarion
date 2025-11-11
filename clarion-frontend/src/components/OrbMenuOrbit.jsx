import { useEffect, useRef, useState, useMemo } from "react";
import { motion, AnimatePresence } from "framer-motion";
import clsx from "clsx";

const BTN = "px-5 py-2.5 rounded-full glass text-base whitespace-nowrap select-none";
const HOVER = { scale: 1.04, transition: { duration: 0.25, ease: "easeOut" } };


export default function OrbMenuOrbit({
  items,
  radius = 290,
  speed = 0.10,
  showSourcesSub = false,
  onPickSource,
  fixed = false,
  active = null,
}) {
  const [t, setT] = useState(0);
  const [hovered, setHovered] = useState(null);
  const raf = useRef();

 // run RAF only on hero
  useEffect(() => {
    if (active != null) return; // section open → don't animate
    const tick = () => {
      setT((prev) => prev + (hovered ? 0 : speed * 0.016));
      raf.current = requestAnimationFrame(tick);
    };
    raf.current = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf.current);
  }, [hovered, speed, active]);

  // when we come back to hero, re-center angle
  useEffect(() => {
    if (active === null) setT(0);
 }, [active]);


  // this box matches OrbCanvas (520x520)
  const center = { x: 260, y: 260 + 20};

  // place on equator; no vertical drift (so path hugs the orb's X axis)
  const angles = useMemo(() => {
    const N = items.length;
    const base = t;
    return items.map((_, i) => base + (i * (2 * Math.PI)) / N);
  }, [items, t]);

  return (
    <div
      className={`${fixed ? "fixed" : "absolute"} z-[40]`}
      style={{ width: 520, height: 520, left: "50%", top: "50%", transform: "translate(-50%, -50%)", pointerEvents: "none" }}
    >
      {items.map((item, i) => {
        const ang = angles[i];

        // Equator ring (true horizontal orbit)
        const x = center.x + Math.cos(ang) * radius;
        const y = center.y; // no vertical offset: stays on equator

        // depth: -1 (back) -> +1 (front)
        const depth = Math.sin(ang);
        const frontness = (depth + 1) / 2; // 0..1

        // Presentational tweaks
        const scale = 1.0 + frontness * 0.26;          // bigger in front
        const alpha = 0.45 + frontness * 0.55;         // fade when behind
        const clickable = depth > 0;                   // only clickable in front

        const isSources = item.id === "sources";
        const isHovered = hovered === item.id;

        return (
          <motion.button
            key={item.id}
            className={clsx(BTN)}
            // whileHover={HOVER}
           style={{
  position: "absolute",
  left: x,
  top: y,
  transform: `translate(-50%, -50%) scale(${scale})`,
  opacity: alpha,
  zIndex: Math.round(50 + frontness * 50),
  pointerEvents: clickable ? "auto" : "none",
  border: isHovered ? "1.6px solid rgba(255,255,255,0.85)" : "1px solid rgba(255,255,255,0.25)",
  boxShadow: isHovered
    ? "0 0 14px rgba(255,255,255,0.55)"
    : "0 0 6px rgba(0,0,0,0.25)",
  transition: "border 0.18s ease, box-shadow 0.18s ease"
}}

            onMouseEnter={() => setHovered(item.id)}
            onMouseLeave={() => setHovered(null)}
            onClick={(e) => {
              e.stopPropagation();
              if (!clickable) return;
              if (isSources) return; // sources handled via submenu
              item.onClick?.();
            }}
          >
            {item.label}

            {/* Sources submenu */}
            {isSources && (
              <AnimatePresence>
                {showSourcesSub && isHovered && (
                  <MiniRadial
                    anchor={{ x, y }}
                    onPick={(s) => onPickSource?.(s)}
                  />
                )}
              </AnimatePresence>
            )}
          </motion.button>
        );
      })}
    </div>
  );
}

function MiniRadial({ anchor, onPick }) {
  const opts = [
    { id: "reddit",  label: "Reddit"  },
    { id: "twitter", label: "Twitter" },
    { id: "news",    label: "News"    },
  ];
  const r = 70;

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1, transition: { duration: 0.18 } }}
      exit={{ opacity: 0, scale: 0.9, transition: { duration: 0.15 } }}
      className="absolute"
      style={{ left: anchor.x, top: anchor.y, transform: "translate(-50%, -50%)" }}
    >
      {opts.map((o, idx) => {
        const ang = (idx / opts.length) * 2 * Math.PI;
        const x = Math.cos(ang) * r;
        const y = Math.sin(ang) * r;

        return (
          <motion.button
            key={o.id}
            whileHover={{ scale: 1.06 }}
            className="px-3 py-1.5 rounded-full glass text-sm pointer-events-auto"
            style={{ position: "absolute", left: x, top: y, transform: "translate(-50%, -50%)" }}
            onClick={(e) => { e.stopPropagation(); onPick?.(o.id); }}
          >
            {o.label}
          </motion.button>
        );
      })}
    </motion.div>
  );
}
