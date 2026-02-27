#version 330
// Source - https://stackoverflow.com/a/4712625
// Posted by Agnius Vasiliauskas, modified by community. See post 'Timeline' for change history
// Retrieved 2026-02-27, License - CC BY-SA 4.0

uniform ivec2 screen_size;
uniform float cell_size = 50;
uniform vec2 pos = vec2(0.0, 0.0);
out vec4 fragColor;

void main()
{
    // Convert fragment coordinates to world space
    vec2 world_pos = gl_FragCoord.xy + pos;

    // Create grid pattern based on cell_size
    ivec2 cell = ivec2(floor(world_pos.x / cell_size),
            floor(world_pos.y / cell_size));

    // Checkerboard pattern
    bool isEven = mod(float(cell.x + cell.y), 2.0) == 0.0;

    vec4 col1 = vec4(0.0, 0.0, 0.0, 1.0);
    vec4 col2 = vec4(1.0, 1.0, 1.0, 1.0);
    fragColor = isEven ? col1 : col2;
}
