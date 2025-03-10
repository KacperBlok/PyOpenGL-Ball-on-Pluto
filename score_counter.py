import os
import sys
import glfw
import glm
from text_render import TextRenderer

class ScoreCounter:
    def __init__(self):
        self.collected_balls = 0

        # Check if the application is frozen (packed by PyInstaller)
        if getattr(sys, 'frozen', False):
            # If the application is packed, set the path to the folder where PyInstaller stores the files
            bundle_dir = sys._MEIPASS
            font_path = os.path.join(bundle_dir, "fonts", "arial.ttf")
        else:
            # If the application is running in development mode, use the relative path to the font
            font_path = os.path.join(os.path.dirname(__file__), "fonts", "arial.ttf")
        
        # Load the font with the dynamically set path
        self.text_renderer = TextRenderer(font_path, 84)

    def increment(self):
        self.collected_balls += 1

    def render(self):
        # Get the window dimensions
        width, height = glfw.get_framebuffer_size(glfw.get_current_context())
        text = f"Collected Balls: {self.collected_balls}"
        
        # Calculate the scaling factor based on the window size
        base_width = 1920.0  # base resolution
        base_height = 1080.0
        scale_factor = min(width / base_width, height / base_height)
        text_scale = 0.5 * scale_factor  # base scale multiplied by window scale factor
        
        # Calculate the position (centered horizontally, near the top of the screen)
        text_width = sum((self.text_renderer.characters.get(c, {}).get('advance', 0) >> 6) for c in text) * text_scale
        x = (width - text_width) / 2
        y = height - (50 * scale_factor)  # also scale the top margin
        
        # Render the text in white color with the appropriate scale
        self.text_renderer.render_text(text, x, y, text_scale, glm.vec3(1.0, 1.0, 1.0))
