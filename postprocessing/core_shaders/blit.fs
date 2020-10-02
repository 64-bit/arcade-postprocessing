#version 330

uniform sampler2D t_source;

in vec2 v_uv;
out vec4 out_color;

void main() {
    vec4 color = texture(t_source, v_uv);
    out_color = color;
}