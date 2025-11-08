export default function Highlights() {
  const items = [
    { title: "Fact Check API", desc: "Google Fact Check integration boosts/penalizes credibility." },
    { title: "Source Reliability", desc: "Per-domain reliability weighting (Reuters, BBC, etc.)." },
    { title: "Community Signals", desc: "Comment-based ‘fake/true’ cues with sarcasm dampening." },
  ];
  return (
    <section className="py-24 bg-transparent">
      <div className="max-w-7xl mx-auto px-6 grid md:grid-cols-3 gap-6">
        {items.map((it) => (
          <div key={it.title} className="glass-card p-6">
            <h3 className="text-xl font-semibold mb-2">{it.title}</h3>
            <p className="opacity-80">{it.desc}</p>
          </div>
        ))}
      </div>
    </section>
  );
}
