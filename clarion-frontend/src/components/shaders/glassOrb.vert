// minimal vertex shader: forward position + vNormal + vWorldPos
precision mediump float;
attribute vec3 position;
attribute vec3 normal;

uniform mat4 projectionMatrix;
uniform mat4 modelViewMatrix;
uniform mat4 modelMatrix;
uniform mat3 normalMatrix;

varying vec3 vNormal;
varying vec3 vWorldPos;

void main() {
  vNormal   = normalize(normalMatrix * normal);
  vec4 wPos = modelMatrix * vec4(position, 1.0);
  vWorldPos = wPos.xyz;
  gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
}
