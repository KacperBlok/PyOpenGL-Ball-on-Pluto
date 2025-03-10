import imgui
import glfw

class ContextMenu:
    def __init__(self, skybox, lighting_vars):
        self.skybox = skybox
        self.visible = False
        self.mouse_pos = (0, 0)
        self.lighting = lighting_vars
        self.window_flags = imgui.WINDOW_NO_COLLAPSE
        # Variables for hummingbird
        self.hummingbird_effect = 0  #0 – Normal, 1 – Mirror, 2 – Transparent
        self.hummingbird_refraction_index = 1.33  # refractive index (as for water)

    def render(self):
        if not self.visible:
            return

        imgui.set_next_window_position(self.mouse_pos[0], self.mouse_pos[1], condition=1)
        imgui.begin("Scene Controls", flags=self.window_flags)

        # Skybox section
        if imgui.tree_node("Skybox Textures"):
            if imgui.button("Mountain Skybox"):
                self.skybox.change_texture(0)
            if imgui.button("World Skybox"):
                self.skybox.change_texture(1)
            if imgui.button("Space Skybox"):
                self.skybox.change_texture(2)
            imgui.tree_pop()

        # Lighting Section
        if imgui.tree_node("Lighting"):
            clicked, new_value = imgui.checkbox("Enable Lighting", self.lighting['use_lighting'])
            if clicked:
                self.lighting['use_lighting'] = new_value

            clicked, new_value = imgui.checkbox("Use Blinn-Phong (OFF = Phong)", self.lighting['current_lighting_model'] == 1)
            if clicked:
                self.lighting['current_lighting_model'] = int(new_value)

            clicked, new_value = imgui.checkbox("Animate Light", self.lighting['animate_light'])
            if clicked:
                self.lighting['animate_light'] = new_value

            if imgui.tree_node("Light Sources"):
                clicked, new_value = imgui.checkbox(
                    "Main Light Directional",
                    self.lighting['main_light'].is_directional
                )
                if clicked:
                    self.lighting['main_light'].is_directional = new_value

                clicked, new_value = imgui.checkbox(
                    "Red Light",
                    self.lighting['additional_lights'][0].is_active
                )
                if clicked:
                    self.lighting['additional_lights'][0].is_active = new_value

                clicked, new_value = imgui.checkbox(
                    "Blue Light",
                    self.lighting['additional_lights'][1].is_active
                )
                if clicked:
                    self.lighting['additional_lights'][1].is_active = new_value
                imgui.tree_pop()

            imgui.tree_pop()

        # Leaves animation section
        if imgui.tree_node("Leaves Animation"):
            clicked, new_value = imgui.checkbox("Enable Falling Leaves", self.lighting['animate_leaves'])
            if clicked:
                self.lighting['animate_leaves'] = new_value
            imgui.tree_pop()

        # Hummingbird effects section
        if imgui.tree_node("Hummingbird Effects"):
            # Radio buttons for effect selection
            if imgui.radio_button("Normal", self.hummingbird_effect == 0):
                self.hummingbird_effect = 0
            imgui.same_line()
            if imgui.radio_button("Reflective", self.hummingbird_effect == 1):
                self.hummingbird_effect = 1
            imgui.same_line()
            if imgui.radio_button("Refractive", self.hummingbird_effect == 2):
                self.hummingbird_effect = 2
            
            # Slider for refractive index (visible only when refractive effect is selected)
            if self.hummingbird_effect == 2:
                changed, new_value = imgui.slider_float(
                    "Refraction Index", 
                    self.hummingbird_refraction_index,
                    1.0, 2.5,  # Range from air (1.0) to diamond (2.42)
                    "%.2f"
                )
                if changed:
                    self.hummingbird_refraction_index = new_value
            
            imgui.tree_pop()

        # Close menu
        if imgui.button("Close"):
            self.visible = False

        imgui.end()

    def handle_mouse(self, window, button, action, mods):
        if button == glfw.MOUSE_BUTTON_RIGHT:
            if action == glfw.PRESS:
                self.visible = not self.visible
                if self.visible:
                    self.mouse_pos = glfw.get_cursor_pos(window)