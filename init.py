import sys
import glm
import glfw
import math
import random
import imgui
from imgui.integrations.glfw import GlfwRenderer
from OpenGL.GL import *
import numpy as np

from model import Model
from shader_program import ShaderProgram
from camera import Camera
from lighting import Light
from skybox import CSkyBox
from context_menu import ContextMenu
from leaf_base import CMultipleLeaves
from shadows import ShadowMapping

# Constants for object identification
OBJECT_NORMAL = 0
OBJECT_HUMMINGBIRD = 1

all_terrain_positions = []

class WindowDimensions:
    def __init__(self, width, height):
        self.width = width
        self.height = height

window_dimensions = None

class GlobalVars:
    def __init__(self):
        self.current_lighting_model = 0
        self.use_lighting = True
        self.animate_light = True
        self.main_light = None
        self.additional_lights = []
        self.context_menu = None
        self.impl = None

g = GlobalVars()

def framebuffer_size_callback(window, width, height):
    """Callback function to handle window resize events"""
    global window_dimensions
    window_dimensions.width = width
    window_dimensions.height = height
    glViewport(0, 0, width, height)
    
    # Update font scaling
    io = imgui.get_io()
    scale_factor = min(width / 1920, height / 1080)
    io.font_global_scale = scale_factor
    
def get_window_dimensions():
    """Helper function to get current window dimensions"""
    return window_dimensions.width, window_dimensions.height

def key_callback(window, key, scancode, action, mods):
    if key == glfw.KEY_ESCAPE and action == glfw.PRESS:
        glfw.set_window_should_close(window, True)

def mouse_button_callback(window, button, action, mods):
    g.context_menu.handle_mouse(window, button, action, mods)

def init_window(title):
    """Initialize GLFW window with resize capability"""
    global window_dimensions
    
    if not glfw.init():
        print("Failed to initialize GLFW")
        sys.exit()

    # Get primary monitor
    primary_monitor = glfw.get_primary_monitor()
    video_mode = glfw.get_video_mode(primary_monitor)
    
    # Calculate window size (50% of screen size)
    screen_width = video_mode.size.width
    screen_height = video_mode.size.height
    window_width = int(screen_width * 0.5)
    window_height = int(screen_height * 0.5)

    # Configure GLFW window hints
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.REFRESH_RATE, 0)  # Wyłącz limit odświeżania
    glfw.window_hint(glfw.DOUBLEBUFFER, True)  # Włącz podwójne buforowanie
    glfw.window_hint(glfw.RESIZABLE, True)  # Włącz możliwość zmiany rozmiaru
    glfw.window_hint(glfw.MAXIMIZED, False)  # Okno nie będzie zmaksymalizowane na starcie

    # Create window
    window = glfw.create_window(window_width, window_height, title, None, None)
    if not window:
        print("Failed to create GLFW window")
        glfw.terminate()
        sys.exit()

    # Center window
    window_x = (screen_width - window_width) // 2
    window_y = (screen_height - window_height) // 2
    glfw.set_window_pos(window, window_x, window_y)

    glfw.make_context_current(window)
    
    # Initialize window dimensions with calculated values
    window_dimensions = WindowDimensions(window_width, window_height)
    
    # Set callbacks
    glfw.set_framebuffer_size_callback(window, framebuffer_size_callback)
    glfw.set_key_callback(window, key_callback)
    glfw.set_mouse_button_callback(window, mouse_button_callback)
    
    # Configure OpenGL
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    
    # Set initial viewport
    glViewport(0, 0, window_width, window_height)
    
    return window

    # Configure GLFW window hints
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.REFRESH_RATE, 0)  # Wyłącz limit odświeżania
    glfw.window_hint(glfw.DOUBLEBUFFER, True)  # Włącz podwójne buforowanie
    glfw.window_hint(glfw.RESIZABLE, True)  # Włącz możliwość zmiany rozmiaru
    glfw.window_hint(glfw.MAXIMIZED, False)  # Okno nie będzie zmaksymalizowane na starcie

    # Create window and center it
    window = glfw.create_window(window_width, window_height, title, None, None)
    
    # Center window
    window_x = (screen_width - window_width) // 2
    window_y = (screen_height - window_height) // 2
    glfw.set_window_pos(window, window_x, window_y)
    if not window:
        print("Failed to create GLFW window")
        glfw.terminate()
        sys.exit()

    glfw.make_context_current(window)
    
    # Initialize window dimensions
    window_dimensions = WindowDimensions(width, height)
    
    # Set callbacks
    glfw.set_framebuffer_size_callback(window, framebuffer_size_callback)
    glfw.set_key_callback(window, key_callback)
    glfw.set_mouse_button_callback(window, mouse_button_callback)
    
    # Configure OpenGL
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    
    # Set initial viewport
    glViewport(0, 0, width, height)
    
    return window

