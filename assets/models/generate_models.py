import bpy
import os
import math

def clean_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)

def create_pbr_material(name, base_color, metallic=0.0, roughness=0.5, emission=None, emission_strength=1.0):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = base_color
        bsdf.inputs["Metallic"].default_value = metallic
        bsdf.inputs["Roughness"].default_value = roughness
        if emission:
            # Blender 4+ Principled BSDF emission input is "Emission Color"
            if "Emission Color" in bsdf.inputs:
                bsdf.inputs["Emission Color"].default_value = emission
                bsdf.inputs["Emission Strength"].default_value = emission_strength
            elif "Emission" in bsdf.inputs:
                bsdf.inputs["Emission"].default_value = emission
                bsdf.inputs["Emission Strength"].default_value = emission_strength
    return mat

def build_bot():
    clean_scene()
    models_dir = os.path.dirname(__file__)

    # Materials
    mat_white = create_pbr_material("Mat_Bot_Body", (0.95, 0.96, 0.98, 1.0), metallic=0.1, roughness=0.25)
    mat_visor = create_pbr_material("Mat_Bot_Visor", (0.05, 0.07, 0.1, 1.0), metallic=0.9, roughness=0.1)
    mat_cyan_glow = create_pbr_material("Mat_Cyan_Glow", (0.0, 0.95, 0.85, 1.0), metallic=0.0, roughness=0.2, emission=(0.0, 1.0, 0.9, 1.0), emission_strength=3.0)
    mat_dark_metal = create_pbr_material("Mat_Dark_Metal", (0.2, 0.22, 0.26, 1.0), metallic=0.8, roughness=0.3)
    mat_gold_accent = create_pbr_material("Mat_Gold", (1.0, 0.8, 0.2, 1.0), metallic=0.9, roughness=0.2)

    # Root Object
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
    root = bpy.context.active_object
    root.name = "BOT_Root"

    # Main Body: rounded egg capsule
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=16, radius=0.45, location=(0, 0, 0.55))
    body = bpy.context.active_object
    body.name = "Body"
    body.scale = (0.9, 0.85, 1.0)
    body.data.materials.append(mat_white)
    bpy.ops.object.shade_smooth()
    body.parent = root

    # Visor screen
    bpy.ops.mesh.primitive_uv_sphere_add(segments=20, ring_count=12, radius=0.24, location=(0, 0.28, 0.62))
    visor = bpy.context.active_object
    visor.name = "Visor"
    visor.scale = (1.1, 0.45, 0.65)
    visor.data.materials.append(mat_visor)
    bpy.ops.object.shade_smooth()
    visor.parent = root

    # Left Eye (Emissive Cyan)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=8, radius=0.045, location=(-0.11, 0.38, 0.63))
    eye_l = bpy.context.active_object
    eye_l.name = "Eye_Left"
    eye_l.scale = (1.0, 0.5, 1.2)
    eye_l.data.materials.append(mat_cyan_glow)
    bpy.ops.object.shade_smooth()
    eye_l.parent = root

    # Right Eye (Emissive Cyan)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=8, radius=0.045, location=(0.11, 0.38, 0.63))
    eye_r = bpy.context.active_object
    eye_r.name = "Eye_Right"
    eye_r.scale = (1.0, 0.5, 1.2)
    eye_r.data.materials.append(mat_cyan_glow)
    bpy.ops.object.shade_smooth()
    eye_r.parent = root

    # Antenna Stem
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.02, depth=0.18, location=(0, 0, 1.05))
    stem = bpy.context.active_object
    stem.name = "Antenna_Stem"
    stem.data.materials.append(mat_dark_metal)
    bpy.ops.object.shade_smooth()
    stem.parent = root

    # Antenna Glowing Orb Tip
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=12, radius=0.065, location=(0, 0, 1.16))
    orb = bpy.context.active_object
    orb.name = "Antenna_Orb"
    orb.data.materials.append(mat_cyan_glow)
    bpy.ops.object.shade_smooth()
    orb.parent = root

    # Left Ear Disc
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.08, depth=0.04, location=(-0.40, 0.0, 0.60))
    ear_l = bpy.context.active_object
    ear_l.name = "Ear_Left"
    ear_l.rotation_euler = (0, math.radians(90), 0)
    ear_l.data.materials.append(mat_gold_accent)
    bpy.ops.object.shade_smooth()
    ear_l.parent = root

    # Right Ear Disc
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.08, depth=0.04, location=(0.40, 0.0, 0.60))
    ear_r = bpy.context.active_object
    ear_r.name = "Ear_Right"
    ear_r.rotation_euler = (0, math.radians(90), 0)
    ear_r.data.materials.append(mat_gold_accent)
    bpy.ops.object.shade_smooth()
    ear_r.parent = root

    # Left Foot
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=10, radius=0.12, location=(-0.20, 0.02, 0.12))
    foot_l = bpy.context.active_object
    foot_l.name = "Foot_Left"
    foot_l.scale = (0.9, 1.3, 0.65)
    foot_l.data.materials.append(mat_dark_metal)
    bpy.ops.object.shade_smooth()
    foot_l.parent = root

    # Right Foot
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=10, radius=0.12, location=(0.20, 0.02, 0.12))
    foot_r = bpy.context.active_object
    foot_r.name = "Foot_Right"
    foot_r.scale = (0.9, 1.3, 0.65)
    foot_r.data.materials.append(mat_dark_metal)
    bpy.ops.object.shade_smooth()
    foot_r.parent = root

    out_path = os.path.join(models_dir, "bot.glb")
    bpy.ops.export_scene.gltf(filepath=out_path, export_format='GLB', use_selection=False)
    print(f"Exported B.O.T to {out_path}")

