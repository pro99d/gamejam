#version 330

uniform vec2 screen_size;
uniform float cell_size;
uniform sampler2D t0;
out vec4 fragColor;

void main() {

    // Calculate the step size in screen coordinates
    float dx = (1.0 / screen_size.x * cell_size);
    float dy = (1.0 / screen_size.y * cell_size);

    // Get the current fragment's UV coordinates
    vec2 FragUV = gl_FragCoord.xy / screen_size;

    // Calculate the texture coordinates
    vec2 Coord = vec2(dx * floor(FragUV.x / dx),
            dy * floor(FragUV.y / dy));

    // Fetch the color from the texture
    fragColor = texture(t0, Coord);
}

