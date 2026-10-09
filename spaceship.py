"""Run inside Blender: blender --background --python spaceship.py"""
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector


def material(name, color, metallic=0.0, emission=0.0):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1)
    mat.use_nodes = True
    shader = mat.node_tree.nodes.get('Principled BSDF')
    shader.inputs['Base Color'].default_value = (*color, 1)
    shader.inputs['Metallic'].default_value = metallic
    shader.inputs['Roughness'].default_value = 0.3
    if emission:
        socket = shader.inputs.get('Emission Color') or shader.inputs.get('Emission')
        socket.default_value = (*color, 1)
        shader.inputs['Emission Strength'].default_value = emission
    return mat


def finish(obj, name, mat, parent):
    obj.name = name
    obj.data.materials.append(mat)
    obj.parent = parent
    for polygon in obj.data.polygons:
        polygon.use_smooth = True
    return obj


def cone(name, position, radius1, radius2, length, mat, parent, direction=1):
    bpy.ops.mesh.primitive_cone_add(
        vertices=32, radius1=radius1, radius2=radius2, depth=length,
        location=position, rotation=(0, direction * math.pi / 2, 0))
    return finish(bpy.context.object, name, mat, parent)


def build():
    # This script builds a new scene. Run it in a new Blender file.
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    scene = bpy.context.scene
    scene.frame_start, scene.frame_end = 1, 96
    scene.render.fps = 24
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'CPU'
    scene.cycles.samples = 16
    scene.cycles.use_denoising = True
    scene.render.resolution_x, scene.render.resolution_y = 640, 480
    scene.render.resolution_percentage = 100
    scene.render.film_transparent = True
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGBA'
    scene.world = bpy.data.worlds.new('Lighting only')
    scene.world.use_nodes = True
    scene.world.node_tree.nodes['Background'].inputs[0].default_value = (0.1, 0.14, 0.22, 1)
    scene.world.node_tree.nodes['Background'].inputs[1].default_value = 0.4
    scene.view_settings.view_transform = 'Standard'

    bpy.ops.object.empty_add()
    ship = bpy.context.object
    ship.name = 'Spaceship'
    hull = material('Pearl silver', (0.62, 0.7, 0.8), 0.65)
    dark = material('Engine graphite', (0.045, 0.065, 0.095), 0.75)
    glass = material('Blue canopy', (0.015, 0.15, 0.32), 0.5)
    blue = material('Blue flame', (0.005, 0.12, 1.0), emission=2.5)
    core = material('Cyan flame core', (0.02, 0.55, 1.0), emission=2.0)

    cone('Fuselage', (0, 0, 0), 0.65, 0.45, 3.2, hull, ship)
    cone('Nose', (2.15, 0, 0), 0.45, 0.02, 1.1, hull, ship)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=12, location=(0.65, 0, 0.45))
    canopy = finish(bpy.context.object, 'Cockpit', glass, ship)
    canopy.scale = (0.9, 0.38, 0.28)

    # Swept wings with a small thickness, mirrored across the fuselage.
    for side in (-1, 1):
        outline = [(0.65, side * 0.4), (-1.35, side * 2.05), (-1.55, side * 0.4)]
        vertices = [(x, y, z) for z in (-0.1, 0.06) for x, y in outline]
        mesh = bpy.data.meshes.new('Wing mesh')
        mesh.from_pydata(vertices, [], [(0, 2, 1), (3, 4, 5), (0, 1, 4, 3),
                                      (1, 2, 5, 4), (2, 0, 3, 5)])
        mesh.update()
        wing = bpy.data.objects.new('Wing', mesh)
        scene.collection.objects.link(wing)
        finish(wing, 'Left wing' if side < 0 else 'Right wing', hull, ship)
        bevel = wing.modifiers.new('Soft edges', 'BEVEL')
        bevel.width, bevel.segments = 0.04, 2

        y = side * 0.9
        cone('Engine pod', (-1.2, y, -0.1), 0.3, 0.25, 1.35, dark, ship)
        cone('Nozzle', (-1.94, y, -0.1), 0.3, 0.24, 0.25, dark, ship)
        # Empty at the nozzle anchors the flame while its length flickers.
        bpy.ops.object.empty_add(location=(-2.07, y, -0.1))
        flame = bpy.context.object
        flame.name = 'Thruster flame'
        flame.parent = ship
        cone('Blue plume', (-0.9, 0, 0), 0.225, 0.0, 1.8, blue, flame, -1)
        cone('Cyan core', (-0.48, 0, 0), 0.23, 0.0, 0.96, core, flame, -1)
        for frame in range(1, 98, 4):
            flame.scale.x = 1 + 0.12 * math.sin(frame * 1.7 + side)
            flame.keyframe_insert(data_path='scale', index=0, frame=frame)

    # A linear frame driver gives constant forward speed across Blender versions.
    ship.driver_add('location', 0).driver.expression = '-3 + 6 * (frame - 1) / 95'

    bpy.ops.object.camera_add(location=(9, -16, 10))
    camera = bpy.context.object
    camera.rotation_euler = (Vector((0, 0, 0)) - camera.location).to_track_quat('-Z', 'Y').to_euler()
    camera.data.type, camera.data.ortho_scale = 'ORTHO', 16
    scene.camera = camera
    for position, power, size in (((1, -5, 8), 1500, 7), ((-3, 5, 4), 1000, 5)):
        bpy.ops.object.light_add(type='AREA', location=position)
        lamp = bpy.context.object
        lamp.data.energy, lamp.data.shape, lamp.data.size = power, 'DISK', size
        lamp.rotation_euler = (-lamp.location).to_track_quat('-Z', 'Y').to_euler()

    scene.frame_set(1)
    # Runnable check of the requested motion and transparency.
    first_x = ship.location.x
    scene.frame_set(96)
    assert ship.location.x > first_x and scene.render.film_transparent
    assert all(obj.parent for obj in scene.objects if obj.type == 'MESH')
    scene.frame_set(1)
    output = Path(__file__).resolve().parent / 'output'
    output.mkdir(exist_ok=True)
    scene.render.filepath = str(output / 'frame_')
    bpy.ops.wm.save_as_mainfile(filepath=str(output / 'spaceship.blend'))
    args = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    if '--preview' in args:
        scene.frame_set(48)
        scene.render.filepath = str(output / 'preview.png')
        bpy.ops.render.render(write_still=True)
    elif '--render' in args:
        bpy.ops.render.render(animation=True)


if __name__ == '__main__':
    build()
