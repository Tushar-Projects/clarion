import { Canvas, useFrame, useThree } from "@react-three/fiber";
import { Environment } from "@react-three/drei";
import * as THREE from "three";
import { useMemo, useRef, useEffect } from "react";

// import shaders (ensure files exist exactly with these names)
import glassFrag from "./shaders/glassOrb.frag?raw";
import glassVert from "./shaders/glassOrb.vert?raw";

function useGlobalPointer() {
  const { pointer } = useThree();
  const eased = useRef({ x: 0, y: 0 });
  useFrame(() => {
    // gentle easing for the BMW-style parallax
    eased.current.x += (pointer.x - eased.current.x) * 0.05;
    eased.current.y += (pointer.y - eased.current.y) * 0.05;
  });
  return eased;
}

function ParallaxRig({ children }) {
  const grp = useRef();
  const eased = useGlobalPointer();
  useFrame(() => {
    if (!grp.current) return;
    grp.current.rotation.y = eased.current.x * 0.8; // wider range
    grp.current.rotation.x = -eased.current.y * 0.5;
  });
  return <group ref={grp}>{children}</group>;
}

// Inner nebula core (custom shader)
function NebulaCore() {
  const mat = useRef();
  const { camera } = useThree();

  const uniforms = useMemo(
    () => ({
      uTime: { value: 0 },
      uBaseColor: { value: new THREE.Color("#8b5cf6").toArray() && new THREE.Color("#8b5cf6") },
      uGlow: { value: 1.0 },
      uCamPos: { value: new THREE.Vector3() },
    }),
    []
  );

  useFrame((state) => {
    uniforms.uTime.value = state.clock.getElapsedTime();
    uniforms.uCamPos.value.copy(camera.position);
  });

  return (
    <mesh>
      <sphereGeometry args={[1.15, 96, 96]} />
      <shaderMaterial
        ref={mat}
        vertexShader={glassVert}
        fragmentShader={glassFrag}
        uniforms={uniforms}
        transparent
        depthWrite={false}
        blending={THREE.NormalBlending}
      />
    </mesh>
  );
}

// Outer glass shell
function GlassShell() {
  return (
    <mesh>
      <sphereGeometry args={[1.2, 96, 96]} />
      <meshPhysicalMaterial
        transparent
        transmission={1}
        ior={1.45}
        thickness={1.4}
        roughness={0.08}
        clearcoat={1}
        clearcoatRoughness={0.08}
        metalness={0.0}
        reflectivity={0.5}
        attenuationColor={"#b19cff"}
        attenuationDistance={1.5}
      />
    </mesh>
  );
}

function FloatingGroup() {
  const ref = useRef();
  useFrame(({ clock }) => {
    const t = clock.getElapsedTime();
    if (!ref.current) return;
    ref.current.position.y = Math.sin(t * 1.2) * 0.08;
  });
  return (
    <group ref={ref}>
      <NebulaCore />
      <GlassShell />
    </group>
  );
}

export default function OrbCanvas() {
  return (
    <div className="w-full h-[80vh] md:h-[88vh] pointer-events-auto">
      <Canvas
        camera={{ position: [0, 0, 4.2], fov: 45 }}
        gl={{ antialias: true }}
        onCreated={({ gl }) => {
          gl.toneMapping = THREE.ACESFilmicToneMapping;
          gl.outputColorSpace = THREE.SRGBColorSpace;
          gl.physicallyCorrectLights = true;
        }}
      >
        {/* studio lights */}
        <ambientLight intensity={0.45} />
        <directionalLight position={[5, 6, 6]} intensity={1.1} />
        <directionalLight position={[-6, -3, -5]} intensity={0.4} />

        <Environment preset="studio" />

        <ParallaxRig>
          <FloatingGroup />
        </ParallaxRig>
      </Canvas>
    </div>
  );
}
