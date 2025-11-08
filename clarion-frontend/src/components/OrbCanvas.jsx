import { Canvas, useFrame } from "@react-three/fiber";
import * as THREE from "three";
import { useRef, useMemo } from "react";
import { motion } from "framer-motion";

import glassFrag from "./shaders/glassOrb.frag?raw";
import glassVert from "./shaders/glassOrb.vert?raw";

function GlitchyOrb({ tint = "purple" }) {
  const mesh = useRef();
  const uniforms = useMemo(() => ({
    uTime: { value: 0 },
    uTint: { value: new THREE.Color(tint === "purple" ? "#7c3aed" : "#ffffff") },
  }), [tint]);

  useFrame((state) => {
    uniforms.uTime.value = state.clock.getElapsedTime();
    if (mesh.current) mesh.current.rotation.y += 0.003;
  });

  return (
    <mesh ref={mesh}>
      <sphereGeometry args={[1.75, 96, 96]} />
      <shaderMaterial
        vertexShader={glassVert}
        fragmentShader={
          // inject a tint if your fragment doesn’t have it
          glassFrag.includes("uTint")
            ? glassFrag
            : glassFrag + "\n// tint mix\n#ifdef GL_ES\nprecision mediump float;\n#endif\n"
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
  fixed = false,
  tint = "purple",
}) {
  const variants = {
    center: {
      top: "50%",
      left: "50%",
      right: "auto",
      transform: "translate(-50%, -50%) scale(1)",
      transition: { type: "spring", stiffness: 160, damping: 22 },
    },
    corner: {
      top: cornerOffset.top,
      left: "auto",
      right: cornerOffset.right,
      transform: `translate(0,0) scale(${cornerScale})`,
      transition: { type: "spring", stiffness: 160, damping: 22 },
    }
  };

  const Wrapper = (props) => (
    <motion.div
      className={`${fixed ? "fixed" : "absolute"} z-[20] pointer-events-auto`}
      style={{ width: 520, height: 520 }}
      initial={false}
      animate={inCorner ? "corner" : "center"}
      variants={variants}
      onClick={inCorner ? onClickCorner : undefined}
      {...props}
    />
  );

  return (
    <Wrapper>
      <Canvas camera={{ position: [0, 0, 5.2], fov: 45 }} gl={{ antialias: true }}>
        <ambientLight intensity={0.6} />
        <directionalLight position={[4, 4, 6]} intensity={1.2} />
        <GlitchyOrb tint={tint} />
      </Canvas>
    </Wrapper>
  );
}
