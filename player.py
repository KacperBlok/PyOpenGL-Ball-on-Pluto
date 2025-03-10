import glm
import numpy as np
from time import time

class Player:
    def __init__(self, model, ground_model):
        self.model = model
        self.ground_model = ground_model
        self.position = glm.vec3(-15.0, 0.0, -15.0)
        self.direction = glm.vec3(0.0, 0.0, -1.0)
        self.up = glm.vec3(0.0, 1.0, 0.0)
        self.angle = 90.0
        self.speed = 5.0
        self.rotation_speed = 90.0
        self.max_slope_angle = 30.0
        self.collision_radius = 0.5
        self.collision_height = 1.0
        self.collision_objects = []
        self.height_offset = 0.1
        self.ground_offset = -0.8  # terrain offset
        self.collected_balls = 0
        self.ball_collection_radius = 1.0  # Radius for ball collection
        
        # Cache for terrain data
        self._vertices = None
        self._height_cache = {}
        self._last_cache_clear = time()
        self._cache_lifetime = 1  
        self._init_terrain_data()

    def check_ball_collection(self, ball_positions):
        collected_indices = []
        for i, transform in enumerate(ball_positions):
            ball_pos = glm.vec3(transform[3])
            distance = glm.length(glm.vec2(self.position.x - ball_pos.x, self.position.z - ball_pos.z))
            if distance < self.ball_collection_radius:
                collected_indices.append(i)
        return collected_indices
    
    def _init_terrain_data(self):
        try:
            self._vertices = np.array(self.ground_model.vertices, dtype=np.float32).reshape(-1, 3)
            initial_height = self.get_height_at_position(self.position)
            print(f"Initial terrain height: {initial_height}")  # Debug
            if initial_height != float('-inf'):
                self.position.y = initial_height + self.height_offset
                print(f"Initial player height: {self.position.y}")  # Debug
        except Exception as e:
            print(f"Error initializing terrain data: {e}")
            self._vertices = np.array([], dtype=np.float32)

    def add_collision_object(self, model, transform, scale=1.0, height_offset=0.0):
        self.collision_objects.append({
            'model': model,
            'transform': transform,
            'scale': scale,
            'height_offset': height_offset  # height offset to collision object
        })

    def _clear_old_cache(self):
        current_time = time()
        if current_time - self._last_cache_clear > self._cache_lifetime:
            self._height_cache.clear()
            self._last_cache_clear = current_time

    def get_height_at_position(self, pos):
        try:
            # Round position to a certain precision for better caching
            cache_key = (round(pos.x, 1), round(pos.z, 1))
            
            # Check cache
            if cache_key in self._height_cache:
                return self._height_cache[cache_key]

            if self._vertices is None or len(self._vertices) == 0:
                return -0.8

            min_height = float('-inf')
            
            for i in range(0, len(self._vertices), 3):
                if i + 2 >= len(self._vertices):
                    break

                v1 = glm.vec3(self._vertices[i][0], self._vertices[i][1], self._vertices[i][2])
                v2 = glm.vec3(self._vertices[i+1][0], self._vertices[i+1][1], self._vertices[i+1][2])
                v3 = glm.vec3(self._vertices[i+2][0], self._vertices[i+2][1], self._vertices[i+2][2])

                if self.point_in_triangle(pos.x, pos.z, v1.x, v1.z, v2.x, v2.z, v3.x, v3.z):
                    height = self.interpolate_height(pos.x, pos.z, v1, v2, v3)
                    min_height = max(min_height, height)

            result = min_height if min_height != float('-inf') else -0.8
            result += self.ground_offset
            self._height_cache[cache_key] = result
            return result

        except Exception as e:
            print(f"Error in get_height_at_position: {e}")
            return self.ground_offset

    def point_in_triangle(self, px, pz, x1, z1, x2, z2, x3, z3):
        def sign(p1x, p1z, p2x, p2z, p3x, p3z):
            return (p1x - p3x) * (p2z - p3z) - (p2x - p3x) * (p1z - p3z)
        
        try:
            d1 = sign(px, pz, x1, z1, x2, z2)
            d2 = sign(px, pz, x2, z2, x3, z3)
            d3 = sign(px, pz, x3, z3, x1, z1)

            has_neg = (d1 < 0) or (d2 < 0) or (d3 < 0)
            has_pos = (d1 > 0) or (d2 > 0) or (d3 > 0)

            return not (has_neg and has_pos)
        except Exception as e:
            print(f"Error in point_in_triangle: {e}")
            return False

    def interpolate_height(self, x, z, v1, v2, v3):
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

    def get_slope_angle(self, pos):
        try:
            center_height = self.get_height_at_position(pos)
            if center_height == float('-inf'):
                return 0.0

            # Check slope in four directions
            max_angle = 0.0
            radius = 0.5
            for angle in [0, 90, 180, 270]:
                rad = np.radians(angle)
                offset = glm.vec3(radius * np.cos(rad), 0, radius * np.sin(rad))
                point_height = self.get_height_at_position(pos + offset)
                
                if point_height != float('-inf'):
                    delta_height = abs(point_height - center_height)
                    slope_angle = np.degrees(np.arctan2(delta_height, radius))
                    max_angle = max(max_angle, slope_angle)

                    # Optimization: if max_slope_angle is exceeded, we can break
                    if max_angle > self.max_slope_angle:
                        return max_angle

            return max_angle

        except Exception as e:
            print(f"Error in get_slope_angle: {e}")
            return 0.0

    def check_object_collision(self, position):
        try:
            for obj in self.collision_objects:
                if obj['model'] == self.ground_model:
                    continue

                model_pos = glm.vec3(obj['transform'][3])
                # Account for height offset of the object in collision detection
                adjusted_model_y = model_pos.y + obj.get('height_offset', 0.0)
                
                # Check for collision with the height offset considered
                if abs(position.y - adjusted_model_y) < self.collision_height:
                    distance = glm.length(glm.vec2(position.x - model_pos.x, position.z - model_pos.z))
                    if distance < (self.collision_radius + obj['scale']):
                        return True
            return False
        except Exception as e:
            print(f"Error in check_object_collision: {e}")
            return False

    def update(self, delta_time, keys):
        try:
            self._clear_old_cache()

            # Rotation handling
            if keys['a']:
                self.angle += self.rotation_speed * delta_time
                self.direction = glm.vec3(
                    glm.sin(glm.radians(self.angle)),
                    0.0,
                    -glm.cos(glm.radians(self.angle))
                )
            if keys['d']:
                self.angle -= self.rotation_speed * delta_time
                self.direction = glm.vec3(
                    glm.sin(glm.radians(self.angle)),
                    0.0,
                    -glm.cos(glm.radians(self.angle))
                )

            # Movement handling
            if keys['w'] or keys['s']:
                # Calculate new position
                move_dir = self.direction if keys['w'] else -self.direction
                proposed_position = self.position + move_dir * self.speed * delta_time

                # Check if the new position is within the terrain bounds
                TERRAIN_BOUNDS_X = 59.0 
                TERRAIN_BOUNDS_Z = 100.0 
                if (abs(proposed_position.x) <= TERRAIN_BOUNDS_X and 
                    abs(proposed_position.z) <= TERRAIN_BOUNDS_Z):
                    
                    ground_height = self.get_height_at_position(proposed_position)
                    if ground_height != float('-inf'):
                        # Set proper height
                        proposed_position.y = ground_height + self.height_offset

                        # Check slope only if height change is significant
                        slope_ok = True
                        if abs(proposed_position.y - self.position.y) > 0.1:
                            slope_angle = self.get_slope_angle(proposed_position)
                            slope_ok = slope_angle <= self.max_slope_angle

                        # Update position if everything is OK
                        if slope_ok and not self.check_object_collision(proposed_position):
                            self.position = proposed_position

        except Exception as e:
            print(f"Error in update: {e}")
            print(f"Current position: {self.position}")

    def get_model_matrix(self):
        try:
            model_matrix = glm.mat4(1.0)
            model_matrix = glm.translate(model_matrix, self.position)
            model_matrix = glm.rotate(model_matrix, glm.radians(self.angle), glm.vec3(0, 1, 0))
            model_matrix = glm.scale(model_matrix, glm.vec3(0.5))
            return model_matrix
        except Exception as e:
            print(f"Error in get_model_matrix: {e}")
            return glm.mat4(1.0)
