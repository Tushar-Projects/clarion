import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { getTopPosts } from "../api";

export default function SectionTopToday({ source }) {
  const [posts, setPosts] = useState([]);

  useEffect(() => {
    getTopPosts(source).then((data) => {
      if (data && Array.isArray(data.results)) {
        setPosts(data.results);
      }
    });
  }, [source]);

  return (
    <motion.section
      id="top-today"
      className="min-h-screen px-6 py-16 flex justify-center"
      initial={{ opacity: 0, y: 24 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <div className="w-full max-w-5xl space-y-6">
        <h2 className="text-3xl font-semibold mb-4">Top Posts Today</h2>

        {posts.length === 0 && (
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
              className="glass p-5 rounded-2xl flex flex-col md:flex-row md:items-center md:justify-between gap-4"
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
