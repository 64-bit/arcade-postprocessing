#version 330

#define USE_PRECEPTUAL_LUMANINCE
//If disabled, use vector length instead

// Color passed in from the vertex shader
in vec2 v_uv;

// The pixel we are writing to in the framebuffer
out vec4 fragColor;

uniform sampler2D t_source; 

uniform float u_strength;
uniform vec3 u_shadow_color;
uniform vec3 u_highlight_color;

const vec3 perceptual_weights = vec3(0.2126, 0.7152, 0.0722);

float calculate_lumanince(vec3 color){
    //Multiply each component of the color by it's perceptual weight, and then add the results together
#ifdef USE_PRECEPTUAL_LUMANINCE
    return dot(color, perceptual_weights);
#else
    return length(color);//Vector legnth probably not the best way to do this :(
#endif
}

void main() {

    vec4 sourceColor = texture(t_source, v_uv);

    //Compute the luminance of the color
    float luminance = clamp(calculate_lumanince(sourceColor.rgb), 0.0, 1.0);

    vec3 greyColor = mix(u_shadow_color, u_highlight_color, luminance);

    //Add split tone color to original color
    vec3 finalColor = mix(sourceColor.rgb, greyColor, u_strength);
    fragColor = vec4(finalColor, sourceColor.a);
}