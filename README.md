# Blender Camera and Light Setup Script

This script arranges a specified number of cameras and lights in a circular pattern around a target point or vertex in a Blender scene. It provides several customizable parameters via command-line arguments. It also allows selecting the camera look-at point either by direct coordinates, a specific vertex in an object, or a currently selected vertex on the active mesh.

## Features

- **Circular Camera Placement:** Positions multiple cameras evenly spaced on a circle around a specified point.
- **Look-at Options:**
  - Direct coordinates (`--look_at_x`, `--look_at_y`, `--look_at_z`)
  - A selected vertex on the active object (`--use_selected_vertex`)
  - A specific vertex by object name and vertex index (`--object_name`, `--vertex_index`)
- **Random Height Variation:** Adds variation to camera heights for more dynamic setups.
- **Clean Scene Option:** Remove all existing cameras and lights (`--clean_scene`) before adding new ones.

## Requirements

- Blender (2.8+ recommended)
- Python included with Blender (no additional installations required)
- Script relies on `bpy` and `mathutils` which are included with Blender.

## Installation

1. Clone or download the repository.
2. Open your `.blend` file in Blender.
3. Place `main.py` in a directory accessible by Blender (same folder as your `.blend` for convenience).

## Usage

**From the Command Line:**  
You can run the script by passing arguments after a double-dash (`--`) which separates Blender’s arguments from the script’s arguments.

```bash
blender /path/to/your_scene.blend --python main.py -- --num_cameras=10 --radius=20 --clean_scene
