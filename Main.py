from OpenGL.GLUT import *
from init import *
from player import Player
from camera import Camera
from fps_counter import FPSCounter
from position_counter import PositionCounter
from score_counter import ScoreCounter
from shader_program import load_shader_file, ShaderProgram

from init import all_terrain_positions

# Constants for object types
OBJECT_TYPES = {
    "ground": {"scale": 1.0, "collision": False},
    "rock": {"scale": 1.2, "collision": True},
    "monkey": {"scale": 1.0, "collision": True},
    "grass": {"scale": 0.5, "collision": False},
    "sphere": {"scale": 1.0, "collision": True},
    "cube": {"scale": 1.0, "collision": True},
    "light_sphere": {"scale": 0.2, "collision": False},
    "hummingbird": {"scale": 1.0, "collision": True},
    "lego": {"scale": 0.5, "collision": False},
    "bark": {"scale": 0.8, "collision": True},
    "ball": {"scale": 0.3, "collision": False},
    "cactus1": {"scale": 0.8, "collision": True}
}

OBJECT_HEIGHT_OFFSETS = {
        "grass": -0.8,    
        "bark": -0.8,     
        "cactus1": -0.8,  
        "rock": -0.8,      
        "ball": -0.1
    }

def main():
    # Initialize window and OpenGL context
    window = init_window("Balls on Pluto")
    glutInit()
    imgui.create_context()
    g.impl = GlfwRenderer(window)
    fps_counter = FPSCounter()
    position_counter = PositionCounter()
    score_counter = ScoreCounter()

    vertex_shader_source = load_shader_file("shadow_vertex_shader.glsl")
    fragment_shader_source = load_shader_file("shadow_fragment_shader.glsl")
    # Initialize shadow mapping
    shadow_mapping = ShadowMapping()
    shadow_program = ShaderProgram(vertex_shader_source, fragment_shader_source)

    # Initialize shaders and skybox
    program, skybox_program, leaf_program = init_shaders()
    skybox = CSkyBox(skybox_program)
    init_lights()
    
    # Initialize lighting variables
    lighting_vars = {
        'current_lighting_model': g.current_lighting_model,
        'use_lighting': g.use_lighting,
        'animate_light': g.animate_light,
        'animate_leaves': True, 
        'main_light': g.main_light,
        'additional_lights': g.additional_lights
    }
    g.context_menu = ContextMenu(skybox, lighting_vars)

    # Initialize leaf vertices and indices
    leaf_vertices = np.array([
        -0.5, 0.0, -0.5,   0.0, 0.0,     1.0, 1.0, 1.0, 1.0,
        0.5, 0.0, -0.5,    1.0, 0.0,     1.0, 1.0, 1.0, 1.0,
        0.5, 0.0,  0.5,    1.0, 1.0,     1.0, 1.0, 1.0, 1.0,
        -0.5, 0.0,  0.5,   0.0, 1.0,     1.0, 1.0, 1.0, 1.0
    ], dtype=np.float32)
    
    leaf_indices = np.array([0, 1, 2, 2, 3, 0], dtype=np.uint32)
    leaf_texture = Model.load_texture(None, "textures/treeLeaf.png")
    leaves = CMultipleLeaves(leaf_vertices, leaf_indices, 5000, leaf_texture)

    # Initialize camera
    camera = Camera(
        position=glm.vec3(0.0, 3.0, 10.0),
        front=glm.vec3(0.0, 0.0, -1.0),
        up=glm.vec3(0.0, 1.0, 0.0),
        angle=0.0
    )

    # Initialize models with their properties
    models = {
        "ground": Model("models/ground-large.obj", program, "textures/texture3.jpg", 
                       ambient=glm.vec3(0.7), diffuse=glm.vec3(1.0), specular=glm.vec3(0.3), shininess=16.0),
        "rock": Model("models/rock.obj", program, "textures/rock_texture.jpg", 
                     ambient=glm.vec3(0.5), diffuse=glm.vec3(0.7), specular=glm.vec3(0.1), shininess=8.0),
        "monkey": Model("models/monkey.obj", program, "textures/texture2.jpg", 
                       ambient=glm.vec3(0.8), diffuse=glm.vec3(1.2), specular=glm.vec3(0.7), shininess=64.0),
        "grass": Model("models/grass.obj", program, "textures/grass_texture.jpg", 
                      ambient=glm.vec3(0.4), diffuse=glm.vec3(0.8), specular=glm.vec3(0.2), shininess=8.0),
        "sphere": Model("models/sphere.obj", program, "textures/sphere.png", 
                       ambient=glm.vec3(1.0), diffuse=glm.vec3(1.5), specular=glm.vec3(1.5), shininess=128.0),
        "cube": Model("models/cube.obj", program, "textures/sphere.png", 
                     ambient=glm.vec3(0.8), diffuse=glm.vec3(1.2), specular=glm.vec3(2.0), shininess=512.0),
        "light_sphere": Model("models/sphere.obj", program, "textures/light.png",
                            ambient=glm.vec3(1.0), diffuse=glm.vec3(1.5), specular=glm.vec3(1.5), shininess=32.0),
        "hummingbird": Model("models/koliber.obj", program, "textures/koliber.jpg",
                           ambient=glm.vec3(0.8), diffuse=glm.vec3(1.0), specular=glm.vec3(0.5), shininess=32.0),
        "lego": Model("models/lego.obj", program, "textures/lego.png",
                     ambient=glm.vec3(0.8), diffuse=glm.vec3(1.0), specular=glm.vec3(0.5), shininess=32.0),
        "bark": Model("models/bark.obj", program, "textures/bark.png",
                       ambient=glm.vec3(0.5), diffuse=glm.vec3(0.8), specular=glm.vec3(0.0), shininess=0.0),
        "cactus1": Model("models/cactus1.obj", program, "textures/cactus.jpg",
                        ambient=glm.vec3(0.5), diffuse=glm.vec3(0.8), specular=glm.vec3(0.2), shininess=16.0),
        "ball": Model("models/sphere.obj", program, "textures/koliber.jpg",
                        ambient=glm.vec3(0.5), diffuse=glm.vec3(0.8), specular=glm.vec3(0.2), shininess=16.0)
    }

    # Set model names for collision detection
    for name, model in models.items():
        model.name = name

    # Initialize transformations
    transformations = {
        "ground": glm.translate(glm.mat4(1.0), glm.vec3(0.0, -0.8, 0.0)),
        "rock": glm.translate(glm.mat4(1.0), glm.vec3(-5.0, -0.7, -2.0)),
        "monkey": glm.translate(glm.mat4(1.0), glm.vec3(0.0, 1.0, 0.0)),
        "sphere": glm.translate(glm.mat4(1.0), glm.vec3(3.0, 1.0, 0.0)),
        "grass": glm.translate(glm.mat4(1.0), glm.vec3(0.0, 3.0, 0.0)),
        "cube": glm.translate(glm.mat4(1.0), glm.vec3(0.0, -1.0, -5.0)),
        #"ball": glm.translate(glm.mat4(1.0), glm.vec3(0.0, 1.0, 0.0)), 
        "hummingbird": glm.translate(glm.mat4(1.0), glm.vec3(2.0, 2.0, -3.0)),
        #"bark": glm.translate(glm.mat4(1.0), glm.vec3(5.0, -0.8, 0.0))
        #"cactus1": glm.translate(glm.mat4(1.0), glm.vec3(0.0, -0.8, 0.0))
    }

    # Initialize player and collision objects
    player = Player(models["lego"], models["ground"])
    
    # Add collision objects
    for name, model in models.items():
        if OBJECT_TYPES.get(name, {}).get("collision", False):
            scale = OBJECT_TYPES[name]["scale"]
            height_offset = OBJECT_HEIGHT_OFFSETS.get(name, 0.0)  # Pobierz offset wysokości
            player.add_collision_object(model, transformations.get(name, glm.mat4(1.0)), scale, height_offset)

    monkey_path_zone = (-2.0, 2.0, -20.0, 20.0)  # Define the path zone for the monkey

    all_terrain_positions.clear() #Czyszczenie listy przed generowaniem nowych pozycji

    # Generate terrain positions with appropriate height offsets
    bark_positions = generate_random_terrain_positions(10, -50, 50, 5.0, OBJECT_HEIGHT_OFFSETS["bark"], exclude_zone=monkey_path_zone, object_type="bark")
    additional_rock_positions = generate_random_terrain_positions(3, -50, 50, 8.0, OBJECT_HEIGHT_OFFSETS["rock"], exclude_zone=monkey_path_zone, object_type="rock")
    cactus1_positions = generate_random_terrain_positions(100, -50, 50, 5.0, OBJECT_HEIGHT_OFFSETS["cactus1"], exclude_zone=monkey_path_zone, object_type="cactus1")
    ball_positions = generate_random_terrain_positions(20, -50, 50, 5.0, OBJECT_HEIGHT_OFFSETS["ball"], exclude_zone=monkey_path_zone, object_type="ball")
    grass_positions = generate_random_terrain_positions(100, -50, 100, 2.0, OBJECT_HEIGHT_OFFSETS["grass"], object_type="grass")
    
    
    

    # Set terrain heights with debug info for first few positions
    print("Calculating terrain heights...")
    for i, pos in enumerate(grass_positions):
        debug = i < 3  # Debug tylko dla pierwszych 3 pozycji
        height = get_terrain_height(models["ground"].vertices, pos, debug)
        pos.y = height + OBJECT_HEIGHT_OFFSETS["grass"]

    for pos in bark_positions:
        height = get_terrain_height(models["ground"].vertices, pos)
        pos.y = height + OBJECT_HEIGHT_OFFSETS["bark"]

    for pos in cactus1_positions:
        height = get_terrain_height(models["ground"].vertices, pos)
        pos.y = height + OBJECT_HEIGHT_OFFSETS["cactus1"]

    for pos in additional_rock_positions:
        height = get_terrain_height(models["ground"].vertices, pos)
        pos.y = height + OBJECT_HEIGHT_OFFSETS["rock"]

    for pos in ball_positions:
        height = get_terrain_height(models["ground"].vertices, pos)
        pos.y = height + OBJECT_HEIGHT_OFFSETS["ball"]

    # Create terrain transformations
    terrain_objects = {
        "bark": [glm.translate(glm.mat4(1.0), pos) for pos in bark_positions],
        "cactus1": [glm.translate(glm.mat4(1.0), pos) for pos in cactus1_positions],
        "additional_rocks": [glm.translate(glm.mat4(1.0), pos) for pos in additional_rock_positions],
        "ball": [glm.translate(glm.mat4(1.0), pos) for pos in ball_positions]
        
    }

    # Add terrain objects to collision system
    for object_type, transforms in terrain_objects.items():
        for transform in transforms:
            if object_type in ["bark", "cactus1"]:
                height_offset = OBJECT_HEIGHT_OFFSETS.get(object_type, 0.0)  # Pobierz offset wysokości
                player.add_collision_object(
                    models[object_type], 
                    transform,
                    OBJECT_TYPES[object_type]["scale"],
                    height_offset
                )
            elif object_type == "additional_rocks":
                height_offset = OBJECT_HEIGHT_OFFSETS.get("rock", 0.0)  # Pobierz offset wysokości dla kamieni
                player.add_collision_object(
                    models["rock"], 
                    transform,
                    OBJECT_TYPES["rock"]["scale"],
                    height_offset
                )

    # Initialize colors
    colors = {
        "ground": glm.vec3(0.5, 0.35, 0.05),
        "rock": glm.vec3(0.0, 0.5, 0.0),
        "monkey": glm.vec3(1.0, 0.8, 0.3),
        "grass": glm.vec3(0.0, 0.7, 0.0),
        "sphere": glm.vec3(1.0, 0.5, 0.0),
        "hummingbird": glm.vec3(1.0, 1.0, 1.0),
        "lego": glm.vec3(1.0, 1.0, 1.0),
        "bark": glm.vec3(0.2, 0.8, 0.2),
        "ball": glm.vec3(1.0, 0.5, 0.0),
        "cactus1": glm.vec3(0.2, 0.8, 0.2)
    }

    # Initialize key states
    keys = {
        'w': False, 's': False, 'a': False, 'd': False,
        'c': False, 'c_pressed': False,
        'minus': False, 'equal': False,
        '0': False, '9': False,
    }

    # Initialize animation variables
    last_frame_time = glfw.get_time()
    monkey_angle = 0.0
    monkey_z = 0.0
    monkey_direction = 1.0
    movement_speed = 4.0
    rotation_speed = 50.0
    distance_limit = 20.0
    light_angle = 0.0
    light_radius = 8.0
    light_speed = 5.0
    light_height = 3.0
    hummingbird_rotation_speed = 90.0
    hummingbird_angle = 0.0
    
    

    # Main game loop
    while not glfw.window_should_close(window):
        current_frame_time = glfw.get_time()
        delta_time = current_frame_time - last_frame_time
        last_frame_time = current_frame_time

        glfw.poll_events()
        g.impl.process_inputs()

        # Get current framebuffer size and update viewport
        fb_width, fb_height = glfw.get_framebuffer_size(window)
        glViewport(0, 0, fb_width, fb_height)

        # Update key states
        keys['w'] = glfw.get_key(window, glfw.KEY_W) == glfw.PRESS
        keys['s'] = glfw.get_key(window, glfw.KEY_S) == glfw.PRESS
        keys['a'] = glfw.get_key(window, glfw.KEY_A) == glfw.PRESS
        keys['d'] = glfw.get_key(window, glfw.KEY_D) == glfw.PRESS
        keys['minus'] = glfw.get_key(window, glfw.KEY_MINUS) == glfw.PRESS
        keys['equal'] = glfw.get_key(window, glfw.KEY_EQUAL) == glfw.PRESS
        keys['0'] = glfw.get_key(window, glfw.KEY_0) == glfw.PRESS
        keys['9'] = glfw.get_key(window, glfw.KEY_9) == glfw.PRESS

        # Check for ball collection
        collected_balls = player.check_ball_collection(terrain_objects["ball"])
        if collected_balls:
            # Remove collected balls in reverse order to maintain correct indices
            for index in sorted(collected_balls, reverse=True):
                terrain_objects["ball"].pop(index)
                score_counter.increment()

        # Handle camera mode toggle
        c_key_current = glfw.get_key(window, glfw.KEY_C) == glfw.PRESS
        if c_key_current and not keys['c_pressed']:
            camera.toggle_camera_mode()
        keys['c_pressed'] = c_key_current

        # Update player and camera
        if camera.camera_mode == "third_person":
            player.update(delta_time, keys)
            camera.follow_player(player.position, player.direction)
        else:
            camera.update(delta_time, keys)

        # Update monkey animation
        monkey_z += monkey_direction * movement_speed * delta_time
        if abs(monkey_z) >= distance_limit:
            monkey_direction *= -1

        monkey_angle += rotation_speed * delta_time
        if monkey_angle >= 360.0:
            monkey_angle -= 360.0

        transformations["monkey"] = glm.translate(glm.mat4(1.0), glm.vec3(0.0, 1.0, monkey_z))
        transformations["monkey"] = glm.rotate(transformations["monkey"], glm.radians(monkey_angle), glm.vec3(0.0, 1.0, 0.0))

        # Update hummingbird animation
        hummingbird_angle += hummingbird_rotation_speed * delta_time
        if hummingbird_angle >= 360.0:
            hummingbird_angle -= 360.0

        model_matrix = glm.mat4(1.0)
        model_matrix = glm.translate(model_matrix, glm.vec3(2.0, 2.0, -3.0))
        model_matrix = glm.rotate(model_matrix, glm.radians(hummingbird_angle), glm.vec3(0.0, 1.0, 0.0))
        transformations["hummingbird"] = model_matrix

        # Update projection matrix based on current framebuffer size
        aspect_ratio = fb_width / fb_height if fb_height != 0 else 1.0
        projection = glm.perspective(glm.radians(45.0), aspect_ratio, 0.1, 100.0)

        # Render shadows
        shadow_mapping.start_shadow_pass()
        shadow_program.use()
        shadow_program.set_mat4("lightSpaceMatrix", shadow_mapping.light_space_matrix)
        
        
        # Draw shadow maps for main objects
        for name, model in models.items():
            if name != "grass" and name != "light_sphere":
                shadow_program.set_mat4("model", transformations.get(name, player.get_model_matrix()))
                model.draw_shadow_map(shadow_program)
        
        # Draw shadow maps for terrain objects
        for object_type, transforms in terrain_objects.items():
            for transform in transforms:
                shadow_program.set_mat4("model", transform)
                if object_type in ["bark", "cactus1"]:
                    models[object_type].draw_shadow_map(shadow_program)
                elif object_type == "additional_rocks":
                    models["rock"].draw_shadow_map(shadow_program)

        shadow_mapping.end_shadow_pass(fb_width, fb_height)

        # Main rendering pass
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Update animated light position
        if lighting_vars['animate_light'] and not g.main_light.is_directional:
            light_angle += light_speed * delta_time
            if light_angle >= 360.0:
                light_angle -= 360.0
            
            light_x = math.cos(glm.radians(light_angle)) * light_radius
            light_z = math.sin(glm.radians(light_angle)) * light_radius
            g.main_light.position = glm.vec3(light_x, light_height, light_z)

        # Set up view matrix
        view = camera.get_view_matrix()

        # Draw skybox with updated matrices
        skybox_program.use()
        skybox_program.set_mat4("view", view)
        skybox_program.set_mat4("projection", projection)
        skybox.draw(view, projection)

        # Configure main shader program
        program.use()
        program.set_bool("use_lighting", lighting_vars['use_lighting'])
        program.set_int("hummingbird_effect", g.context_menu.hummingbird_effect)
        program.set_float("refraction_index", g.context_menu.hummingbird_refraction_index)
        program.set_vec3("viewPos", camera.position)
        program.set_mat4("view", view)
        program.set_mat4("projection", projection)

        # Set up shadow mapping
        shadow_mapping.bind_shadow_map(program)
        program.set_mat4("lightSpaceMatrix", shadow_mapping.light_space_matrix)

        # Configure lighting
        active_count = 1
        for light in g.additional_lights:
            if light.is_active:
                active_count += 1
        program.set_int("active_lights", active_count)

        # Set up main light
        g.main_light.set_uniforms(program, 0)
        if not g.main_light.is_directional:
            light_transform = glm.translate(glm.mat4(1.0), g.main_light.position)
            light_transform = glm.scale(light_transform, glm.vec3(0.2))
            program.set_mat4("model", light_transform)
            program.set_int("current_object", OBJECT_NORMAL)
            models["light_sphere"].draw(g.main_light.color, lighting_vars['current_lighting_model'])

        # Set up additional lights
        current_index = 1
        for light in g.additional_lights:
            if light.is_active:
                light.set_uniforms(program, current_index)
                light_transform = glm.translate(glm.mat4(1.0), light.position)
                light_transform = glm.scale(light_transform, glm.vec3(0.2))
                program.set_mat4("model", light_transform)
                program.set_int("current_object", OBJECT_NORMAL)
                models["light_sphere"].draw(light.color, lighting_vars['current_lighting_model'])
                current_index += 1

        # Draw main objects
        for name, model in models.items():
            if name != "grass" and name != "light_sphere" and name != "lego":
                if name == "hummingbird":
                    program.set_int("current_object", OBJECT_HUMMINGBIRD)
                    program.set_mat4("model", transformations["hummingbird"])
                elif name == "cactus1" or name == "bark" or name == "ball":
                    continue
                else:
                    program.set_int("current_object", OBJECT_NORMAL)
                    program.set_mat4("model", transformations[name])
                
                model.draw(colors.get(name, glm.vec3(1.0)), lighting_vars['current_lighting_model'])

        # Draw player (Lego)
        program.set_int("current_object", OBJECT_NORMAL)
        program.set_mat4("model", player.get_model_matrix())
        models["lego"].draw(colors["lego"], lighting_vars['current_lighting_model'])

        # Draw terrain objects
        program.set_int("current_object", OBJECT_NORMAL)
        for object_type, transforms in terrain_objects.items():
            for transform in transforms:
                program.set_mat4("model", transform)
                if object_type in ["bark", "cactus1"]:
                    models[object_type].draw(colors[object_type], lighting_vars['current_lighting_model'])
                elif object_type == "additional_rocks":
                    models["rock"].draw(colors["rock"], lighting_vars['current_lighting_model'])
                elif object_type == "ball":
                    models["ball"].draw(colors["ball"], lighting_vars['current_lighting_model'])

        # Draw grass
        for pos in grass_positions:
            program.set_mat4("model", glm.translate(glm.mat4(1.0), pos))
            models["grass"].draw(colors["grass"], lighting_vars['current_lighting_model'])

        # Draw leaves with updated matrices
        leaf_program.use()
        leaf_program.set_mat4("view", view)
        leaf_program.set_mat4("projection", projection)
        leaves.update_positions(delta_time, lighting_vars['animate_leaves'])
        leaves.draw()

        position_counter.update((player.position.x, player.position.y, player.position.z))

        fps_counter.update()
        score_counter.render()
        # UI rendering with updated positions
        imgui.new_frame()
        
        # Update UI positions based on current window size
        fps_pos = (fb_width - 120, 10)
        pos_counter_pos = (10, 10)
        score_pos = (fb_width // 2 - 100, 10)
        
        imgui.set_next_window_position(fps_pos[0], fps_pos[1])
        fps_counter.render(imgui)
        
        imgui.set_next_window_position(pos_counter_pos[0], pos_counter_pos[1])
        position_counter.render(imgui)
        
        #imgui.set_next_window_position(score_pos[0], score_pos[1])
        #score_counter.render(imgui)
        
        g.context_menu.render()
        
        imgui.render()
        g.impl.render(imgui.get_draw_data())

        # Swap buffers
        glfw.swap_buffers(window)

    # Cleanup
    g.impl.shutdown()
    glfw.terminate()

if __name__ == "__main__":
    main()