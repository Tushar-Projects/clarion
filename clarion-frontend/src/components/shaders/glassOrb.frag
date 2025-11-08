// glassOrb.frag
precision highp float;

uniform float uTime;
uniform vec3 uTint;           // inner tint (your purple)
uniform float uRefraction;    // subtle refraction strength (we will reduce its influence)

varying vec3 vWorldPos;
varying vec3 vNormal;
varying vec2 vUv;

// cheap hash noise
float hash(vec3 p) {
  p = fract(p * 0.3183099 + vec3(0.1, 0.2, 0.3));
  p *= 17.0;
  return fract(p.x * p.y * p.z * (p.x + p.y + 0.1));
}

float fbm(vec3 p) {
  float a = 0.0;
  float f = 1.0;
  for (int i = 0; i < 5; i++) {
    a += hash(p * f) / f;
    f *= 2.0;
  }
  return a;
}

void main() {
  vec3 N = normalize(vNormal);
  vec3 V = normalize(cameraPosition - vWorldPos);

  // nebula motion → slowed slightly for calm breathing feel
  float n = fbm(vWorldPos * 0.85 + vec3(0.0, uTime * 0.05, 0.0));
  vec3 inner = mix(vec3(0.92, 0.86, 1.0), uTint, smoothstep(0.25, 0.9, n));

  // smoother fresnel — FIX for black edge issues
  float fres = pow(1.0 - max(dot(N, V), 0.0), 2.2);

  // soft highlight
  vec3 L = normalize(vec3(0.4, 0.7, 0.5));
  float spec = pow(max(dot(reflect(-L, N), V), 0.0), 20.0) * 0.25;

  // softer refraction so the orb does NOT blow out white
  float refr = mix(0.0, 1.0, fres) * (uRefraction * 0.45);

  vec3 col = inner + vec3(spec);
  col = mix(col, vec3(1.0), refr * 0.25);

  // smooth glass transparency — FIX for harsh bloom
  float alpha = smoothstep(0.08, 0.9, fres) * 0.28 + 0.55;

  // Prevent black crush + ensure soft purple always visible
  col = max(col, vec3(0.05)); 

  gl_FragColor = vec4(col, alpha);
}
