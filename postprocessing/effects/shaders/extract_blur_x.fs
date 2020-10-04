#version 330

uniform sampler2D t_source;

const int samples = 11;
const int midpoint = samples/2;

uniform float u_weights[11];
uniform float u_weight_sum;
uniform vec2 u_texel_size;

uniform float u_threshold;

in vec2 v_uv;
out vec4 out_color;

void main() 
{
    vec3 color = texture(t_source, v_uv).rgb;

    vec2 sample_pos = v_uv;
    sample_pos.x -= midpoint * u_texel_size.x;

    vec3 final_color = vec3(0.0);

    for(int i = 0; i < samples; i++)
    {
        vec3 sample = texture(t_source, sample_pos).xyz;

        float brightness = max(max(sample.x, sample.y), sample.z);
        float knee = (brightness - u_threshold) / brightness;
        knee = clamp(knee, 0.0, 1.0);
        sample *= knee;

        //Apply guassian weight
        final_color += sample * u_weights[i];
        //Advance sample position
        sample_pos.x += u_texel_size.x;
    }

    //Divide by weight sum to ensure no gain or loss of energy
    final_color /= u_weight_sum;

    out_color = vec4(final_color, 1.0);
}