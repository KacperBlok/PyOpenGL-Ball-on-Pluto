# text_renderer.py
from OpenGL.GL import *
import numpy as np
import freetype
import glm
from shader_program import ShaderProgram
import glfw

class TextRenderer:
    def __init__(self, font_path, font_size):
        self.characters = {}
        
        # Initialize shader with corrected vertex shader
        self.shader = ShaderProgram(
            # Vertex shader - poprawiony aby używał odpowiedniej projekcji
            """
            #version 330 core
            layout (location = 0) in vec4 vertex;
            out vec2 TexCoords;
            
            uniform mat4 projection;
            
            void main()
            {
                gl_Position = projection * vec4(vertex.xy, 0.0, 1.0);
                TexCoords = vertex.zw;
            }
            """,
            # Fragment shader - bez zmian
            """
            #version 330 core
            in vec2 TexCoords;
            out vec4 color;
            
            uniform sampler2D text;
            uniform vec3 textColor;
            
            void main()
            {
                vec4 sampled = vec4(1.0, 1.0, 1.0, texture(text, TexCoords).r);
                color = vec4(textColor, 1.0) * sampled;
            }
            """
        )
        
        # Load font with proper configuration
        face = freetype.Face(font_path)
        face.set_pixel_sizes(0, font_size)
        
        # Disable byte-alignment restriction
        glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
        
        # Configure VAO/VBO for texture quads
        self.VAO = glGenVertexArrays(1)
        self.VBO = glGenBuffers(1)
        glBindVertexArray(self.VAO)
        glBindBuffer(GL_ARRAY_BUFFER, self.VBO)
        glBufferData(GL_ARRAY_BUFFER, 24 * 4, None, GL_DYNAMIC_DRAW)  # 6 vertices * 4 components
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 4, GL_FLOAT, GL_FALSE, 0, None)
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)
        
        # Load first 128 ASCII characters
        for c in range(128):
            self._load_character(face, chr(c))

    def _load_character(self, face, char):
        # Load character glyph
        face.load_char(char, freetype.FT_LOAD_RENDER)
        
        # Generate texture
        texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture)
        glTexImage2D(
            GL_TEXTURE_2D,
            0,
            GL_RED,
            face.glyph.bitmap.width,
            face.glyph.bitmap.rows,
            0,
            GL_RED,
            GL_UNSIGNED_BYTE,
            face.glyph.bitmap.buffer
        )
        
        # Set texture options
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        
        # Store character information
        self.characters[char] = {
            'texture': texture,
            'size': (face.glyph.bitmap.width, face.glyph.bitmap.rows),
            'bearing': (face.glyph.bitmap_left, face.glyph.bitmap_top),
            'advance': face.glyph.advance.x
        }
        
        glBindTexture(GL_TEXTURE_2D, 0)

    def render_text(self, text, x, y, scale, color):
        # Enable blending for proper text rendering
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        self.shader.use()
        
        # Get window dimensions and create orthographic projection
        width, height = glfw.get_framebuffer_size(glfw.get_current_context())
        projection = glm.ortho(0.0, float(width), 0.0, float(height))
        self.shader.set_mat4("projection", projection)
        self.shader.set_vec3("textColor", color)
        
        glActiveTexture(GL_TEXTURE0)
        glBindVertexArray(self.VAO)
        
        # Iterate through characters
        for c in text:
            ch = self.characters.get(c)
            if not ch:
                continue
            
            # Calculate position and size of the character
            xpos = x + ch['bearing'][0] * scale
            # Invert y-coordinate calculation to match OpenGL coordinate system
            ypos = y - (ch['size'][1] - ch['bearing'][1]) * scale
            
            w = ch['size'][0] * scale
            h = ch['size'][1] * scale
            
            # Update VBO for each character
            vertices = np.array([
                xpos,     ypos + h,   0.0, 0.0,  # bottom left
                xpos,     ypos,       0.0, 1.0,  # top left
                xpos + w, ypos,       1.0, 1.0,  # top right
                
                xpos,     ypos + h,   0.0, 0.0,  # bottom left
                xpos + w, ypos,       1.0, 1.0,  # top right
                xpos + w, ypos + h,   1.0, 0.0   # bottom right
            ], dtype=np.float32)
            
            # Render glyph texture over quad
            glBindTexture(GL_TEXTURE_2D, ch['texture'])
            
            # Update content of VBO memory
            glBindBuffer(GL_ARRAY_BUFFER, self.VBO)
            glBufferSubData(GL_ARRAY_BUFFER, 0, vertices.nbytes, vertices)
            glBindBuffer(GL_ARRAY_BUFFER, 0)
            
            # Render quad
            glDrawArrays(GL_TRIANGLES, 0, 6)
            
            # Advance cursor for next glyph
            x += (ch['advance'] >> 6) * scale
        
        # Restore default state
        glBindVertexArray(0)
        glBindTexture(GL_TEXTURE_2D, 0)
        glDisable(GL_BLEND)