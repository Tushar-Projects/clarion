// src/pages/Hero.jsx
import { motion } from "framer-motion";
import OrbCanvas from "../components/OrbCanvas";
import OrbMenuOverlay from "../components/OrbMenuOverlay";

export default function Hero() {
  return (
    <section
      id="hero"
      className="min-h-[88vh] md:min-h-screen relative flex items-center justify-center overflow-hidden"
    >
      {/* Orb */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8 }}
        className="absolute inset-0"
      >
        <OrbCanvas />
      </motion.div>

      {/* Headline */}
      <motion.div
        className="relative z-10 text-center max-w-4xl px-6"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.35, duration: 0.6 }}
      >
        <h1 className="text-4xl md:text-6xl font-semibold">
          Clarion <span className="opacity-60">— see truth clearly.</span>
        </h1>
        <p className="mt-3 opacity-75">
          Hover the orb to explore. Click a mode to continue.
        </p>
      </motion.div>

      {/* Radial Navigation Overlay */}
      <OrbMenuOverlay />


    </section>
  );
}
