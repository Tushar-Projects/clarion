import { motion } from "framer-motion";
import clsx from "clsx";

export default function OrbMenuOrbit({ items, radius = 220, speed = "slow" }) {
  const duration = speed === "fast" ? 10 : speed === "medium" ? 18 : 26;

  return (
    <div className="pointer-events-none absolute inset-0 flex items-center justify-center">
      <motion.div
        className="relative flex gap-6"
        style={{
          transform: `translateY(${radius}px)`, // Move items to horizontal orbit line
        }}
        animate={{ x: ["-30%", "30%", "-30%"] }}
        transition={{ repeat: Infinity, duration, ease: "easeInOut" }}
      >
        {items.map((it) => (
          <button
            key={it.id}
            onClick={(e) => {
              e.stopPropagation();
              it.onClick?.();
            }}
            className={clsx(
              "pointer-events-auto px-4 py-2 rounded-full backdrop-blur-md border glass",
              "bg-white/8 dark:bg-white/6 border-white/20 hover:bg-white/14",
              "text-sm whitespace-nowrap"
            )}
          >
            {it.label}
          </button>
        ))}
      </motion.div>
    </div>
  );
}
