uniform vec2 u_resolution;

float draw_rectangle(vec2 coord, vec2 dimensions, vec2 offset) {
    vec2 shaper = step(offset, coord);
    shaper *= step(coord, offset + dimensions);

    return shaper.x * shaper.y;
}

void main() {
    vec2 coord = gl_FragCoord.xy / u_resolution;
    float rectangle = draw_rectangle(coord, vec2(0.5, 0.5), vec2(0.25, 0.25));
    vec3 color = vec3(rectangle);

    gl_FragColor = vec4(color, 1.0);
}