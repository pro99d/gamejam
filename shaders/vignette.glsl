#version 330

uniform vec2 screen_size;
uniform sampler2D t0;
uniform float alpha = 1.0;
uniform float inner_radius = 0.0;
uniform float outer_radius = 1.0;

out vec4 fragColor;

void main() {
    vec2 UV = gl_FragCoord.xy / screen_size;
    vec4 i = texture(t0, UV);
    float x = abs(UV.r - .5) * 2.0;
    float y = abs(UV.g - .5) * 2.0;
    float q = 1.0 - (1.0 - sqrt(x * x + y * y) / outer_radius) / (1.0 - inner_radius);
    fragColor = vec4(i.x - q, i.y - q, i.z - q, q * alpha);
}
