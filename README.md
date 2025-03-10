# Balls on Pluto
![image](https://github.com/user-attachments/assets/bade5b2a-ddc9-4cbe-8dc4-159917cc476f)


## Description
"**Balls on Pluto**" is a 3D scene renderer built using **OpenGL** and **Python**. The project features an interactive environment with dynamic lighting, shadow mapping, skybox rendering, and various 3D models, including the player character, terrain, and collectible objects. This project is designed to showcase real-time 3D rendering techniques and interactive scene controls.

## Main Features
- **Two camera modes**: 
  - Third-Person (TPP)
  - Free mode
- **Dynamic lighting system** with multiple light sources
- **Real-time shadow mapping**
- **Skybox** with texture-switching capability
- **Particle system** (falling leaves animation)
- **Terrain collision detection**
- **Ball collection system** with score counter
- **FPS counter** and **position display**
- **Context menu** for scene control
- **Dynamic terrain generation** with various objects (rocks, cacti, grass, etc.)

## Technical Details
The project uses the following technologies and libraries:
- **OpenGL**: For 3D rendering
- **GLFW**: For window management and input handling
- **GLM**: For mathematical operations (transformations, vectors, matrices)
- **ImGui**: For user interface rendering
- **Freetype**: For text rendering
- **PIL**: For texture loading
- **NumPy**: For numerical operations

## Main Components

### 1. Camera System
- Switch between Third-Person (TPP) and Free camera modes
- Smooth movement and rotation with camera height control (in Free mode)

### 2. Lighting System
- Multiple light sources (directional and point lights) with different colors
- Support for **Blinn-Phong** and **Phong** lighting models

### 3. Object System
- Various 3D models (terrain, rocks, cacti, balls, etc.)
- **Collision detection** for terrain and objects
- **Dynamic terrain generation** with different objects (rocks, cacti, grass, etc.)

### 4. User Interface
- **FPS counter**
- **Position display**
- **Score counter**
- **Context menu** for scene settings (lighting control, skybox texture switching, particle effects)

## Controls

### Basic Movement:
- `W`: Move forward
- `S`: Move backward
- `A`: Rotate left
- `D`: Rotate right
- `C`: Switch camera mode (TPP/Free)

### Camera Height Control (Free Mode):
- `0`: Raise camera
- `9`: Lower camera

### Mouse Control:
- **Right Click**: Open context menu

## Context Menu Functions:
- **Select skybox texture**
- **Control lighting**:
  - Turn lighting on/off
  - Switch between Phong and Blinn-Phong lighting models
  - Turn light animation on/off
  - Control individual light sources
- **Turn falling leaves effect on/off**
- **Hummingbird effects** (Normal/Reflecting/Refracting)

## Gameplay Elements:
- **Collect balls** scattered across the terrain
- **Navigate through obstacles** (rocks, cacti)
- **Explore the terrain** while avoiding collisions with objects
- Track the **score** of collected balls

## Performance Features:
- **Efficient shadow mapping**
- Optimized **terrain collision detection**
- **Height calculation caching system**
- **Dynamic instancing** for particle objects

## Other Features:
- Terrain includes **height-based collision detection**
- Objects have **individual collision boundaries**
- Scene includes **proper depth testing** and **alpha blending**
- Support for various screen resolutions with **proper scaling**

## Installation & Setup

### Prerequisites:
Make sure you have Python installed on your machine. Then, install the required dependencies using `pip`:

```bash
pip install PyOpenGL glfw imgui freetype numpy pillow

![image](https://github.com/user-attachments/assets/7bf1fda8-2c94-4e20-8e2e-810130c22a8d)
![image](https://github.com/user-attachments/assets/defc9a8f-7a7f-4014-841d-34ae1cec47f3)
![image](https://github.com/user-attachments/assets/32ffbead-7247-46b3-8bdc-bc4e347dce25)
![image](https://github.com/user-attachments/assets/43ac4e16-1f5f-4724-9f0b-075c2c13070e)
![image](https://github.com/user-attachments/assets/0f1fad4e-5267-49a2-af3e-6ab8b11af5c0)




