from OpenGL.GL import *
import numpy as np
import glm
import ctypes
from PIL import Image

class CSkyBox:
    def __init__(self, shader_program):
        """Initialize SkyBox with multiple cubemaps"""
        self.shader_program = shader_program
        self.current_texture = 0
        self.textures = []
        
        # Setup both cubemap sets
        self.setup_cubemap("skybox1")  # First set
        self.setup_cubemap("skybox3")  # Second set
        self.setup_cubemap("skybox")  # third set

        
        self.vao = self._setup_mesh()

    def setup_cubemap(self, folder):
        """Setup cubemap textures from specified folder"""
        texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_CUBE_MAP, texture)

        # Load and set up each face of the cubemap
        faces = [
            f"{folder}/posx.jpg",  # Right
            f"{folder}/negx.jpg",  # Left
            f"{folder}/posy.jpg",  # Top
            f"{folder}/negy.jpg",  # Bottom
            f"{folder}/posz.jpg",  # Front
            f"{folder}/negz.jpg"   # Back
        ]

        for i, face in enumerate(faces):
            try:
                image = Image.open(face)
                img_data = np.array(image.convert("RGB"), dtype=np.uint8)
                glTexImage2D(
                    GL_TEXTURE_CUBE_MAP_POSITIVE_X + i,
                    0, GL_RGB, image.width, image.height, 
                    0, GL_RGB, GL_UNSIGNED_BYTE, img_data
                )
            except Exception as e:
                print(f"Failed to load cubemap texture {face}: {e}")
                return None

        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_R, GL_CLAMP_TO_EDGE)

        self.textures.append(texture)

    def _setup_mesh(self):
        """Setup skybox cube vertices"""
        vertices = np.array([
            # positions          
            -1.0,  1.0, -1.0,
            -1.0, -1.0, -1.0,
             1.0, -1.0, -1.0,
             1.0, -1.0, -1.0,
             1.0,  1.0, -1.0,
            -1.0,  1.0, -1.0,

            -1.0, -1.0,  1.0,
            -1.0, -1.0, -1.0,
            -1.0,  1.0, -1.0,
            -1.0,  1.0, -1.0,
            -1.0,  1.0,  1.0,
            -1.0, -1.0,  1.0,

             1.0, -1.0, -1.0,
             1.0, -1.0,  1.0,
             1.0,  1.0,  1.0,
             1.0,  1.0,  1.0,
             1.0,  1.0, -1.0,
             1.0, -1.0, -1.0,

            -1.0, -1.0,  1.0,
            -1.0,  1.0,  1.0,
             1.0,  1.0,  1.0,
             1.0,  1.0,  1.0,
             1.0, -1.0,  1.0,
            -1.0, -1.0,  1.0,

            -1.0,  1.0, -1.0,
             1.0,  1.0, -1.0,
             1.0,  1.0,  1.0,
             1.0,  1.0,  1.0,
            -1.0,  1.0,  1.0,
            -1.0,  1.0, -1.0,

            -1.0, -1.0, -1.0,
            -1.0, -1.0,  1.0,
             1.0, -1.0, -1.0,
             1.0, -1.0, -1.0,
            -1.0, -1.0,  1.0,
             1.0, -1.0,  1.0
        ], dtype=np.float32)

        vao = glGenVertexArrays(1)
        vbo = glGenBuffers(1)

        glBindVertexArray(vao)
        glBindBuffer(GL_ARRAY_BUFFER, vbo)
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 3 * 4, None)

        return vao

    def draw(self, view, projection):
        """Render the skybox"""
        glDepthFunc(GL_LEQUAL)
        self.shader_program.use()
        
        # Remove translation from view matrix
        view = glm.mat4(glm.mat3(view))
        
        self.shader_program.set_mat4("view", view)
        self.shader_program.set_mat4("projection", projection)
        
        glBindVertexArray(self.vao)
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_CUBE_MAP, self.textures[self.current_texture])
        
        # Set the skybox uniform sampler
        glUniform1i(glGetUniformLocation(self.shader_program.program, "skybox"), 0)
        
        glDrawArrays(GL_TRIANGLES, 0, 36)
        glDepthFunc(GL_LESS)

    def change_texture(self, index):
        """Change current skybox texture"""
        if 0 <= index < len(self.textures):
            self.current_texture = index