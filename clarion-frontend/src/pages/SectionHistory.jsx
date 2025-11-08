import { motion } from 'framer-motion';
export default function SectionHistory() {
  return (
    <motion.section
      id="history"
      className="min-h-screen flex items-center justify-center px-6"
      initial={{ opacity: 0, y: 24 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ duration: 0.6 }}
    >
      <div className="glass max-w-4xl w-full p-6 rounded-3xl">
        <h2 className="text-2xl font-semibold mb-2">History</h2>
        <p className="opacity-80">Recent checks will appear here.</p>
      </div>
    </motion.section>
  );
}
