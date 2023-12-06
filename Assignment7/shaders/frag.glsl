#version 330 core

out vec4 outColor;

in vec3 fragNormal;
in vec3 fragPosition;

uniform vec4 light_pos;
uniform vec3 eye_pos;
uniform float ID;
uniform vec3 material_color;

uniform vec3 specular_color;
uniform int shininess;
uniform float ambient_intensity;
uniform float K_s;

vec3 computeDiffuse(vec3 N, vec3 L){
      return material_color * clamp(dot(L,N), 0.0,1.0);
}

vec3 computeSpecular(vec3 N, vec3 L, vec3 half_vector){
      return specular_color * pow(clamp(dot(N, half_vector), 0, 1), shininess);
}

vec3 computeDiffAndSpec(vec3 N, vec3 L, vec3 color_ambient_light, vec3 half_vector){
      return color_ambient_light + computeDiffuse(N,L) + K_s * computeSpecular(N,L, half_vector);
}

void main(){
      vec3 N = normalize(fragNormal);
      vec3 L;
      if (light_pos.w==0.0)   L = normalize(light_pos.xyz);                   // directional light
      else                    L = normalize(light_pos.xyz-fragPosition);      // point light


      vec3 res;
      if(ID == 1) //Diffuse Material
      {
            res = computeDiffuse(N, L);
      }
      else if(ID == 2) //Specular Material
      {
            vec3 V = normalize(eye_pos - fragPosition);
            vec3 half_vector = normalize(L + V);

            res = computeSpecular(N,L, half_vector);
      }
      else if(ID == 3) //Both
      {
            vec3 V = normalize(eye_pos - fragPosition);
            vec3 half_vector = normalize(L + V);
            vec3 color_ambient_light = ambient_intensity * material_color;

            res = computeDiffAndSpec(N,L, color_ambient_light, half_vector);
      }
      outColor = vec4(res, 1.0);
}