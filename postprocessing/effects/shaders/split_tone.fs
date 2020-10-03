#version 330

#define USE_PRECEPTUAL_LUMANINCE
//If disabled, use vector length instead

// Color passed in from the vertex shader
in vec2 v_uv;

// The pixel we are writing to in the framebuffer
out vec4 fragColor;

uniform sampler2D t_source; 

uniform float u_threshold;
uniform float u_crossover_half;
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

    vec3 sourceColor = texture(t_source, v_uv).xyz;

    //Compute the luminance of the color
    float luminance = calculate_lumanince(sourceColor);

    //Use smoothstep to find out where we are in the crossover band centered aroud the threshold.
    //This clamps to 0.0 anywhere past the full shadow side, and 1.0 anywhere past the full highlight side
    float lerpTime = smoothstep(u_threshold - u_crossover_half,u_threshold + u_crossover_half, luminance);

    //Blend the 2 split tone colors together based on where we are in the crossover band, or select 1 if we are fully outside of it
    vec3 splitToneColor = mix(u_shadow_color, u_highlight_color, lerpTime);

    //Add split tone color to original color
    vec3 finalColor = sourceColor + splitToneColor;

    fragColor = vec4(finalColor, 0.0);
}