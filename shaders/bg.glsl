#version 330

uniform vec2 screen_size;
uniform float cell_size = 50;
uniform vec2 pos = vec2(0.0, 0.0);
uniform float zoom=1;
out vec4 fragColor;

const mat2 myt = mat2(.12121212, .13131313, -.13131313, .12121212);
const vec2 mys = vec2(1e4, 1e6);

vec2 rhash(vec2 uv) {
    uv *= myt;
    uv *= mys;
    return fract(fract(uv / mys) * uv);
}

vec3 hash(vec3 p) {
    return fract(sin(vec3(dot(p, vec3(1.0, 57.0, 113.0)),
                dot(p, vec3(57.0, 113.0, 1.0)),
                dot(p, vec3(113.0, 1.0, 57.0)))) *
            43758.5453);
}

float voronoi2d(const in vec2 point) {
    vec2 p = floor(point);
    vec2 f = fract(point);
    float res = 0.0;
    for (int j = -1; j <= 1; j++) {
        for (int i = -1; i <= 1; i++) {
            vec2 b = vec2(i, j);
            vec2 r = vec2(b) - f + rhash(p + b);
            res += 1. / pow(dot(r, r), 8.);
        }
    }
    return pow(1. / res, 0.3625);
}

vec3 mix(vec3 v1, vec3 v2, float a) {
    return v1 * (1 - a) + v2 * a;
}

float get_vor(vec2 dp) {
    vec2 centered = gl_FragCoord.xy - screen_size.xy / 2.0;
    vec2 world_pos = pos + centered / zoom;
    return voronoi2d((world_pos + dp) / 30);
}

float voronoi2d_web(const in vec2 point) {
    vec2 p = floor(point);
    vec2 f = fract(point);
    float res = 1e6;
    vec2 mr;
    for (int j = -1; j <= 1; j++) {
        for (int i = -1; i <= 1; i++) {
            vec2 b = vec2(i, j);
            vec2 r = vec2(b) - f + rhash(p + b);
            float d = dot(r, r);
            if (d < res) {
                res = d;
                mr = r;
            }
        }
    }
    float res2 = 1e6;
    for (int j = -1; j <= 1; j++) {
        for (int i = -1; i <= 1; i++) {
            vec2 b = vec2(i, j);
            vec2 r = vec2(b) - f + rhash(p + b);
            float d = dot(r, r);
            if (abs(d - res) > 1e-5 && d < res2) {
                res2 = d;
            }
        }
    }
    float border = abs(sqrt(res2) - sqrt(res));

    return border < 0.035 ? 1.0 : 0.0;
}
void main()
{
    vec2 centered = gl_FragCoord.xy - screen_size.xy / 2.0;
    vec2 world_pos = pos + centered / zoom;

    ivec2 cell = ivec2(floor(world_pos.x / cell_size),
            floor(world_pos.y / cell_size));

    bool isEven = mod(float(cell.x + cell.y), 2.0) == 0.0;

    vec3 dirt = vec3(0.34, 0.188, 0);
    vec3 col1 = vec3(0.0, 0.0, 0.0);
    vec3 col2 = vec3(1.0, 1.0, 1.0);
    bool isMin = false;

    float vor = voronoi2d_web(world_pos / 30);
    vec3 col = (vor == 1.0) ? vec3(0.0) : dirt;
    float stone_vor = get_vor(vec2(0));
    if (pow(stone_vor, 2) > 0.1) {
        col = vec3(0.5 * pow(stone_vor, 2) - vor);
    }
    col *= 2;
    fragColor = vec4(col, 1.0);
}
