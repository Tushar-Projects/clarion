// glassOrb.vert
precision highp float;

uniform float uTime;

varying vec3 vWorldPos;
varying vec3 vNormal;
varying vec2 vUv;

void main() {
  vUv = uv;
  vNormal = normalize(normalMatrix * normal);

  // subtle breathing
  float wobble = sin(uTime * 0.8 + position.y * 2.0) * 0.002;
  vec3 pos = position + normal * wobble;

  vec4 world = modelMatrix * vec4(pos, 1.0);
  vWorldPos = world.xyz;

  gl_Position = projectionMatrix * viewMatrix * world;
}
