import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { getTopPosts } from "../api";

export default function SectionTopToday({ source, setOrbTint }) {
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(false);

  const fetchPosts = (force = false) => {
    setLoading(true);
    getTopPosts(source, force)
      .then((data) => {
        if (data && Array.isArray(data.results)) {
          console.log("Received posts:", data.results.map(p => `${p.id}: ${p.title}`));
          setPosts(data.results);
        }
      })
      .catch((err) => console.error("Failed to fetch posts:", err))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchPosts(false);
  }, [source]);

  const getTint = (score) => {
    if (score === null || score === undefined) return "purple";
    if (score < 0) return "red";
    if (score > 0.5) return "gold";
    if (score >= 0.1) return "green";
    return "purple";
  };

  return (
    <motion.section
      id="top-today"
      className="min-h-screen px-6 py-16 flex justify-center"
      initial={{ opacity: 0, y: 24 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <div className="w-full max-w-5xl space-y-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-3xl font-semibold">Top Posts Today</h2>
          <button
            onClick={() => fetchPosts(true)}
            disabled={loading}
            className="px-4 py-2 rounded-lg glass hover:bg-white/10 transition text-sm disabled:opacity-50"
          >
            {loading ? "Refreshing..." : "Refresh"}
          </button>
        </div>

        {posts.length === 0 && !loading && (
          <div className="opacity-70 text-center py-20">
            Fetching posts…
          </div>
        )}

        {posts.map((post) => {
          const redditLink = `https://reddit.com/comments/${post.post_id}`;
          const sourceLink = post.url;

          return (
            <div
              key={post.id}
              className="glass p-5 rounded-2xl flex flex-col md:flex-row md:items-center md:justify-between gap-4 transition-all duration-200 border border-white/25 shadow-[0_0_6px_rgba(0,0,0,0.25)] hover:border-white/85 hover:shadow-[0_0_14px_rgba(255,255,255,0.55)]"
              onMouseEnter={() => setOrbTint?.(getTint(post.advanced_score))}
              onMouseLeave={() => setOrbTint?.("purple")}
            >
              <div className="max-w-2xl">
                <h3 className="font-medium text-lg">{post.title}</h3>
                <p className="text-sm opacity-70 mt-1">
                  Platform: {post.platform}
                </p>

                <p className="text-sm mt-2">
                  <span className="opacity-70">Score:</span>{" "}
                  <span className="font-semibold text-purple-400">
                    {post.advanced_score !== null
                      ? post.advanced_score.toFixed(2)
                      : "N/A"}
                  </span>
                  <span className="mx-2 opacity-40">|</span>
                  <span className="opacity-70">Community:</span>{" "}
                  <span className="font-semibold text-blue-400">
                    {post.community_sentiment !== null && post.community_sentiment !== undefined
                      ? post.community_sentiment.toFixed(2)
                      : "N/A"}
                  </span>
                </p>
              </div>

              <div className="flex gap-3">
                <a
                  href={redditLink}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="px-4 py-2 rounded-full glass hover:bg-white/15 transition"
                >
                  View Reddit Thread
                </a>

                {sourceLink && (
                  <a
                    href={sourceLink}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="px-4 py-2 rounded-full glass hover:bg-white/15 transition"
                  >
                    View Source Article
                  </a>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </motion.section>
  );
}
