import glm
import math

class Camera:
    def __init__(self, position, front, up, angle):
        # Basic camera properties
        self.position = glm.vec3(position)
        self.front = glm.vec3(front)
        self.up = glm.vec3(up)
        self.angle = angle
        
        # Camera control parameters
        self.speed = 5.0  # Camera movement speed
        self.rotation_speed = 90.0  # Rotation speed in degrees per second
        
        # Third-person camera parameters
        self.offset_distance = 5.0  # Distance from the character
        self.offset_height = 2.0    # Height above the character
        
        # Camera mode
        self.camera_mode = "third_person"  # "third_person" or "free"
        
        # Helper vectors
        self.right = glm.normalize(glm.cross(self.front, self.up))
        self.world_up = glm.vec3(0.0, 1.0, 0.0)

    def update(self, delta_time, keys):
        """
        Update camera position and orientation in free mode
        """
        if self.camera_mode == "free":
            # Camera rotation
            if keys['a']:
                self.angle += self.rotation_speed * delta_time
            if keys['d']:
                self.angle -= self.rotation_speed * delta_time

            # Update the front vector based on the angle
            self.front.x = glm.sin(glm.radians(self.angle))
            self.front.z = -glm.cos(glm.radians(self.angle))
            self.front = glm.normalize(self.front)

            # Update the right vector
            self.right = glm.normalize(glm.cross(self.front, self.world_up))

            # Move forward/backward
            if keys['w']:
                self.position += self.front * self.speed * delta_time
            if keys['s']:
                self.position -= self.front * self.speed * delta_time

            # Move up/down
            if keys['0']:
                self.position.y += self.speed * delta_time
            if keys['9']:
                self.position.y -= self.speed * delta_time

    def toggle_camera_mode(self):
        """
        Switch between camera modes
        """
        if self.camera_mode == "third_person":
            # Switch to free mode
            self.camera_mode = "free"
            # Keep the current orientation
            self.angle = glm.degrees(math.atan2(self.front.x, -self.front.z))
        else:
            # Switch to third-person mode
            self.camera_mode = "third_person"
            # Reset orientation
            self.front = glm.vec3(0.0, 0.0, -1.0)
            self.angle = 0.0

    def follow_player(self, player_pos, player_direction):
        """
        Update camera position in third-person mode
        """
        if self.camera_mode == "third_person":
            # Calculate camera offset relative to the player
            offset = -player_direction * self.offset_distance
            offset.y = self.offset_height
            
            # Set the camera position
            self.position = player_pos + offset
            
            # Set the point the camera is looking at (slightly above the character)
            target = player_pos + glm.vec3(0.0, 1.0, 0.0)
            self.front = glm.normalize(target - self.position)

    def get_view_matrix(self):
        """
        Returns the view matrix for the current camera position and orientation
        """
        return glm.lookAt(self.position, self.position + self.front, self.up)

    def get_position(self):
        """
        Returns the current camera position
        """
        return self.position

    def get_front(self):
        """
        Returns the camera's direction vector
        """
        return self.front

    def get_up(self):
        """
        Returns the camera's up vector
        """
        return self.up

    def get_right(self):
        """
        Returns the camera's right vector
        """
        return self.right

    def set_position(self, position):
        """
        Sets the camera position
        """
        self.position = glm.vec3(position)

    def set_front(self, front):
        """
        Sets the camera's look direction
        """
        self.front = glm.normalize(glm.vec3(front))
        self.right = glm.normalize(glm.cross(self.front, self.world_up))

    def set_up(self, up):
        """
        Sets the camera's up vector
        """
        self.up = glm.normalize(glm.vec3(up))

    def set_angle(self, angle):
        """
        Sets the camera's rotation angle
        """
        self.angle = angle
        # Update the front vector based on the new angle
        self.front.x = glm.sin(glm.radians(self.angle))
        self.front.z = -glm.cos(glm.radians(self.angle))
        self.front = glm.normalize(self.front)
