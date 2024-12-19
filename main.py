import argparse
import math
import random
import sys
import bpy
from mathutils import Vector


def parse_arguments(args):
    """
    Parse command line arguments.

    Parameters
    ----------
    args : list of str
        Command line arguments passed to the script.

    Returns
    -------
    argparse.Namespace
        Parsed arguments namespace.
    """
    parser = argparse.ArgumentParser(
        description="Generate a series of cameras and lights in a Blender scene."
    )

    parser.add_argument(
        "--num_cameras", type=int, default=256,
        help="Number of cameras to create (default: 256)."
    )
    parser.add_argument(
        "--radius", type=float, default=25.0,
        help="Radius of the circle on which cameras are placed (default: 25)."
    )
    parser.add_argument(
        "--base_height", type=float, default=3.0,
        help="Base height at which cameras are placed (default: 3)."
    )
    parser.add_argument(
        "--height_variation", type=float, default=30.0,
        help="Maximum random vertical offset added to camera height (default: 30)."
    )

    # Look-at point parameters
    parser.add_argument(
        "--look_at_x", type=float, default=0.0,
        help="X-coordinate of the point all cameras look at (default: 0)."
    )
    parser.add_argument(
        "--look_at_y", type=float, default=0.0,
        help="Y-coordinate of the point all cameras look at (default: 0)."
    )
    parser.add_argument(
        "--look_at_z", type=float, default=0.0,
        help="Z-coordinate of the point all cameras look at (default: 0)."
    )

    parser.add_argument(
        "--use_selected_vertex", action='store_true',
        help="Use the first selected vertex of the active mesh object as the look-at point."
    )

    parser.add_argument(
        "--object_name", type=str,
        help="Name of the object from which to pick a vertex as a look-at point."
    )

    parser.add_argument(
        "--vertex_index", type=int,
        help="Index of the vertex in the specified object to use as the look-at point."
    )

    parser.add_argument(
        "--light_energy", type=float, default=1000.0,
        help="Energy (intensity) of the added point lights (default: 1000)."
    )
    parser.add_argument(
        "--light_offset", type=float, default=2.0,
        help="Distance in front of the camera to place the point light (default: 2)."
    )
    parser.add_argument(
        "--clean_scene", action='store_true',
        help="Remove existing cameras and lights before adding new ones."
    )

    return parser.parse_known_args(args)


def clean_scene():
    """
    Remove all existing cameras and lights from the current Blender scene.
    """
    for obj in bpy.context.scene.objects:
        if obj.type == 'CAMERA' or obj.type == 'LIGHT':
            bpy.data.objects.remove(obj, do_unlink=True)


def get_vertex_world_coordinate(obj_name, vertex_index):
    """
    Get the world coordinates of a specified vertex from a given object.

    Parameters
    ----------
    obj_name : str
        The name of the object.
    vertex_index : int
        The index of the vertex.

    Returns
    -------
    Vector
        World coordinates of the specified vertex.

    Raises
    ------
    ValueError
        If the object or vertex isn't found or is not a mesh.
    """
    obj = bpy.data.objects.get(obj_name)
    if not obj:
        raise ValueError(f"Object '{obj_name}' not found.")

    if obj.type != 'MESH':
        raise ValueError(f"Object '{obj_name}' is not a mesh.")

    mesh = obj.data
    if vertex_index < 0 or vertex_index >= len(mesh.vertices):
        raise ValueError(f"Vertex index {vertex_index} out of range for object '{obj_name}'.")

    return obj.matrix_world @ mesh.vertices[vertex_index].co


def get_selected_vertex_world_coordinate():
    """
    Get the world coordinates of the first selected vertex on the active mesh object.

    Returns
    -------
    Vector
        World coordinates of the first selected vertex.

    Raises
    ------
    ValueError
        If no active object or no selected vertex is found.
    TypeError
        If the active object is not a mesh.
    """
    if bpy.context.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')

    active_obj = bpy.context.active_object
    if not active_obj or active_obj.type != 'MESH':
        raise TypeError("Active object is not a mesh or no active object found.")

    selected_vertices = [v for v in active_obj.data.vertices if v.select]
    if not selected_vertices:
        raise ValueError("No vertices are selected. Please select a vertex on the object.")

    return active_obj.matrix_world @ selected_vertices[0].co


