# fps_counter.py
import time

class FPSCounter:
    def __init__(self, update_interval=1.0):
        self.frame_count = 0
        self.last_update_time = time.time()
        self.current_fps = 0
        self.update_interval = update_interval
        self.window_width = 120
        self.window_height = 50

    def update(self):
        self.frame_count += 1
        current_time = time.time()
        elapsed = current_time - self.last_update_time

        if elapsed >= self.update_interval:
            self.current_fps = int(self.frame_count / elapsed)
            self.frame_count = 0
            self.last_update_time = current_time

    def get_fps(self):
        return self.current_fps

    def render(self, imgui):
        # Get current display size and calculate scale factor
        display_w, display_h = imgui.get_io().display_size
        scale_factor = min(display_w / 1920, display_h / 1080)
        
        # Scale window dimensions
        scaled_width = int(self.window_width * scale_factor)
        scaled_height = int(self.window_height * scale_factor)
        
        # Position window in top-right corner with padding
        padding = 10 * scale_factor
        window_pos_x = display_w - scaled_width - padding
        window_pos_y = padding
        
        # Set window position and size
        imgui.set_next_window_position(window_pos_x, window_pos_y)
        imgui.set_next_window_size(scaled_width, scaled_height)
        
        window_flags = (
            imgui.WINDOW_NO_RESIZE | 
            imgui.WINDOW_NO_MOVE | 
            imgui.WINDOW_NO_COLLAPSE |
            imgui.WINDOW_NO_TITLE_BAR |
            imgui.WINDOW_NO_SCROLLBAR
        )
        
        imgui.begin("FPS", flags=window_flags)
        
        # Center the FPS text within the window
        text = f"FPS: {self.current_fps}"
        text_width = imgui.calc_text_size(text).x
        imgui.set_cursor_pos_x((scaled_width - text_width) * 0.5)
        imgui.text(text)
        
        imgui.end()