import { motion, useMotionValue, useTransform } from "framer-motion";

export default function OrbMenuOrbit({ items, radius = 260, speed = 0.5 }) {
  const rot = useMotionValue(0);
  const rotate = () => rot.set(rot.get() + speed * 0.002);

  return (
    <div
      className="pointer-events-auto absolute inset-0 flex items-center justify-center"
      style={{ zIndex: 15 }}
      onMouseMove={rotate}
    >
      {items.map((item, i) => {
        const angle = (i / items.length) * Math.PI * 2;
        const x = useTransform(rot, (r) => Math.cos(r + angle) * radius);
        const y = useTransform(rot, (r) => Math.sin(r + angle) * 40);

        return (
          <motion.button
            key={item.id}
            style={{ x, y }}
            onClick={item.onClick}
            whileHover={{ scale: 1.2, opacity: 1 }}
            className="absolute px-4 py-2 rounded-xl bg-white/20 dark:bg-white/10 backdrop-blur-md text-white border border-white/30 text-sm"
          >
            {item.label}
          </motion.button>
        );
      })}
    </div>
  );
}
