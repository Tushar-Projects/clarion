import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { getHistory } from "../api";

export default function SectionHistory({ setOrbTint }) {
  const [posts, setPosts] = useState([]);

  useEffect(() => {
    getHistory().then((data) => {
      if (Array.isArray(data)) setPosts(data);
    });
  }, []);

  const getTint = (score) => {
    if (score === null || score === undefined) return "purple";
    if (score < 0) return "red";
    if (score > 0.5) return "gold";
    if (score >= 0.1) return "green";
    return "purple";
  };

  return (
    <motion.section
      id="history"
      className="min-h-screen px-6 py-16 flex justify-center"
      initial={{ opacity: 0, y: 24 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <div className="w-full max-w-5xl space-y-6">
        <h2 className="text-3xl font-semibold mb-4">History</h2>

        {posts.length === 0 && (
          <div className="opacity-70 text-center py-20">
            No posts analyzed yet.
          </div>
        )}

        {posts.map((post) => {
          const redditThread = post.post_id
            ? `https://reddit.com/comments/${post.post_id}`
            : null;

          return (
            <div
              key={post.id}
              className="glass p-5 rounded-2xl flex flex-col md:flex-row md:items-center md:justify-between gap-4 transition-all duration-200 border border-white/25 shadow-[0_0_6px_rgba(0,0,0,0.25)] hover:border-white/85 hover:shadow-[0_0_14px_rgba(255,255,255,0.55)]"
              onMouseEnter={() => setOrbTint?.(getTint(post.advanced_score))}
              onMouseLeave={() => setOrbTint?.("purple")}
            >
              <div className="max-w-2xl">
                <h3 className="font-medium text-lg">{post.title}</h3>
                <p className="text-sm opacity-70 mt-1">Platform: {post.platform}</p>
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
                {redditThread && (
                  <a
                    href={redditThread}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="px-4 py-2 rounded-full glass hover:bg-white/15 transition"
                  >
                    Reddit Thread
                  </a>
                )}

                {post.url && (
                  <a
                    href={post.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="px-4 py-2 rounded-full glass hover:bg-white/15 transition"
                  >
                    Source Article
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
