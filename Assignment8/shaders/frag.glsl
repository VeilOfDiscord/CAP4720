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
uniform bool sil;

vec3 computeToon1(vec3 N, vec3 L){
      float intensity = dot(L, N);

      if(intensity > 0.85){intensity = 1;}
      else if(intensity > 0.5 && intensity < 0.85){intensity = 0.7;}
      else if(intensity > 0.25 && intensity < 0.5){intensity = 0.5;}
      else if(intensity > 0.1 && intensity < 0.25){intensity = 0.3;}
      else if(intensity < 0.1){intensity = 0.1;}

      return material_color * intensity;
}

vec3 computeToon2(vec3 L, vec3 N){
      float intensity = clamp(dot(L, N), 0 ,1);
      int n = 4;

      float step = sqrt(intensity) * n;
      intensity = (floor(step) + smoothstep(0.48, 0.52, fract(step))) / n;
      intensity = intensity * intensity;

      return material_color * intensity;
}


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
      vec3 L; //Light_dir
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
      else if(ID == 4) //Toon Shading
      {
            res = computeToon2(N, L);
            if(sil == true && dot(N, normalize(eye_pos-fragPosition)) < 0.2)
            {
                  res = vec3(0,0,0);
            }

      }

      outColor = vec4(res, 1.0);
}