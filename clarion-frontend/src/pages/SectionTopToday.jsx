import { motion } from 'framer-motion';
export default function SectionTopToday() {
  return (
    <motion.section
      id="top-today"
      className="min-h-screen flex items-center justify-center px-6"
      initial={{ opacity: 0, y: 24 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ duration: 0.6 }}
    >
      <div className="glass max-w-5xl w-full p-6 rounded-3xl">
        <h2 className="text-2xl font-semibold mb-2">Top Posts Today</h2>
        <p className="opacity-80">When you hook the backend, this will pull Reddit/Twitter top posts.</p>
      </div>
    </motion.section>
  );
}
