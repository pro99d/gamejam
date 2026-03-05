#version 330
// bullet for ammo shader

uniform sampler2D t0;
uniform vec2 screen_size = vec2(1920, 1080);
uniform vec2 start_pos = vec2(0, 0);
uniform int repeat_count = 1;
uniform float reload;
out vec4 fragColor;
#define offset 14
#define bullet_width 12
#define bullet_height 20

void main() {
    vec2 p = gl_FragCoord.xy;
    vec3 color = vec3(0.0);
    float relative_x = p.x - start_pos.x;
    int copy_index = int(floor(relative_x / float(offset)));
    vec2 p_base = p;
    p_base.x = start_pos.x + mod(relative_x, float(offset));

    vec2 st_pos = start_pos;
    vec2 pos_norm = p_base / screen_size;
    vec2 dp = p_base - st_pos;
    bool in_any_copy = false;
    for (int i = 0; i < repeat_count; i++) {
        float copy_x = start_pos.x + float(i) * offset;
        if (p.x >= copy_x && p.x < copy_x + float(bullet_width)) {
            in_any_copy = true;
            break;
        }
    }

    if (in_any_copy) {
        if (dp.x < 0 || dp.y < 0) {
            color = texture(t0, p/screen_size).rgb;
        } else if (dp.x < 12 && dp.y <= 14*reload) {
            color = vec3(0.947, 0.517, 0.077);
        } else if (dp.x > 1 && dp.x < 11 && dp.y < 17*reload) {
            color = vec3(0.947, 0.517, 0.077);
        } else if (dp.x > 2 && dp.x < 10 && dp.y < 19*reload) {
            color = vec3(0.947, 0.517, 0.077);
        } else if (dp.x > 3 && dp.x < 9 && dp.y < 20*reload) {
            color = vec3(0.947, 0.517, 0.077);
        } else {
            color = texture(t0, p/screen_size).rgb;
        }
    } else {
        color = texture(t0, p/screen_size).rgb;
    }

    fragColor = vec4(color, 1.0);
}
