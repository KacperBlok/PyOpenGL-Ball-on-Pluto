from OpenGL.GL import *
import numpy as np
import glm

class ShadowMapping:
    def __init__(self, width=1024, height=1024):
        self.width = width
        self.height = height
        self.depth_map_fbo = None
        self.depth_map_texture = None
        self.shadow_shader = None
        
        # Light parameters for shadows
        self.light_position = glm.vec3(0.0, 10.0, 0.0)
        self.light_direction = glm.normalize(glm.vec3(0.2, -1.0, 0.3))
        
        # Light matrices
        self.light_projection = glm.ortho(-20.0, 20.0, -20.0, 20.0, 1.0, 30.0)
        self.light_view = glm.lookAt(
            self.light_position,
            self.light_position + self.light_direction,
            glm.vec3(0.0, 1.0, 0.0)
        )
        self.light_space_matrix = self.light_projection * self.light_view
        
        self.initialize()
        
    def initialize(self):
        # Creating the depth map texture
        self.depth_map_texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.depth_map_texture)
        glTexImage2D(
            GL_TEXTURE_2D, 0, GL_DEPTH_COMPONENT,
            self.width, self.height, 0, GL_DEPTH_COMPONENT, GL_FLOAT, None
        )
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_BORDER)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_BORDER)
        border_color = [1.0, 1.0, 1.0, 1.0]
        glTexParameterfv(GL_TEXTURE_2D, GL_TEXTURE_BORDER_COLOR, border_color)
        
        # Creating the framebuffer
        self.depth_map_fbo = glGenFramebuffers(1)
        glBindFramebuffer(GL_FRAMEBUFFER, self.depth_map_fbo)
        glFramebufferTexture2D(
            GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_TEXTURE_2D, 
            self.depth_map_texture, 0
        )
        glDrawBuffer(GL_NONE)
        glReadBuffer(GL_NONE)
        glBindFramebuffer(GL_FRAMEBUFFER, 0)
    
    def start_shadow_pass(self):
        """Starts the shadow rendering pass"""
        glViewport(0, 0, self.width, self.height)
        glBindFramebuffer(GL_FRAMEBUFFER, self.depth_map_fbo)
        glClear(GL_DEPTH_BUFFER_BIT)
    
    def end_shadow_pass(self, window_width, window_height):
        """Ends the shadow rendering pass"""
        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        glViewport(0, 0, window_width, window_height)
    
    def bind_shadow_map(self, shader_program, texture_unit=3):
        """Binds the shadow map to the shader"""
        glActiveTexture(GL_TEXTURE0 + texture_unit)
        glBindTexture(GL_TEXTURE_2D, self.depth_map_texture)
        # Set uniforms for the shader
        shader_program.set_mat4("lightSpaceMatrix", self.light_space_matrix)
        shader_program.set_int("shadowMap", texture_unit)
