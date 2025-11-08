import { motion } from "framer-motion";
import GlassOrb from "../components/GlassOrb";

export default function Hero() {
  return (
    <section className="min-h-screen relative overflow-hidden flex items-center justify-center bg-[radial-gradient(ellipse_at_center,rgba(180,200,255,0.25),transparent_60%)] dark:bg-[radial-gradient(ellipse_at_center,rgba(30,30,50,0.6),transparent_60%)]">
      {/* subtle vignette */}
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_at_center,transparent_40%,rgba(0,0,0,0.35))]" />

      <div className="max-w-7xl w-full px-6 grid md:grid-cols-2 gap-10 items-center">
        <div className="order-2 md:order-1">
          <motion.h1
            initial={{ y: 24, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ duration: 0.7, ease: "easeOut" }}
            className="text-5xl md:text-6xl font-semibold tracking-tight"
          >
            Clarion
            <span className="block text-xl md:text-2xl mt-3 opacity-80">
              Intelligence Console
            </span>
          </motion.h1>

          <motion.p
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ duration: 0.75, delay: 0.1, ease: "easeOut" }}
            className="mt-6 text-lg leading-relaxed opacity-85"
          >
            A glass-smooth interface for multi-stage credibility analysis across
            Reddit, News, and Tweets — with fact-checks, source reliability, and
            sarcasm-aware signals. Clarity over noise.
          </motion.p>

          <motion.div
            initial={{ y: 18, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ duration: 0.8, delay: 0.2, ease: "easeOut" }}
            className="mt-8 flex gap-4"
          >
            <button className="glass-card px-5 py-3 rounded-xl hover:scale-[1.02] transition">
              Explore Top Posts
            </button>
            <button className="glass-card px-5 py-3 rounded-xl hover:scale-[1.02] transition">
              Check a URL
            </button>
          </motion.div>
        </div>

        <div className="order-1 md:order-2 flex items-center justify-center">
          {/* Pass a demo score to preview color (e.g., 0.85 = purple verified) */}
          <GlassOrb size={420} score={0.85} />
        </div>
      </div>

      <div className="absolute bottom-8 left-0 right-0 flex justify-center">
        <span className="text-sm opacity-70">Scroll</span>
      </div>
    </section>
  );
}
