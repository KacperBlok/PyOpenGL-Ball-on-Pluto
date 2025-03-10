# position_counter.py
class PositionCounter:
    def __init__(self):
        self.position = (0.0, 0.0, 0.0)

    def update(self, position):
        self.position = position

    def render(self, imgui):
        # Create a small window in the top-left corner
        window_flags = (
            imgui.WINDOW_NO_RESIZE | 
            imgui.WINDOW_NO_MOVE | 
            imgui.WINDOW_NO_COLLAPSE |
            imgui.WINDOW_ALWAYS_AUTO_RESIZE
        )
        
        # Set window position to top-left corner
        imgui.set_next_window_position(10, 10, imgui.ONCE)
        
        imgui.begin("Position", flags=window_flags)
        imgui.text(f"X: {self.position[0]:.2f}")
        imgui.text(f"Y: {self.position[1]:.2f}")
        imgui.text(f"Z: {self.position[2]:.2f}")
        imgui.end()