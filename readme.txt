

Project Name: Balls on Pluto

Description:
The project presents a 3D scene renderer built using OpenGL and Python. It features an interactive environment with dynamic lighting, shadow mapping, skybox rendering, and various 3D models, including the player character, terrain, and collectible objects.

Main Features:
- Two camera modes: Third-Person (TPP) and Free
- Dynamic lighting system with multiple light sources
- Real-time shadow mapping
- Skybox with texture-switching capability
- Particle system (falling leaves animation)
- Terrain collision detection
- Ball collection system with a score counter
- FPS counter and position display
- Context menu for scene control
- Dynamic terrain generation with various objects (rocks, cacti, grass, etc.)

Technical Details:
The project uses the following technologies and libraries:
- OpenGL for 3D rendering
- GLFW for window management and input handling
- GLM for mathematical operations
- ImGui for user interface
- Freetype for text rendering
- PIL for texture loading
- NumPy for numerical operations

Main Components:
1. Camera System
   - Switch between TPP and Free mode
   - Smooth movement and rotation

2. Lighting System
   - Multiple light sources with different colors
   - Support for directional and point lights
   - Blinn-Phong lighting model

3. Object System
   - Various 3D models with textures
   - Collision detection
   - Dynamic terrain generation

4. User Interface
   - FPS counter
   - Position display
   - Score counter
   - Context menu for scene settings

Controls:

- **Basic Movement:
  - `W` - Move forward
  - `S` - Move backward
  - `A` - Rotate left
  - `D` - Rotate right
  - `C` - Switch camera mode (TPP/Free)

- Camera Height Control (Free Mode):
  - `0` - Raise camera
  - `9` - Lower camera

- Mouse Control:
  - `Right Click` - Open context menu

**Context Menu Functions:
- Select skybox texture
- Control lighting
   - Turn lighting on/off
   - Switch between Phong and Blinn-Phong lighting models
   - Turn light animation on/off
   - Control individual light sources
- Turn falling leaves effect on/off
- Hummingbird effects (Normal/Reflecting/Refracting)

Gameplay Elements:
- Collect balls scattered across the terrain
- Navigate through obstacles (rocks, cacti)
- Explore the terrain while avoiding collisions with objects
- Track the score of collected balls

Performance Features:
- Efficient shadow mapping
- Optimized terrain collision detection
- Height calculation caching system
- Dynamic instancing for particle objects

Other:
- Terrain includes height-based collision detection
- Objects have individual collision boundaries
- Scene includes proper depth testing and alpha blending
- Support for various screen resolutions with proper scaling

