import { motion } from 'framer-motion';
export default function SectionCheck() {
  return (
    <motion.section
      id="check"
      className="min-h-screen flex items-center justify-center px-6"
      initial={{ opacity: 0, y: 24 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ duration: 0.6 }}
    >
      <div className="glass max-w-3xl w-full p-6 rounded-3xl">
        <h2 className="text-2xl font-semibold mb-3">Check a Post</h2>
        <input
          type="text"
          placeholder="Paste a Reddit/Twitter/News URL…"
          className="w-full rounded-xl px-4 py-3 bg-white/70 dark:bg-black/30 border border-white/20 outline-none"
        />
        <div className="mt-4 text-sm opacity-70">This will call <code>/check_url</code> later.</div>
      </div>
    </motion.section>
  );
}
