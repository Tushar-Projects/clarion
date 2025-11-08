import { motion } from 'framer-motion';
export default function SectionSettings() {
  return (
    <motion.section
      id="settings"
      className="min-h-screen flex items-center justify-center px-6"
      initial={{ opacity: 0, y: 24 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ duration: 0.6 }}
    >
      <div className="glass max-w-3xl w-full p-6 rounded-3xl">
        <h2 className="text-2xl font-semibold mb-3">Settings</h2>
        <p className="opacity-80">Theme, sources, preferences…</p>
      </div>
    </motion.section>
  );
}
