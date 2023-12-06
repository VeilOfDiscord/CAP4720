#version 420 core

// todo: define all the input variables to the fragment shader
in vec3 fragNormal;
in vec3 fragPosition;
in vec2 fragUV;
in vec4 fragPosLightSpace;

// todo: define all the uniforms
uniform vec3 lightPosition;
uniform vec3 eye_pos;
uniform vec3 matColour;

layout (binding=0) uniform sampler2D depthTex;  // depth texture bound to texture unit 0
out vec4 outColor;

void main(){
    // todo: fill in the fragment shader
    vec3 N = normalize(fragNormal);
    vec3 L = normalize(lightPosition.xyz-fragPosition); // point light

    vec3 fragPos3D = fragPosLightSpace.xyz / fragPosLightSpace.w;
    fragPos3D = (fragPos3D + 1.0) / 2.0;

    float z_current = fragPos3D.z;
    float z_depthTex = texture(depthTex, fragPos3D.xy).r;

    vec3 res;
    float bias = max(0.0005f * (1.0 - dot(fragNormal, L)), 0.0001f);

    if(z_current - bias > z_depthTex)
    {
        res  = vec3(0,0,0) * clamp(dot(L,N), 0.0,1.0); // <---- Shadow
    }
    else
    {
        res = matColour * clamp(dot(N,L), 0.0,1.0); // <----- Everything else
    }
    outColor = vec4(res, 1.0);
}