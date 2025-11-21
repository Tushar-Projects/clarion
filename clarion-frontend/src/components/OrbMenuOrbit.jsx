import { useEffect, useRef, useState, useMemo } from "react";
import { motion, AnimatePresence } from "framer-motion";
import clsx from "clsx";

const BTN = "px-5 py-2.5 rounded-full glass text-base whitespace-nowrap select-none";

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
  const center = { x: 260, y: 260 + 20 };

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
          <motion.div
            key={item.id}
            style={{
              position: "absolute",
              left: x,
              top: y,
              transform: `translate(-50%, -50%) scale(${scale})`,
              opacity: alpha,
              zIndex: Math.round(50 + frontness * 50),
              pointerEvents: clickable ? "auto" : "none",
            }}
            onMouseEnter={() => setHovered(item.id)}
            onMouseLeave={() => setHovered(null)}
          >
            <div
              className={clsx(BTN)}
              style={{
                border: isHovered ? "1.6px solid rgba(255,255,255,0.85)" : "1px solid rgba(255,255,255,0.25)",
                boxShadow: isHovered
                  ? "0 0 14px rgba(255,255,255,0.55)"
                  : "0 0 6px rgba(0,0,0,0.25)",
                transition: "border 0.18s ease, box-shadow 0.18s ease",
                cursor: "pointer",
              }}
              onClick={(e) => {
                e.stopPropagation();
                if (!clickable) return;
                item.onClick?.();
              }}
            >
              {item.label}
            </div>

            {/* Sources submenu */}
            {isSources && (
              <AnimatePresence>
                {showSourcesSub && (
                  <SourceDropdown
                    onPick={(s) => onPickSource?.(s)}
                  />
                )}
              </AnimatePresence>
            )}
          </motion.div>
        );
      })}
    </div>
  );
}

function SourceDropdown({ onPick }) {
  const [customMode, setCustomMode] = useState(false);
  const [customVal, setCustomVal] = useState("");

  const opts = [
    { id: "news", label: "News" },
    // Removed Reddit/Twitter as requested
  ];

  return (
    <motion.div
      initial={{ opacity: 0, y: -10, scale: 0.95 }}
      animate={{ opacity: 1, y: 10, scale: 1, transition: { duration: 0.2, ease: "easeOut" } }}
      exit={{ opacity: 0, y: -10, scale: 0.95, transition: { duration: 0.15 } }}
      className="absolute left-1/2 -translate-x-1/2 top-full flex flex-col gap-1 p-2 rounded-xl glass border border-white/20 shadow-xl z-[60]"
      style={{ minWidth: 140, pointerEvents: "auto" }}
      onClick={(e) => e.stopPropagation()}
    >
      {opts.map((o) => (
        <button
          key={o.id}
          className="px-4 py-2 rounded-lg hover:bg-white/10 text-sm text-left w-full transition-colors text-white"
          onClick={() => onPick?.(o.id)}
        >
          {o.label}
        </button>
      ))}

      {/* Custom Option */}
      {!customMode ? (
        <button
          className="px-4 py-2 rounded-lg hover:bg-white/10 text-sm text-left w-full transition-colors text-white"
          onClick={() => setCustomMode(true)}
        >
          Custom
        </button>
      ) : (
        <form
          onSubmit={(e) => {
            e.preventDefault();
            if (customVal.trim()) onPick?.(customVal.trim());
          }}
          className="px-2 py-1"
        >
          <input
            autoFocus
            type="text"
            className="w-full bg-white/10 rounded px-2 py-1 text-sm text-white outline-none border border-white/30 focus:border-white/60"
            placeholder="subreddit..."
            value={customVal}
            onChange={(e) => setCustomVal(e.target.value)}
            onKeyDown={(e) => e.stopPropagation()}
          />
        </form>
      )}
    </motion.div>
  );
}