def build_energy_fragment():
    clean_scene()
    models_dir = os.path.dirname(__file__)

    mat_crystal = create_pbr_material("Mat_Crystal", (0.1, 0.85, 1.0, 1.0), metallic=0.2, roughness=0.1, emission=(0.0, 0.9, 1.0, 1.0), emission_strength=4.0)
    mat_gold = create_pbr_material("Mat_Ring_Gold", (1.0, 0.82, 0.25, 1.0), metallic=0.9, roughness=0.2, emission=(0.8, 0.5, 0.05, 1.0), emission_strength=1.5)

    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
    root = bpy.context.active_object
    root.name = "EnergyFragment_Root"

    # Inner Octahedron / Diamond Crystal (Ico sphere with 1 subdivision = octahedron-like crystal)
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=0.42, location=(0, 0, 0.5))
    crystal = bpy.context.active_object
    crystal.name = "CrystalCore"
    crystal.scale = (0.7, 0.7, 1.2)
    crystal.data.materials.append(mat_crystal)
    crystal.parent = root

    # Outer floating orbit ring
    bpy.ops.mesh.primitive_torus_add(major_radius=0.48, minor_radius=0.035, location=(0, 0, 0.5))
    ring = bpy.context.active_object
    ring.name = "OrbitRing"
    ring.rotation_euler = (math.radians(35), math.radians(20), 0)
    ring.data.materials.append(mat_gold)
    ring.parent = root

    out_path = os.path.join(models_dir, "energy_fragment.glb")
    bpy.ops.export_scene.gltf(filepath=out_path, export_format='GLB', use_selection=False)
    print(f"Exported Energy Fragment to {out_path}")

def build_switch_pedestal():
    clean_scene()
    models_dir = os.path.dirname(__file__)

    mat_stone = create_pbr_material("Mat_Pedestal_Stone", (0.55, 0.52, 0.58, 1.0), metallic=0.1, roughness=0.8)
    mat_gold = create_pbr_material("Mat_Pedestal_Trim", (0.9, 0.75, 0.2, 1.0), metallic=0.8, roughness=0.3)
    mat_cyan_button = create_pbr_material("Mat_Button_Cyan", (0.0, 0.9, 1.0, 1.0), metallic=0.1, roughness=0.2, emission=(0.0, 1.0, 0.9, 1.0), emission_strength=3.5)

    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
    root = bpy.context.active_object
    root.name = "Switch_Root"

    # Base stone pedestal
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.6, depth=0.4, location=(0, 0, 0.2))
    base = bpy.context.active_object
    base.name = "PedestalBase"
    base.data.materials.append(mat_stone)
    base.parent = root

    # Upper Ring Trim
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.52, depth=0.1, location=(0, 0, 0.45))
    trim = bpy.context.active_object
    trim.name = "PedestalTrim"
    trim.data.materials.append(mat_gold)
    trim.parent = root

    # Glowing Interactive Core Button
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.32, depth=0.12, location=(0, 0, 0.52))
    button = bpy.context.active_object
    button.name = "PedestalButton"
    button.data.materials.append(mat_cyan_button)
    button.parent = root

    out_path = os.path.join(models_dir, "switch_pedestal.glb")
    bpy.ops.export_scene.gltf(filepath=out_path, export_format='GLB', use_selection=False)
    print(f"Exported Switch Pedestal to {out_path}")

