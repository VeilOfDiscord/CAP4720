#version 330 core

in vec3 fragNormal;
out vec4 outColour;

void main(){
    vec3 norm = abs(normalize(fragNormal));
    outColour = vec4(norm,1.0);
}