#version 420 core

out vec4 outColor;

in vec3 fragNormal;
in vec3 fragPosition;

uniform float metallic;
uniform int material_type;
uniform float roughness;

uniform vec4 light_pos;
uniform vec3 eye_pos;

uniform float ambient_intensity;

vec3 fresnel(vec3 V, vec3 H){ //Calculate Fresnel Term F
      vec3 F0Die = vec3(0.04);
      vec3 F0Metallic;
      if(material_type == 0)
      {F0Metallic = vec3(0.56,0.57,0.58);}
      else if(material_type == 1)
      {F0Metallic = vec3(0.95,0.64,0.54);}
      else if(material_type == 2)
      {F0Metallic = vec3(1.00,0.71,0.29);}
      else if(material_type == 3)
      {F0Metallic = vec3(0.91,0.92,0.92);}
      else if(material_type == 4)
      {F0Metallic = vec3(0.95,0.93,0.88);}



      vec3 F0 = mix(F0Die, F0Metallic, metallic); //F0 Metal depends on choice. Metallic slider.
      return F0 + (1-F0) * pow(1-dot(V, H),5);
}

vec3 distributionfunc(vec3 N, vec3 H){ //Calculate Microfacet Distribution Function D
      return vec3(pow(roughness,2)/pow(3.142 * (pow(dot(N,H),2)*pow(roughness,2)-1.0)+1.0,2));
}

vec3 geometric(vec3 N, vec3 V, vec3 L){ //Calculate Geometric Attenuation Factor G
      float k = (roughness) / 2;
      float Gv = dot(N, V) / (dot(N, V) * (1 - k) + k);
      float Gl = dot(N, L) / (dot(N, L) * (1 - k) + k);
      return vec3(Gv * Gl);
}

vec3 computeMicrofacet(vec3 N, vec3 V, vec3 H, vec3 L){
      return fresnel(V,H) * distributionfunc(N, H) * geometric(N,V,L);
}

vec3 computeDiffuse(vec3 F, vec3 N, vec3 L){
      vec3 Kd = 1-F;
      return vec3(Kd * (1-metallic) * (1.0,1.0,1.0) * max(dot(N, L), 0));
}

void main(){
//      N: normal vector
      vec3 N = normalize(fragNormal);
//      L: light vector
      vec3 L = normalize(light_pos.xyz-fragPosition);
//      V: view vector
      vec3 V = normalize(eye_pos - fragPosition);
//      H: half vector
      vec3 H = normalize(L + V);

      vec3 ambientColor = ambient_intensity * vec3(0.5,0.2,0.5);

      vec3 specularColor = computeMicrofacet(N, L, V, H) * vec3(1.0);

      vec3 diffuseColor = computeDiffuse(fresnel(V, H),N,L);

      outColor = vec4(ambientColor + diffuseColor + specularColor,1.0);
}













