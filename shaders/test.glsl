#version 330
// bullet for ammo shader

uniform sampler2D t0;
uniform vec2 screen_size = vec2(1920, 1080);
uniform vec2 start_pos = vec2(10, 0);
uniform int repeat_time = 2;
out vec4 fragColor;
#define offset 25
void main() {
    vec2 pos;
    vec2 pos_norm;
    vec2 p = gl_FragCoord.xy;
    vec2 st_pos = start_pos;
    vec3 color;
    vec2 dp;
    for (int i = 0; i < repeat_time; i++) {
        p.x += i * offset;
        st_pos.x += i * offset;
        pos = p;
        pos_norm = p / screen_size;
        dp = p - st_pos;
        if (dp.x < 0 || dp.y < 0) {
            color = texture(t0, pos_norm).rgb;
        } else if (dp.x < 12 && dp.y <= 14) {
            color = vec3(0.947, 0.517, 0.077);
        } else if (dp.x > 1 && dp.x < 11 && dp.y < 17) {
            color = vec3(0.947, 0.517, 0.077);
        } else if (dp.x > 2 && dp.x < 10 && dp.y < 19) {
            color = vec3(0.947, 0.517, 0.077);
        } else if (dp.x > 3 && dp.x < 9 && dp.y < 20) {
            color = vec3(0.947, 0.517, 0.077);
        }
        else {
            color = texture(t0, pos_norm).rgb;
        }
    }
    fragColor = vec4(color, 1);
}
