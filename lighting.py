import glm

class Light:
    def __init__(self, position, color, direction=None, ambient_strength=0.2):
        self.position = glm.vec3(position)
        self.color = glm.vec3(color)
        self.direction = glm.vec3(direction) if direction else glm.vec3(0.0, -1.0, 0.0)
        self.ambient_strength = ambient_strength
        self.is_active = False
        self.is_directional = False

    def set_uniforms(self, shader_program, index):
        if self.is_active:
            shader_program.set_vec3(f"lights[{index}].position", self.position)
            shader_program.set_vec3(f"lights[{index}].color", self.color)
            shader_program.set_float(f"lights[{index}].ambient_strength", self.ambient_strength)
            shader_program.set_bool(f"lights[{index}].is_directional", self.is_directional)
            shader_program.set_vec3(f"lights[{index}].direction", self.direction)