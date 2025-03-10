from OpenGL.GL import *
from PIL import Image
import numpy as np
import glm
import ctypes
from objloader import loadOBJ

class Model:
    def __init__(self, obj_path, shader_program, texture_path=None, 
                 ambient=glm.vec3(1.0), 
                 diffuse=glm.vec3(1.0), 
                 specular=glm.vec3(1.0), 
                 shininess=32.0):
        """
        Initializes the 3D model.
        
        Args:
            obj_path: Path to the .obj file
            shader_program: Shader program for rendering the model
            texture_path: Optional texture path
            ambient: Ambient light coefficient
            diffuse: Diffuse light coefficient
            specular: Specular light coefficient
            shininess: Material shininess
        """
        self.vertices, self.uvs, self.normals = loadOBJ(obj_path)
        self.shader_program = shader_program
        self.texture = None
        if texture_path:
            self.texture = self.load_texture(texture_path)
            
        # Initialize VAO and VBO
        self.vao = glGenVertexArrays(1)
        self.vbo = glGenBuffers(1)
        self.setup_mesh()
        
        # Material properties
        self.material = {
            'ambient': ambient,
            'diffuse': diffuse,
            'specular': specular,
            'shininess': shininess
        }

    def load_texture(self, file):
        """
        Loads the texture from a file and configures its parameters.
        
        Args:
            file: Path to the texture file
            
        Returns:
            OpenGL texture ID
        """
        image = Image.open(file).transpose(Image.FLIP_TOP_BOTTOM)
        img_data = np.array(image.convert("RGBA"), dtype=np.uint8)
        
        texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture)
        
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, image.width, image.height, 
                     0, GL_RGBA, GL_UNSIGNED_BYTE, img_data)
        
        # Generate mipmaps and set texture parameters
        glGenerateMipmap(GL_TEXTURE_2D)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        
        return texture

    def setup_mesh(self):
        """
        Configures OpenGL buffers for the model's mesh.
        """
        combined = []
        for i in range(len(self.vertices)):
            # Combine vertices, normals, and texture coordinates
            combined.extend(self.vertices[i])
            combined.extend(self.normals[i])
            if self.uvs:
                combined.extend(self.uvs[i])
            else:
                combined.extend([0.0, 0.0])

        vertices = (GLfloat * len(combined))(*combined)
        
        # Setup VAO and VBO
        glBindVertexArray(self.vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, len(vertices) * 4, vertices, GL_STATIC_DRAW)

        # Vertex positions
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, (3 + 3 + 2) * 4, 
                             ctypes.c_void_p(0))
        
        # Normals
        glEnableVertexAttribArray(2)
        glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, (3 + 3 + 2) * 4, 
                             ctypes.c_void_p(3 * 4))
        
        # Texture coordinates
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, (3 + 3 + 2) * 4, 
                             ctypes.c_void_p((3 + 3) * 4))
        
        glBindVertexArray(0)

    def draw(self, object_color=None, lighting_model=0):
        """
        Renders the model considering lighting and materials.
        
        Args:
            object_color: Object color (vec3)
            lighting_model: Lighting model (0 - Phong, 1 - Blinn-Phong)
        """
        if self.texture:
            glActiveTexture(GL_TEXTURE0)
            glBindTexture(GL_TEXTURE_2D, self.texture)
            glUniform1i(glGetUniformLocation(self.shader_program.program, "texture1"), 0)
        
        # Set material properties
        glUniform3f(glGetUniformLocation(self.shader_program.program, "material.ambient"), 
                    self.material['ambient'].x * object_color.x, 
                    self.material['ambient'].y * object_color.y, 
                    self.material['ambient'].z * object_color.z)
        
        glUniform3f(glGetUniformLocation(self.shader_program.program, "material.diffuse"), 
                    self.material['diffuse'].x * object_color.x, 
                    self.material['diffuse'].y * object_color.y, 
                    self.material['diffuse'].z * object_color.z)
        
        glUniform3f(glGetUniformLocation(self.shader_program.program, "material.specular"), 
                    self.material['specular'].x, 
                    self.material['specular'].y, 
                    self.material['specular'].z)
        
        glUniform1f(glGetUniformLocation(self.shader_program.program, "material.shininess"), 
                    self.material['shininess'])
        
        # Set lighting model
        glUniform1i(glGetUniformLocation(self.shader_program.program, "lightingModel"), 
                    lighting_model)
        
        # Render the model
        glBindVertexArray(self.vao)
        glDrawArrays(GL_TRIANGLES, 0, len(self.vertices))
        glBindVertexArray(0)

    def draw_shadow_map(self, shadow_program=None):
        """
        Renders the model to a shadow map.
        """
        glBindVertexArray(self.vao)
        glDrawArrays(GL_TRIANGLES, 0, len(self.vertices))
        glBindVertexArray(0)

    def cleanup(self):
        """
        Frees OpenGL resources.
        """
        if self.vao:
            glDeleteVertexArrays(1, [self.vao])
        if self.vbo:
            glDeleteBuffers(1, [self.vbo])
        if self.texture:
            glDeleteTextures(1, [self.texture])
