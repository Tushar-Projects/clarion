import { useState } from "react";
import { motion } from "framer-motion";
import { checkPostByUrl } from "../api/index";

export default function SectionCheck() {
  const [url, setUrl] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleCheck = async () => {
    if (!url.trim()) return;
    setLoading(true);
    setResult(null);

    const data = await checkPostByUrl(url);
    setResult(data);
    setLoading(false);
  };

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
        <h2 className="text-2xl font-semibold mb-4">Check a Post</h2>

        {/* URL Input */}
        <div className="flex gap-2">
          <input
            type="text"
            placeholder="Paste a Reddit / Twitter / News URL…"
            className="flex-1 rounded-xl px-4 py-3 bg-white/70 dark:bg-black/30 border border-white/20 outline-none"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
          />
          <button
            onClick={handleCheck}
            className="px-4 py-3 rounded-xl glass hover:scale-[1.03] transition select-none"
          >
            Check
          </button>
        </div>

        {/* Loading Indicator */}
        {loading && (
          <p className="mt-4 text-sm opacity-70">Analyzing post…</p>
        )}

        {/* Result Box */}
        {result && !loading && (
          <div className="mt-6 p-5 rounded-2xl border border-white/20 bg-white/60 dark:bg-black/30 backdrop-blur">
            <h3 className="text-xl font-semibold">{result.title || "Untitled Post"}</h3>
            <p className="opacity-70 mt-1 text-sm">{result.platform}</p>

            <div className="mt-4 text-lg">
              Credibility Score:
              <span className="font-semibold ml-1">
                {result.credibility_score !== null ? result.credibility_score : "N/A"}
              </span>
            </div>

            {result.community_sentiment && (
              <div className="mt-1 opacity-80 text-sm">
                Community Sentiment: {result.community_sentiment}
              </div>
            )}
          </div>
        )}
      </div>
    </motion.section>
  );
}