def build_portal():
    clean_scene()
    models_dir = os.path.dirname(__file__)

    mat_arch = create_pbr_material("Mat_Portal_Arch", (0.4, 0.42, 0.48, 1.0), metallic=0.2, roughness=0.7)
    mat_gold = create_pbr_material("Mat_Portal_Gold", (1.0, 0.82, 0.25, 1.0), metallic=0.85, roughness=0.25, emission=(0.6, 0.4, 0.05, 1.0), emission_strength=1.5)
    mat_vortex = create_pbr_material("Mat_Portal_Vortex", (0.1, 0.7, 1.0, 1.0), metallic=0.0, roughness=0.1, emission=(0.0, 0.8, 1.0, 1.0), emission_strength=4.0)

    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
    root = bpy.context.active_object
    root.name = "Portal_Root"

    # Portal Ring / Arch
    bpy.ops.mesh.primitive_torus_add(major_radius=1.5, minor_radius=0.18, location=(0, 0, 1.6))
    arch = bpy.context.active_object
    arch.name = "PortalArch"
    arch.rotation_euler = (math.radians(90), 0, 0)
    arch.data.materials.append(mat_arch)
    arch.parent = root

    # Golden Runes / Pillars
    for i in [-1.4, 1.4]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.25, depth=0.6, location=(i, 0, 0.3))
        pillar = bpy.context.active_object
        pillar.name = f"PortalPillar_{i}"
        pillar.data.materials.append(mat_gold)
        pillar.parent = root

    # Portal Vortex Disk in the center
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=1.32, depth=0.04, location=(0, 0, 1.6))
    vortex = bpy.context.active_object
    vortex.name = "PortalVortex"
    vortex.rotation_euler = (math.radians(90), 0, 0)
    vortex.data.materials.append(mat_vortex)
    vortex.parent = root

    out_path = os.path.join(models_dir, "portal_gate.glb")
    bpy.ops.export_scene.gltf(filepath=out_path, export_format='GLB', use_selection=False)
    print(f"Exported Portal Gate to {out_path}")

def build_floating_island():
    clean_scene()
    models_dir = os.path.dirname(__file__)

    mat_grass = create_pbr_material("Mat_Grass_Stylized", (0.28, 0.72, 0.32, 1.0), metallic=0.0, roughness=0.7)
    mat_dirt = create_pbr_material("Mat_Cliff_Rock", (0.52, 0.42, 0.35, 1.0), metallic=0.05, roughness=0.9)

    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
    root = bpy.context.active_object
    root.name = "Island_Root"

    # Grassy top plateau (cylinder with rounded bevel/scale)
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=7.0, depth=0.8, location=(0, 0, -0.4))
    grass_top = bpy.context.active_object
    grass_top.name = "GrassTop"
    grass_top.data.materials.append(mat_grass)
    bpy.ops.object.shade_smooth()
    grass_top.parent = root

    # Rocky tapering underside (cone pointing down)
    bpy.ops.mesh.primitive_cone_add(vertices=16, radius1=6.8, radius2=0.5, depth=4.5, location=(0, 0, -3.0))
    rock_bottom = bpy.context.active_object
    rock_bottom.name = "RockBottom"
    rock_bottom.rotation_euler = (math.radians(180), 0, 0)
    rock_bottom.data.materials.append(mat_dirt)
    bpy.ops.object.shade_smooth()
    rock_bottom.parent = root

    out_path = os.path.join(models_dir, "floating_island.glb")
    bpy.ops.export_scene.gltf(filepath=out_path, export_format='GLB', use_selection=False)
    print(f"Exported Floating Island to {out_path}")

if __name__ == "__main__":
    build_bot()
    build_energy_fragment()
    build_switch_pedestal()
    build_portal()
    build_floating_island()
    print("All Blender 3D models generated and exported successfully!")
