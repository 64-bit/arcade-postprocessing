#version 330

// Color passed in from the vertex shader
in vec2 v_uv;

// The pixel we are writing to in the framebuffer
out vec4 fragColor;

uniform sampler2D t_source;

uniform float u_axial;
uniform float u_transverse;

const float u_strength = 0.01;

const int sample_count = 15;
uniform vec3 u_channel_weights [sample_count];
uniform vec3 u_channel_sums;

uniform float u_distance_scale;

void main() 
{

    vec2 direction = v_uv * 2.0 - 1.0;

    float dist = length(direction);
    direction /= dist;

    int stepsPerSide = sample_count / 2;

    vec2 step = direction * dist * u_distance_scale / float(stepsPerSide);
    vec2 samplePos = v_uv - (step * float(stepsPerSide));

    vec3 colorSum = vec3(0.0);
    for(int i = 0; i < sample_count; i++)
    {
        colorSum += texture(t_source, samplePos).rgb * u_channel_weights[i];
        samplePos += step;
    }

    vec3 baseColor = texture(t_source, v_uv).rgb;
    vec3 finalAberration = colorSum / u_channel_sums;

    vec3 finalColor = mix(baseColor, finalAberration, u_axial);
    fragColor = vec4(finalColor, 1.0);
}


/*
    vec3 transverse = vec3(
        texture(t_source, v_uv - vec2(u_strength, 0.0)).r,
        texture(t_source, v_uv).g,
        texture(t_source, v_uv + vec2(u_strength, 0.0)).b
    );

    vec3 axial = vec3(
        texture(t_source, v_uv * 1.01 - 0.005).r,
        texture(t_source, v_uv).g,
        texture(t_source, v_uv * 0.99 + 0.005).b
    );

    vec3 baseColor = texture(t_source, v_uv).rgb;
    float baseFactor = 1.0 - u_axial - u_transverse;

    vec3 finalColor = baseColor * baseFactor + transverse * u_transverse + axial * u_axial;
    fragColor = vec4(finalColor, 1.0);

*/