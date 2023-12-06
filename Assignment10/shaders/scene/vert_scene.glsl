#version 420 core

// Attributes
layout (location = 0) in vec3 position;    // we can also use layout to specify the location of the attribute
layout (location = 1) in vec2 uv;
layout (location = 2) in vec3 normal;


// todo: define all the out variables
out vec2 fragUV;
out vec3 fragNormal;
out vec3 fragPosition;
out vec4 fragPosLightSpace;


// todo: define all the uniforms
uniform mat4 modelMatrix;
uniform mat4 view_mat;
uniform mat4 projection_mat;
uniform mat4 lightProjectionMatrix;
uniform mat4 lightViewMatrix;

void main(){
//     todo: fill in vertex shader
    vec4 world_pos = modelMatrix * vec4(position, 1.0);

    fragPosLightSpace = lightProjectionMatrix * lightViewMatrix * world_pos;
    fragPosition = world_pos.xyz;
    gl_Position = projection_mat * view_mat * world_pos;
    fragUV = uv;

    mat4 normal_matrix = transpose(inverse(modelMatrix));
    vec3 new_normal = (normal_matrix*vec4(normal,0)).xyz;
    fragNormal = normalize(new_normal);
}