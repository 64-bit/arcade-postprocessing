#version 330

// Color passed in from the vertex shader
in vec2 v_uv;

// The pixel we are writing to in the framebuffer
out vec4 fragColor;

uniform sampler2D t_source; 
uniform float u_whitePoint_2;//Pre squred white point

void main() {

    vec3 hdrColor = texture(t_source, v_uv).xyz;

    vec3 numerator = hdrColor * (1.0 + (hdrColor / u_whitePoint_2));

    //Reinhard tonemapping, basic but works good enough for this
    vec3 ldrColor = numerator / (1.0 + hdrColor);
    fragColor = vec4(ldrColor, 0.0);
}