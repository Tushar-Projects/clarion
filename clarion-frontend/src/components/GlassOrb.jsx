import { useEffect, useRef, useState } from "react";
import { motion, useMotionValue, useTransform, animate } from "framer-motion";

// Map credibility → glow colors (you can tweak)
function scoreToGradient(score = 0.0) {
  // clamp
  const s = Math.max(-1, Math.min(1, score));
  // -1 (red) → 0 (blue/green) → 1 (purple)
  if (s <= -0.3) {
    return { inner: "#ff3b3b", mid: "#ff6b6b", outer: "#ffb3b3" }; // fake
  } else if (s < 0.3) {
    return { inner: "#28c76f", mid: "#7bed9f", outer: "#c8ffe0" }; // plausible/green
  } else if (s < 0.8) {
    return { inner: "#3bb3ff", mid: "#8ad0ff", outer: "#d6ecff" }; // medium/blue
  } else {
    return { inner: "#865DFF", mid: "#C09BFF", outer: "#E8D9FF" }; // verified/purple
  }
}

export default function GlassOrb({ size = 380, score = 0.0, floating = true }) {
  const canvasRef = useRef(null);
  const [grad, setGrad] = useState(scoreToGradient(score));

  // subtle parallax based on mouse
  const rotX = useMotionValue(0);
  const rotY = useMotionValue(0);
  const tiltX = useTransform(rotY, [-30, 30], [8, -8]);
  const tiltY = useTransform(rotX, [-30, 30], [-8, 8]);

  useEffect(() => {
    // animate gradient when score changes
    const from = grad;
    const to = scoreToGradient(score);
    const controls = animate(0, 1, {
      duration: 0.6,
      onUpdate: (v) => {
        // quick lerp in HSL space would be nicer; for simplicity, snap halfway
        if (v > 0.5) setGrad(to);
      },
    });
    return () => controls.stop();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [score]);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    let raf;

    const draw = () => {
      const w = canvas.width;
      const h = canvas.height;
      const cx = w / 2;
      const cy = h / 2;
      const r = Math.min(w, h) * 0.45;

      ctx.clearRect(0, 0, w, h);

      // Base glow
      const g = ctx.createRadialGradient(cx, cy, r * 0.2, cx, cy, r);
      g.addColorStop(0, grad.inner);
      g.addColorStop(0.55, grad.mid);
      g.addColorStop(1, "rgba(255,255,255,0)");

      ctx.fillStyle = g;
      ctx.beginPath();
      ctx.arc(cx, cy, r, 0, Math.PI * 2);
      ctx.fill();

      // Glass highlight
      const hlg = ctx.createLinearGradient(cx - r, cy - r, cx + r, cy + r);
      hlg.addColorStop(0, "rgba(255,255,255,0.35)");
      hlg.addColorStop(0.5, "rgba(255,255,255,0.08)");
      hlg.addColorStop(1, "rgba(255,255,255,0)");

      ctx.fillStyle = hlg;
      ctx.beginPath();
      ctx.ellipse(cx - r * 0.18, cy - r * 0.22, r * 0.55, r * 0.38, -0.6, 0, Math.PI * 2);
      ctx.fill();

      // subtle rim light
      ctx.strokeStyle = "rgba(255,255,255,0.20)";
      ctx.lineWidth = 1.2;
      ctx.beginPath();
      ctx.arc(cx, cy, r - 0.5, 0, Math.PI * 2);
      ctx.stroke();

      raf = requestAnimationFrame(draw);
    };

    // setup
    canvas.width = size * 2;   // hi-dpi
    canvas.height = size * 2;
    canvas.style.width = `${size}px`;
    canvas.style.height = `${size}px`;

    draw();
    return () => cancelAnimationFrame(raf);
  }, [grad, size]);

  function onMouseMove(e) {
    const rect = e.currentTarget.getBoundingClientRect();
    const mx = e.clientX - rect.left - rect.width / 2;
    const my = e.clientY - rect.top - rect.height / 2;
    rotX.set(mx / (rect.width / 2) * 30);
    rotY.set(my / (rect.height / 2) * 30);
  }

  return (
    <motion.div
      onMouseMove={onMouseMove}
      className="relative"
      style={{
        rotateX: tiltY,
        rotateY: tiltX,
        transformStyle: "preserve-3d"
      }}
      animate={floating ? { y: [0, -6, 0] } : {}}
      transition={floating ? { duration: 4, repeat: Infinity, ease: "easeInOut" } : {}}
    >
      {/* soft glow behind */}
      <div
        className="absolute inset-0 blur-3xl opacity-60"
        style={{
          background: `radial-gradient( circle at 50% 50%, ${grad.mid}, transparent 60% )`,
          transform: "scale(1.15)"
        }}
      />
      <canvas
        ref={canvasRef}
        className="relative z-10 rounded-full shadow-glow"
        aria-label="Clarion credibility orb"
      />
    </motion.div>
  );
}
