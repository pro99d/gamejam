#version 330

uniform float size = 100.0;
uniform vec3 bg_color = vec3(0.0);
uniform vec3 grid_color = vec3(1.0);
uniform vec2 pos = vec2(0.0);
uniform vec2 u_resolution = vec2(1920.0, 1080.0);

out vec4 fragColor;

void main() {
    vec2 frag = gl_FragCoord.xy;
    vec2 cell = vec2(size);
    vec2 p = mod(frag + pos, cell);
    float lineWidth = .5;
    float distX = min(p.x, cell.x - p.x);
    float distY = min(p.y, cell.y - p.y);
    float d = min(distX, distY);
    float antiAlias = 1.5;
    float t = smoothstep(lineWidth, lineWidth + antiAlias, d);

    // Mix colors: grid_color near lines (t=0), bg_color elsewhere (t=1)
    vec3 col = mix(grid_color, bg_color, t);

    gl_FragColor = vec4(col, 1.0);
}
