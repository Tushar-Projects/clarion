import { useState, useEffect } from "react";
import { motion } from "framer-motion";

// This will call /top-posts from backend
import { getTopPosts } from "../api/index";

export default function SectionTopToday({source}) {
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);

useEffect(() => {
  getTopPosts(source)
    .then((data) => {
      if (Array.isArray(data)) {
        setPosts(data);
      } else if (Array.isArray(data.posts)) {
        setPosts(data.posts);
      } else {
        setPosts([]);
      }
    })
    .catch(() => setPosts([]));
}, [source]);


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
        <h2 className="text-2xl font-semibold mb-4">Top Posts Today</h2>

        {/* Loading state */}
        {loading && <p className="opacity-70">Fetching top posts…</p>}

        {/* No posts */}
        {!loading && posts.length === 0 && (
          <p className="opacity-70">No posts available for today yet.</p>
        )}

        {/* Posts List */}
        <div className="mt-4 space-y-4">
          {posts.map((post) => (
            <motion.div
              key={post.id}
              whileHover={{ scale: 1.02 }}
              className="p-4 rounded-2xl border border-white/20 bg-white/60 dark:bg-black/30 backdrop-blur cursor-pointer transition"
            >
              <h3 className="font-semibold text-lg">{post.title}</h3>
              <p className="opacity-70 text-sm mt-1">{post.platform}</p>

              <div className="mt-2 text-sm">
                Credibility Score:
                <span className="font-semibold ml-1">
                  {post.credibility_score ?? "N/A"}
                </span>
              </div>

              {post.community_sentiment && (
                <div className="opacity-80 text-xs mt-1">
                  Community Sentiment: {post.community_sentiment}
                </div>
              )}
            </motion.div>
          ))}
        </div>
      </div>
    </motion.section>
  );
}
