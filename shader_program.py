import os
import sys
from OpenGL.GL import *
import glm

class ShaderProgram:
    def __init__(self, vertex_source, fragment_source):
        """
        Initializes the shader program by compiling the provided sources.
        :param vertex_source: Vertex Shader source code
        :param fragment_source: Fragment Shader source code
        """
        self.program = glCreateProgram()

        # Compile shaders from the given sources
        vertex_shader = self.compile_shader(vertex_source, GL_VERTEX_SHADER)
        fragment_shader = self.compile_shader(fragment_source, GL_FRAGMENT_SHADER)

        glAttachShader(self.program, vertex_shader)
        glAttachShader(self.program, fragment_shader)
        glLinkProgram(self.program)

        if not glGetProgramiv(self.program, GL_LINK_STATUS):
            error = glGetProgramInfoLog(self.program).decode()
            raise RuntimeError(f"Linking program failed: {error}")

        glDetachShader(self.program, vertex_shader)
        glDetachShader(self.program, fragment_shader)
        glDeleteShader(vertex_shader)
        glDeleteShader(fragment_shader)

    def compile_shader(self, source, shader_type):
        """
        Compiles a shader from the given source.
        :param source: Shader source code
        :param shader_type: Shader type (GL_VERTEX_SHADER or GL_FRAGMENT_SHADER)
        :return: Compiled shader
        """
        shader = glCreateShader(shader_type)
        glShaderSource(shader, source)
        glCompileShader(shader)

        if not glGetShaderiv(shader, GL_COMPILE_STATUS):
            error = glGetShaderInfoLog(shader).decode()
            raise RuntimeError(f"Shader compilation failed ({shader_type}): {error}")
        return shader

    def use(self):
        """Activates the shader program."""
        glUseProgram(self.program)

    def set_mat4(self, name, matrix):
        """
        Sets a uniform matrix in the shader.
        :param name: Name of the uniform in the shader
        :param matrix: Matrix object (e.g., glm.mat4)
        """
        location = glGetUniformLocation(self.program, name)
        if location == -1:
            print(f"Warning: Uniform '{name}' not found!")
        glUniformMatrix4fv(location, 1, GL_FALSE, glm.value_ptr(matrix))

    def set_vec3(self, name, vector):
        """
        Sets a uniform vector in the shader.
        :param name: Name of the uniform in the shader
        :param vector: Vector object (e.g., glm.vec3)
        """
        location = glGetUniformLocation(self.program, name)
        if location == -1:
            print(f"Warning: Uniform '{name}' not found!")
        glUniform3fv(location, 1, glm.value_ptr(vector))

    def set_float(self, name, value):
        """
        Sets a float uniform in the shader.
        :param name: Name of the uniform in the shader
        :param value: Float value
        """
        location = glGetUniformLocation(self.program, name)
        if location == -1:
            print(f"Warning: Uniform '{name}' not found!")
        glUniform1f(location, value)

    def set_bool(self, name, value):
        """
        Sets a boolean uniform in the shader.
        :param name: Name of the uniform in the shader
        :param value: Boolean value (True/False)
        """
        location = glGetUniformLocation(self.program, name)
        if location == -1:
            print(f"Warning: Uniform '{name}' not found!")
        glUniform1i(location, int(value))

    def set_int(self, name, value):
        """
        Sets an integer uniform in the shader.
        :param name: Name of the uniform in the shader
        :param value: Integer value
        """
        location = glGetUniformLocation(self.program, name)
        if location == -1:
            print(f"Warning: Uniform '{name}' not found!")
        glUniform1i(location, value)

    def set_double(self, name, value):
        """
        Sets a double uniform in the shader.
        :param name: Name of the uniform in the shader
        :param value: Double value
        """
        location = glGetUniformLocation(self.program, name)
        if location == -1:
            print(f"Warning: Uniform '{name}' not found!")
        glUniform1d(location, value)

    def set_vec2(self, name, vector):
        """
        Sets a vec2 uniform vector in the shader.
        :param name: Name of the uniform in the shader
        :param vector: Vector object (e.g., glm.vec2)
        """
        location = glGetUniformLocation(self.program, name)
        if location == -1:
            print(f"Warning: Uniform '{name}' not found!")
        glUniform2fv(location, 1, glm.value_ptr(vector))

    def set_vec4(self, name, vector):
        """
        Sets a vec4 uniform vector in the shader.
        :param name: Name of the uniform in the shader
        :param vector: Vector object (e.g., glm.vec4)
        """
        location = glGetUniformLocation(self.program, name)
        if location == -1:
            print(f"Warning: Uniform '{name}' not found!")
        glUniform4fv(location, 1, glm.value_ptr(vector))


# Function to load shader files based on whether the app is frozen or not
def load_shader_file(file_name):
    if getattr(sys, 'frozen', False):
        # If the application is frozen (PyInstaller), use the _MEIPASS directory
        bundle_dir = sys._MEIPASS
        file_path = os.path.join(bundle_dir, "shaders", file_name)
    else:
        # If running in development mode, use the normal file path
        file_path = os.path.join(os.path.dirname(__file__), "shaders", file_name)

    with open(file_path, 'r') as file:
        return file.read()
