#version 330 core
const int MAX_LIGHTS = 4;

struct Light {
    vec3 position;
    vec3 color;
    float ambient_strength;
    bool is_directional;
    vec3 direction;
};

struct Material {
    float shininess;
    vec3 ambient;
    vec3 diffuse;
    vec3 specular;
};

in vec3 FragPos;
in vec3 Normal;
in vec2 TexCoord;
in vec4 FragPosLightSpace;
in vec3 WorldPos;

out vec4 FragColor;

uniform Light lights[MAX_LIGHTS];
uniform Material material;
uniform vec3 viewPos;
uniform sampler2D texture1;
uniform sampler2D shadowMap;
uniform samplerCube skybox;
uniform int lightingModel;
uniform bool use_lighting;
uniform int active_lights;
uniform int current_object;
uniform int hummingbird_effect;
uniform float refraction_index;

float ShadowCalculation(vec4 fragPosLightSpace, float bias)
{
    vec3 projCoords = fragPosLightSpace.xyz / fragPosLightSpace.w;
    projCoords = projCoords * 0.5 + 0.5;
    float closestDepth = texture(shadowMap, projCoords.xy).r;
    float currentDepth = projCoords.z;
    
    float shadow = 0.0;
    vec2 texelSize = 1.0 / textureSize(shadowMap, 0);
    for(int x = -1; x <= 1; ++x) {
        for(int y = -1; y <= 1; ++y) {
            float pcfDepth = texture(shadowMap, projCoords.xy + vec2(x, y) * texelSize).r;
            shadow += currentDepth - bias > pcfDepth ? 1.0 : 0.0;
        }
    }
    shadow /= 9.0;
    
    if(projCoords.z > 1.0)
        shadow = 0.0;
        
    return shadow;
}

vec3 calculateLight(Light light, vec3 norm, vec3 viewDir)
{
    vec3 lightDir;
    float attenuation;
    
    if(light.is_directional) {
        lightDir = normalize(-light.direction);
        attenuation = 1.0;
    } else {
        lightDir = normalize(light.position - FragPos);
        float distance = length(light.position - FragPos);
        attenuation = 100.0 / (distance * distance);
    }

    float bias = max(0.05 * (1.0 - dot(norm, lightDir)), 0.005);
    float shadow = ShadowCalculation(FragPosLightSpace, bias);
    
    vec3 ambient = light.ambient_strength * light.color * material.ambient;
    
    float diff = max(dot(norm, lightDir), 0.0);
    vec3 diffuse = diff * light.color * material.diffuse * attenuation;
    
    vec3 specular;
    if(lightingModel == 0) {
        vec3 reflectDir = reflect(-lightDir, norm);
        float spec = pow(max(dot(viewDir, reflectDir), 0.0), material.shininess);
        specular = spec * light.color * material.specular * attenuation;
    } else {
        vec3 halfwayDir = normalize(lightDir + viewDir);
        float spec = pow(max(dot(norm, halfwayDir), 0.0), material.shininess);
        specular = spec * light.color * material.specular * attenuation;
    }
    
    return ambient + (1.0 - shadow) * (diffuse + specular);
}

void main()
{
    if(current_object == 1) {  // Koliber
        if(hummingbird_effect == 1) {  // Efekt lustrzany
            vec3 I = normalize(FragPos - viewPos);
            vec3 R = reflect(I, normalize(Normal));
            FragColor = vec4(texture(skybox, R).rgb, 1.0);
            return;
        }
        else if(hummingbird_effect == 2) {  // Efekt załamania
            float ratio = 1.00 / refraction_index;
            vec3 I = normalize(FragPos - viewPos);
            vec3 R = refract(I, normalize(Normal), ratio);
            FragColor = vec4(texture(skybox, R).rgb, 1.0);
            return;
        }
    }

    vec4 texColor = texture(texture1, TexCoord);
    if(!use_lighting) {
        FragColor = texColor;
        return;
    }

    vec3 norm = normalize(Normal);
    vec3 viewDir = normalize(viewPos - FragPos);
    
    vec3 result = vec3(0.0);
    for(int i = 0; i < active_lights && i < MAX_LIGHTS; i++) {
        result += calculateLight(lights[i], norm, viewDir);
    }
    
    FragColor = vec4(result * texColor.rgb, texColor.a);
}