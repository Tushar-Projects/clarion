// Map a credibility score in [-1..1] to your palette:
// Red (fake), Blue (medium), Green (authentic), Purple (fully legit)
export function scoreToColor(score) {
  if (score == null) return '#94a3b8'; // slate (unknown)
  if (score <= -0.2) return '#ef4444'; // red
  if (score < 0.35) return '#60a5fa';  // blue
  if (score < 0.8) return '#22c55e';   // green
  return '#a78bfa';                    // purple
}
