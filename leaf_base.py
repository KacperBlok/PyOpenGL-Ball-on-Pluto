import numpy as np
from OpenGL.GL import *
import random
import ctypes

class CLeaf:
    def __init__(self, vertices, indices, texture=None):
        self.vertices = vertices
        self.indices = indices
        self.texture = texture
        self.setup_mesh()

    def setup_mesh(self):
        self.vao = glGenVertexArrays(1)
        self.vbo = glGenBuffers(1)
        self.ebo = glGenBuffers(1)

        glBindVertexArray(self.vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)

        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ebo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.indices.nbytes, self.indices, GL_STATIC_DRAW)

        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 9 * 4, None)
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 9 * 4, ctypes.c_void_p(3 * 4))
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(2, 4, GL_FLOAT, GL_FALSE, 9 * 4, ctypes.c_void_p(5 * 4))
        glEnableVertexAttribArray(2)

    def draw(self):
        if self.texture:
            glBindTexture(GL_TEXTURE_2D, self.texture)
        glBindVertexArray(self.vao)
        glDrawElements(GL_TRIANGLES, len(self.indices), GL_UNSIGNED_INT, None)

        #Zdefiniowanie bazowej geometrii liścia
        #Wygenerowanie danych dla wielu instancji
        #Skonfigurowanie atrybutów instancji (pozycja, skala, rotacja, prędkość)
        #Użycie glDrawElementsInstanced do narysowania wielu kopii tej samej geometrii z różnymi atrybutami
        #class to render intance
class CMultipleLeaves(CLeaf):
    def __init__(self, vertices, indices, instance_count, texture=None):
        super().__init__(vertices, indices, texture)
        self.instance_count = instance_count
        self.instance_data = self.generate_instance_data()
        self.setup_instance_attributes()

    def generate_instance_data(self):
        instance_data = []
        for _ in range(self.instance_count):
            x = random.uniform(-50, 50)
            y = random.uniform(10, 50)
            z = random.uniform(-50, 50)
            scale = random.uniform(0.2, 0.5)
            rotation = random.uniform(0, 360)
            vel_x = random.uniform(-1, 1)
            vel_y = random.uniform(-2, -1)
            vel_z = random.uniform(-1, 1)
            instance_data.extend([x, y, z, scale, rotation, vel_x, vel_y, vel_z])
        return np.array(instance_data, dtype=np.float32)
#Configure instance attributes
    def setup_instance_attributes(self):
        self.instance_vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.instance_vbo)
        glBufferData(GL_ARRAY_BUFFER, self.instance_data.nbytes, self.instance_data, GL_DYNAMIC_DRAW)

         # Pozytion atributee
        glVertexAttribPointer(3, 3, GL_FLOAT, GL_FALSE, 8 * 4, None)
        glEnableVertexAttribArray(3)
        glVertexAttribDivisor(3, 1)
        #  scale
        glVertexAttribPointer(4, 1, GL_FLOAT, GL_FALSE, 8 * 4, ctypes.c_void_p(3 * 4))
        glEnableVertexAttribArray(4)
        glVertexAttribDivisor(4, 1)
        # Rotation 
        glVertexAttribPointer(5, 1, GL_FLOAT, GL_FALSE, 8 * 4, ctypes.c_void_p(4 * 4))
        glEnableVertexAttribArray(5)
        glVertexAttribDivisor(5, 1)
        # speed 
        glVertexAttribPointer(6, 3, GL_FLOAT, GL_FALSE, 8 * 4, ctypes.c_void_p(5 * 4))
        glEnableVertexAttribArray(6)
        glVertexAttribDivisor(6, 1)

    def update_positions(self, delta_time, animate):
        if not animate:
            return
        for i in range(self.instance_count):
            idx = i * 8
            ## Position update according to speed
            self.instance_data[idx:idx+3] += self.instance_data[idx+5:idx+8] * delta_time
            ## Leaf rotation
            self.instance_data[idx+4] += delta_time * 50

            ## Reset position when the leaf falls too low
            if self.instance_data[idx+1] < -10: # Y pozytion
                self.instance_data[idx+1] = 50
                self.instance_data[idx] = random.uniform(-50, 50)
                self.instance_data[idx+2] = random.uniform(-50, 50)

        glBindBuffer(GL_ARRAY_BUFFER, self.instance_vbo)
        glBufferSubData(GL_ARRAY_BUFFER, 0, self.instance_data.nbytes, self.instance_data)


    def draw(self):
        if self.texture:
            glBindTexture(GL_TEXTURE_2D, self.texture)
        glBindVertexArray(self.vao)
        glDrawElementsInstanced(GL_TRIANGLES, len(self.indices), GL_UNSIGNED_INT, None, self.instance_count)