// soft purple nebula + fresnel glow, transparent core
precision mediump float;

uniform float uTime;
uniform vec3  uBaseColor;   // e.g. purple hue
uniform float uGlow;        // overall glow intensity
uniform vec3  uCamPos;

varying vec3 vNormal;
varying vec3 vWorldPos;

// simple fbm noise
float hash(vec3 p){ return fract(sin(dot(p, vec3(27.1,61.7,12.4))) * 43758.5453); }
float noise(vec3 p){
  vec3 i=floor(p); vec3 f=fract(p);
  float n=dot(i, vec3(1.0,57.0,113.0));
  vec3 u=f*f*(3.0-2.0*f);
  return mix(
    mix(mix(hash(i+vec3(0,0,0)),hash(i+vec3(1,0,0)),u.x),
        mix(hash(i+vec3(0,1,0)),hash(i+vec3(1,1,0)),u.x),u.y),
    mix(mix(hash(i+vec3(0,0,1)),hash(i+vec3(1,0,1)),u.x),
        mix(hash(i+vec3(0,1,1)),hash(i+vec3(1,1,1)),u.x),u.y),u.z);
}
float fbm(vec3 p){
  float v=0.0, a=0.5;
  for(int i=0;i<5;i++){ v+=a*noise(p); p*=2.02; a*=0.5; }
  return v;
}

void main() {
  // view & fresnel
  vec3  V = normalize(uCamPos - vWorldPos);
  float fres = pow(1.0 - max(dot(normalize(vNormal), V), 0.0), 2.2);

  // soft moving nebula inside
  vec3  p = vWorldPos * 0.9 + vec3(0.0, uTime*0.05, 0.0);
  float n = fbm(p*1.2) * 0.75 + fbm(p*2.3)*0.25;

  vec3 nebula = mix(vec3(0.1,0.05,0.12), uBaseColor, n);
  float alpha = 0.38 + 0.25*n + 0.35*fres*uGlow;

  gl_FragColor = vec4(nebula, clamp(alpha, 0.12, 0.95));
}
