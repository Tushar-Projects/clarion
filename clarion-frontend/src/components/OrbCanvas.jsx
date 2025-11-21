import { Canvas, useFrame } from "@react-three/fiber";
import * as THREE from "three";
import { useRef, useMemo, useEffect } from "react";
import { motion } from "framer-motion";

import glassFrag from "./shaders/glassOrb.frag?raw";
import glassVert from "./shaders/glassOrb.vert?raw";

const COLORS = {
  purple: "#7c3aed",
  red: "#ef4444",
  green: "#22c55e",
  gold: "#eab308",
  white: "#ffffff"
};

function GlitchyOrb({ tint = "purple" }) {
  const mesh = useRef();

  // Stable uniforms
  const uniforms = useMemo(
    () => ({
      uTime: { value: 0 },
      uTint: { value: new THREE.Color(COLORS.purple) },
    }),
    []
  );

  // Target color for lerping
  const targetColor = useRef(new THREE.Color(COLORS.purple));

  // Update target when tint prop changes
  useEffect(() => {
    const hex = COLORS[tint] || COLORS.purple;
    targetColor.current.set(hex);
  }, [tint]);

  useFrame((state) => {
    uniforms.uTime.value = state.clock.getElapsedTime();
    if (mesh.current) mesh.current.rotation.y += 0.003;

    // Smoothly lerp current color to target color
    uniforms.uTint.value.lerp(targetColor.current, 0.05);
  });

  return (
    <mesh ref={mesh}>
      <sphereGeometry args={[1.75, 96, 96]} />
      <shaderMaterial
        vertexShader={glassVert}
        fragmentShader={
          glassFrag.includes("uTint") ? glassFrag : glassFrag + "\n// tint passthrough"
        }
        uniforms={uniforms}
        transparent
        depthWrite={false}
      />
    </mesh>
  );
}

export default function OrbCanvas({
  inCorner = false,
  cornerOffset = { top: 80, right: 80 },
  cornerScale = 0.6,
  onClickCorner,
  tint = "purple",
}) {
  // Variants animation still exists, but we will override via style
  const variants = {
    center: {
      top: "50%",
      left: "50%",
      right: "auto",
      transform: "translate(-50%, -50%) scale(1)",
      transition: { type: "spring", stiffness: 140, damping: 16 },
    },
    corner: {
      top: cornerOffset.top,
      left: "auto",
      right: cornerOffset.right,
      transform: `translate(0, 0) scale(${cornerScale})`,
      transition: { type: "spring", stiffness: 140, damping: 16 },
    },
  };


  return (
    <motion.div
      className="fixed z-[20] pointer-events-auto"
      initial={false}
      animate={inCorner ? "corner" : "center"}
      variants={variants}
      onClick={inCorner ? onClickCorner : undefined}
      style={{
        width: 520,
        height: 520,
        borderRadius: "50%",

        // 🔥 THIS IS THE IMPORTANT PART — force override center vs. corner
        ...(inCorner
          ? {
            position: "fixed",
            top: cornerOffset.top,
            left: "auto",
            right: cornerOffset.right,
            transform: `scale(${cornerScale})`,
            transformOrigin: "top right",
          }
          : {
            top: "50%",
            left: "50%",
            // right: "auto",
            transform: "translate(-50%, -50%) scale(1)",
          }),
      }}
    >
      <Canvas camera={{ position: [0, 0, 5.2], fov: 45 }} gl={{ antialias: true }} resize={{ scroll: false, debounce: 0 }}>
        <ambientLight intensity={0.6} />
        <directionalLight position={[4, 4, 6]} intensity={1.2} />
        <GlitchyOrb tint={tint} />
      </Canvas>
    </motion.div>
  );
}
