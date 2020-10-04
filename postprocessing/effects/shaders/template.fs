#version 330

// Color passed in from the vertex shader
in vec2 v_uv;

// The pixel we are writing to in the framebuffer
out vec4 fragColor;

uniform sampler2D t_source;


void main() {

    vec4 sourceColor = texture(t_source, v_uv);


    fragColor = sourceColor;
}