def generate_random_terrain_positions(num_positions, min_dist=-50, max_dist=50, min_spacing=3.0, height_offset=0.0, exclude_zone=None, object_type=""):
    global all_terrain_positions
    positions = []
    max_attempts = num_positions * 20
    
    # Dostosowujemy minimalne odstępy dla różnych typów obiektów
    type_spacing = {
        "rock": 8.0,
        "cactus1": 6.0,
        "bark": 6.0,
        "grass": 2.0
    }
    
    print("====================================")
    print(f"Generowanie pozycji dla typu: '{object_type}'")
    print(f"Wymagany odstep bazowy: {min_spacing}")
    print(f"Liczba obiektow do wygenerowania: {num_positions}")
    print("====================================")
    
    attempts = 0
    while len(positions) < num_positions and attempts < max_attempts:
        attempts += 1
        x = random.uniform(min_dist, max_dist)
        z = random.uniform(min_dist, max_dist)
        pos = glm.vec3(x, height_offset, z)
        
        if exclude_zone:
            x_min, x_max, z_min, z_max = exclude_zone
            if x_min <= x <= x_max and z_min <= z <= z_max:
                continue
        
        too_close = False
        collision_info = ""
        
        # Sprawdź odległość od obiektów tego samego typu
        for existing_pos in positions:
            distance = glm.length(glm.vec2(pos.x - existing_pos.x, pos.z - existing_pos.z))
            if distance < min_spacing:
                too_close = True
                collision_info = f"Kolizja z tym samym typem ('{object_type}'), odległość: {distance:.2f}"
                break
        
        # Sprawdź odległość od obiektów innych typów
        if not too_close:
            for existing_pos, existing_type in all_terrain_positions:
                required_spacing = max(
                    type_spacing.get(object_type, min_spacing),
                    type_spacing.get(existing_type, min_spacing)
                )
                
                distance = glm.length(glm.vec2(pos.x - existing_pos.x, pos.z - existing_pos.z))
                if distance < required_spacing:
                    too_close = True
                    collision_info = f"Kolizja między '{object_type}' a '{existing_type}', odległość: {distance:.2f}, wymagana: {required_spacing}"
                    break
        
        if not too_close:
            positions.append(pos)
            all_terrain_positions.append((pos, object_type))
            if len(positions) % 10 == 0:
                print(f"Wygenerowano {len(positions)}/{num_positions} pozycji dla '{object_type}'")
        elif attempts % 100 == 0:
            print(f"Nieudana próba ({attempts}): {collision_info}")
    
    print("====================================")
    print(f"Zakonczono generowanie '{object_type}'")
    print(f"Wygenerowano {len(positions)}/{num_positions} pozycji po {attempts} probach")
    print("====================================\n")
    
    return positions

