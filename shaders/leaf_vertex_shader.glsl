#version 330 core
layout (location = 0) in vec3 aPos;
layout (location = 1) in vec2 aTexCoord;
layout (location = 2) in vec4 aColor;
layout (location = 3) in vec3 aOffset;
layout (location = 4) in float aScale;
layout (location = 5) in float aRotation;

out vec2 TexCoord;
out vec4 Color;

uniform mat4 view;
uniform mat4 projection;

void main() {
    float rad = radians(aRotation);
    mat2 rotation = mat2(
        cos(rad), -sin(rad),
        sin(rad), cos(rad)
    );
    
    vec2 rotated = rotation * aPos.xz;
    vec3 pos = vec3(rotated.x, aPos.y, rotated.y);
    pos = pos * aScale + aOffset;
    
    gl_Position = projection * view * vec4(pos, 1.0);
    TexCoord = aTexCoord;
    Color = aColor;
}