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

    try {
      const data = await checkPostByUrl(url, false);
      if (data.error) {
        alert(data.error);
      } else {
        console.log("API Response (Check):", data); // Debug log
        setResult(data);
        if (data.url) setUrl(data.url);
      }
    } catch (e) {
      console.error(e);
    }
    setLoading(false);
  };

  const handleRecalculate = async () => {
    if (!url.trim()) return;
    setLoading(true);
    setResult(null);

    try {
      const data = await checkPostByUrl(url, true);
      if (data.error) {
        alert(data.error);
      } else {
        setResult(data);
        if (data.url) setUrl(data.url);
      }
    } catch (e) {
      console.error(e);
    }
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
            <div className="flex justify-between items-start gap-4">
              <div>
                <h3 className="text-xl font-semibold">{result.title || "Untitled Post"}</h3>
                <p className="opacity-70 mt-1 text-sm">{result.platform}</p>
              </div>
              <button
                onClick={handleRecalculate}
                className="text-xs px-3 py-2 rounded-lg border border-white/20 hover:bg-white/10 transition whitespace-nowrap"
              >
                Recalculate
              </button>
            </div>

            {result.previous_result ? (
              <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Old */}
                <div className="p-4 rounded-xl bg-red-500/5 border border-red-500/20">
                  <p className="text-xs uppercase tracking-wider opacity-60 mb-2">Previous Check</p>
                  <div className="text-lg">
                    Score: <span className="font-semibold">{result.previous_result.credibility_score?.toFixed(2) ?? "N/A"}</span>
                  </div>
                  <div className="text-sm opacity-80">
                    Community: {result.previous_result.community_sentiment?.toFixed(2) ?? "N/A"}
                  </div>
                </div>

                {/* New */}
                <div className="p-4 rounded-xl bg-green-500/5 border border-green-500/20">
                  <p className="text-xs uppercase tracking-wider opacity-60 mb-2">New Check</p>
                  <div className="text-lg">
                    Score: <span className="font-semibold">{result.credibility_score?.toFixed(2) ?? "N/A"}</span>
                  </div>
                  <div className="text-sm opacity-80">
                    Community: {result.community_sentiment?.toFixed(2) ?? "N/A"}
                  </div>
                </div>
              </div>
            ) : (
              <>
                <div className="mt-4 text-lg">
                  Credibility Score:
                  <span className="font-semibold ml-1">
                    {result.credibility_score !== null && result.credibility_score !== undefined ? result.credibility_score.toFixed(2) : "N/A"}
                  </span>

                  {/* Verdict Badge */}
                  {result.credibility_score > 0.5 && (
                    <span className="ml-3 px-3 py-1 rounded-full bg-green-500/20 text-green-300 border border-green-500/30 text-sm font-medium">
                      ✅ Verified
                    </span>
                  )}
                  {result.credibility_score < -0.5 && (
                    <span className="ml-3 px-3 py-1 rounded-full bg-red-500/20 text-red-300 border border-red-500/30 text-sm font-medium">
                      ❌ Likely Fake
                    </span>
                  )}
                  {result.credibility_score >= -0.5 && result.credibility_score <= 0.5 && result.credibility_score !== null && (
                    <span className="ml-3 px-3 py-1 rounded-full bg-white/10 text-white/70 border border-white/20 text-sm font-medium">
                      ⚖️ Neutral
                    </span>
                  )}
                </div>

                {result.community_sentiment !== null && (
                  <div className="mt-1 opacity-80 text-sm">
                    Community Sentiment: {result.community_sentiment.toFixed(2)}
                  </div>
                )}

                {/* Reliability Signals */}
                <div className="mt-4 flex flex-wrap gap-2 text-xs">
                  {result.sensationalism_score > 0.6 && (
                    <span className="px-2 py-1 rounded bg-red-500/20 text-red-300 border border-red-500/30">
                      ⚠️ High Sensationalism
                    </span>
                  )}
                  {result.corroboration_score > 0 && (
                    <span className="px-2 py-1 rounded bg-green-500/20 text-green-300 border border-green-500/30">
                      ✅ Corroborated
                    </span>
                  )}
                  {result.platform === "News" && (!result.corroboration_score || result.corroboration_score <= 0) && (
                    <span className="px-2 py-1 rounded bg-yellow-500/20 text-yellow-300 border border-yellow-500/30">
                      ⚠️ Uncorroborated
                    </span>
                  )}
                  {result.image_provenance_status === "recycled" && (
                    <span className="px-2 py-1 rounded bg-red-500/20 text-red-300 border border-red-500/30">
                      ❌ Recycled Image
                    </span>
                  )}
                  {result.llm_verdict && (
                    <div className="w-full mt-2 p-3 rounded bg-white/5 border border-white/10 text-white/80 italic">
                      <span className="block font-semibold not-italic opacity-50 mb-1">AI Verdict:</span>
                      "{result.llm_verdict.reasoning || ""}"
                    </div>
                  )}
                  {result.image_provenance_status === "recycled" && result.score_explanation?.image_provenance && (
                    <div className="w-full mt-2 p-3 rounded bg-red-500/10 border border-red-500/20 text-red-200">
                      <span className="block font-semibold opacity-70 mb-1">Image Provenance:</span>
                      "{result.score_explanation.image_provenance}"
                    </div>
                  )}
                </div>
              </>
            )}
          </div>
        )}
      </div>
    </motion.section>
  );
}