def get_terrain_height(vertices, pos, debug=False):
    try:
        min_height = float('-inf')
        max_dist = 1000.0

        if abs(pos.x) > max_dist or abs(pos.z) > max_dist:
            return -0.8

        # Konwertuj vertices na numpy array dla lepszej wydajności
        vertices_array = np.array(vertices).reshape(-1, 3)
        
        for i in range(0, len(vertices_array), 3):
            if i + 2 >= len(vertices_array):
                break

            v1 = glm.vec3(*vertices_array[i])
            v2 = glm.vec3(*vertices_array[i + 1])
            v3 = glm.vec3(*vertices_array[i + 2])

            if point_in_triangle(pos.x, pos.z, v1.x, v1.z, v2.x, v2.z, v3.x, v3.z):
                height = interpolate_height(pos.x, pos.z, v1, v2, v3)
                if debug:
                    print(f"Triangle vertices: {v1}, {v2}, {v3}")
                    print(f"Calculated height: {height}")
                min_height = max(min_height, height)

        final_height = -0.8 if min_height == float('-inf') else min_height
        if debug:
            print(f"Final height for position {pos}: {final_height}")
        return final_height

    except Exception as e:
        print(f"Error in get_terrain_height: {e}")
        return -0.8

def point_in_triangle(px, pz, x1, z1, x2, z2, x3, z3):
    def sign(p1x, p1z, p2x, p2z, p3x, p3z):
        return (p1x - p3x) * (p2z - p3z) - (p2x - p3x) * (p1z - p3z)
    
    d1 = sign(px, pz, x1, z1, x2, z2)
    d2 = sign(px, pz, x2, z2, x3, z3)
    d3 = sign(px, pz, x3, z3, x1, z1)

    has_neg = (d1 < 0) or (d2 < 0) or (d3 < 0)
    has_pos = (d1 > 0) or (d2 > 0) or (d3 > 0)

    return not (has_neg and has_pos)

def interpolate_height(x, z, v1, v2, v3):
    try:
        edge1 = v2 - v1
        edge2 = v3 - v1
        normal = glm.normalize(glm.cross(edge1, edge2))
        
        if abs(normal.y) < 0.001:
            return v1.y
            
        d = -(normal.x * v1.x + normal.y * v1.y + normal.z * v1.z)
        return (-normal.x * x - normal.z * z - d) / normal.y
    except Exception as e:
        print(f"Error in interpolate_height: {e}")
        return -0.8

def init_lights():
    print("Initializing lights...")
    g.main_light = Light(
        position=glm.vec3(4.0, 3.0, 0.0),
        color=glm.vec3(2.0, 2.0, 1.8),
        direction=glm.vec3(-0.2, -1.0, -0.3),
        ambient_strength=0.2
    )
    g.main_light.is_directional = False
    g.main_light.is_active = True

    g.additional_lights = [
        Light(position=glm.vec3(-8.0, 5.0, -8.0),
             color=glm.vec3(1.5, 0.5, 0.5),
             ambient_strength=0.3),
        Light(position=glm.vec3(8.0, 5.0, -8.0),
             color=glm.vec3(0.5, 0.5, 1.5),
             ambient_strength=0.3)
    ]

def init_shaders():
    try:
        with open("shaders/vertex_shader.glsl", "r") as f:
            vertex_src = f.read()
        with open("shaders/fragment_shader.glsl", "r") as f:
            fragment_src = f.read()
        with open("shaders/skybox_vertex_shader.glsl", "r") as f:
            skybox_vertex_src = f.read()
        with open("shaders/skybox_fragment_shader.glsl", "r") as f:
            skybox_fragment_src = f.read()
        with open("shaders/leaf_vertex_shader.glsl", "r") as f:
            leaf_vertex_src = f.read()
        with open("shaders/leaf_fragment_shader.glsl", "r") as f:
            leaf_fragment_src = f.read()
            
        program = ShaderProgram(vertex_src, fragment_src)
        skybox_program = ShaderProgram(skybox_vertex_src, skybox_fragment_src)
        leaf_program = ShaderProgram(leaf_vertex_src, leaf_fragment_src)
        return program, skybox_program, leaf_program
    except Exception as e:
        print(f"Shader initialization error: {e}")
        glfw.terminate()
        sys.exit(1)