def determine_look_at_point(args):
    """
    Determine the look-at point based on the provided arguments.

    Priority:
    1. If --use_selected_vertex is given and a selected vertex is found.
    2. If --object_name and --vertex_index are given.
    3. Otherwise, use --look_at_x, --look_at_y, --look_at_z.

    Parameters
    ----------
    args : argparse.Namespace
        Parsed command line arguments.

    Returns
    -------
    Vector
        The look-at coordinates.
    """
    # Attempt using selected vertex
    if args.use_selected_vertex:
        try:
            return get_selected_vertex_world_coordinate()
        except (ValueError, TypeError):
            # Fallback if no valid selected vertex found
            pass

    # Attempt using specific object and vertex index
    if args.object_name and args.vertex_index is not None:
        try:
            return get_vertex_world_coordinate(args.object_name, args.vertex_index)
        except ValueError:
            # If this fails, we revert to default
            pass

    # Default to specified coordinates
    return Vector((args.look_at_x, args.look_at_y, args.look_at_z))


def add_camera_and_light(index, angle, radius, base_height, height_variation, look_at, light_energy, light_offset):
    """
    Add a single camera and corresponding light into the scene.

    Parameters
    ----------
    index : int
        The camera index (for naming).
    angle : float
        The angle around the circle where the camera is placed.
    radius : float
        The radius from the center point where the camera is placed.
    base_height : float
        Base height for the camera.
    height_variation : float
        Maximum random additional height to add to the camera's position.
    look_at : Vector
        The point in 3D space the camera should look at.
    light_energy : float
        The intensity (energy) of the point light.
    light_offset : float
        The distance in front of the camera where the light is placed.
    """
    # Calculate camera position
    x = radius * math.cos(angle)
    y = radius * math.sin(angle)
    z = base_height + random.uniform(0, height_variation)

    # Add camera
    bpy.ops.object.camera_add(location=(x, y, z))
    cam = bpy.context.active_object
    cam.name = f"Camera_{index}"

    # Orient camera towards the target point
    direction = look_at - cam.location
    cam.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()

    # Add a point light at the camera location
    bpy.ops.object.light_add(type='POINT', location=(x, y, z))
    light = bpy.context.active_object
    light.name = f"Light_{index}"
    light.data.energy = light_energy
    light.parent = cam

    # Offset the light in front of the camera
    light.location = cam.location + cam.matrix_world.to_quaternion() @ Vector((0, 0, light_offset))


def main(args):
    """
    Main entry point for the script. Sets up the scene with multiple cameras and lights.
    """
    # Parse arguments
    parsed_args, _ = parse_arguments(args)

    num_cameras = parsed_args.num_cameras
    radius = parsed_args.radius
    base_height = parsed_args.base_height
    height_variation = parsed_args.height_variation
    look_at = determine_look_at_point(parsed_args)
    light_energy = parsed_args.light_energy
    light_offset = parsed_args.light_offset
    clean = parsed_args.clean_scene

    # Clean up existing cameras/lights if requested
    if clean:
        clean_scene()

    # Add specified number of cameras
    for i in range(num_cameras):
        angle = i * (2 * math.pi / num_cameras)
        add_camera_and_light(
            index=i+1,
            angle=angle,
            radius=radius,
            base_height=base_height,
            height_variation=height_variation,
            look_at=look_at,
            light_energy=light_energy,
            light_offset=light_offset
        )


if __name__ == "__main__":
    #Change this if not running from command line
    #sys.argv = ['main.py', '--num_cameras=10', '--radius=20', '--clean_scene']
    main(sys.argv)
