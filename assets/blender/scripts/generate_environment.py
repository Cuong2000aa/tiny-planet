import bpy
import os
import math

def clean_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)

def get_or_create_mat(name, base_color, metallic=0.0, roughness=0.6, emission=None, emission_strength=1.0):
    mat = bpy.data.materials.get(name)
    if mat:
        return mat
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = base_color
        bsdf.inputs["Metallic"].default_value = metallic
        bsdf.inputs["Roughness"].default_value = roughness
        if emission:
            if "Emission Color" in bsdf.inputs:
                bsdf.inputs["Emission Color"].default_value = emission
                bsdf.inputs["Emission Strength"].default_value = emission_strength
            elif "Emission" in bsdf.inputs:
                bsdf.inputs["Emission"].default_value = emission
                bsdf.inputs["Emission Strength"].default_value = emission_strength
    return mat

def create_palette():
    return {
        "grass": get_or_create_mat("Mat_Grass_Lush", (0.24, 0.64, 0.26, 1.0), roughness=0.75),
        "grass_trim": get_or_create_mat("Mat_Grass_Highlight", (0.34, 0.74, 0.28, 1.0), roughness=0.7),
        "rock": get_or_create_mat("Mat_Cliff_Sandstone", (0.48, 0.40, 0.34, 1.0), roughness=0.85),
        "dark_rock": get_or_create_mat("Mat_Cliff_Basalt", (0.32, 0.28, 0.25, 1.0), roughness=0.9),
        "path": get_or_create_mat("Mat_Path_Cobble", (0.68, 0.62, 0.54, 1.0), roughness=0.8),
        "ancient": get_or_create_mat("Mat_Ancient_Stone", (0.58, 0.56, 0.52, 1.0), roughness=0.65),
        "cyan_rune": get_or_create_mat("Mat_Rune_Cyan", (0.0, 0.9, 1.0, 1.0), roughness=0.2, emission=(0.0, 0.95, 1.0, 1.0), emission_strength=3.5),
        "cloud": get_or_create_mat("Mat_Cloud_Fluffy", (0.95, 0.96, 1.0, 1.0), roughness=0.4),
    }

def build_environment():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    source_dir = os.path.join(script_dir, "..", "source")
    env_model_dir = os.path.join(script_dir, "..", "..", "models", "environment")
    root_model_dir = os.path.join(script_dir, "..", "..", "models")
    os.makedirs(source_dir, exist_ok=True)
    os.makedirs(env_model_dir, exist_ok=True)

    # =========================================================================
    # 1. MAIN AWAKENING ISLAND (island_awakening.glb)
    # =========================================================================
    clean_scene()
    palette = create_palette()
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
    root_island1 = bpy.context.active_object
    root_island1.name = "Island_Awakening_Root"

    # Grassy Upper Plateau (radius 7.0, height 0.9 at z=-0.45)
    bpy.ops.mesh.primitive_cylinder_add(vertices=28, radius=7.0, depth=0.9, location=(0, 0, -0.45))
    top_grass = bpy.context.active_object
    top_grass.name = "GrassPlateau"
    top_grass.data.materials.append(palette["grass"])
    bpy.ops.object.shade_smooth()
    top_grass.parent = root_island1

    # Overhanging Stylized Grass Rim Fringe
    bpy.ops.mesh.primitive_torus_add(major_radius=7.05, minor_radius=0.18, location=(0, 0, -0.05))
    grass_rim = bpy.context.active_object
    grass_rim.name = "GrassRim"
    grass_rim.data.materials.append(palette["grass_trim"])
    bpy.ops.object.shade_smooth()
    grass_rim.parent = root_island1

    # Winding Cobblestone Pathway embedded in grass
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=1.6, depth=0.06, location=(0, 0, 0.02))
    path_center = bpy.context.active_object
    path_center.name = "Path_Spawn"
    path_center.data.materials.append(palette["path"])
    path_center.parent = root_island1

    path_coords = [(0, 1.8, 0.015), (0.4, 3.5, 0.015), (0.2, 5.2, 0.015)]
    for idx, (px, py, pz) in enumerate(path_coords):
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(px, py, pz))
        p_stone = bpy.context.active_object
        p_stone.name = f"Path_Stone_{idx}"
        p_stone.scale = (1.4, 1.4, 0.05)
        p_stone.rotation_euler = (0, 0, math.radians(idx * 15))
        p_stone.data.materials.append(palette["path"])
        p_stone.parent = root_island1

    # Upper Cliff Stratum
    bpy.ops.mesh.primitive_cylinder_add(vertices=20, radius=6.7, depth=1.6, location=(0, 0, -1.6))
    cliff_mid = bpy.context.active_object
    cliff_mid.name = "Cliff_Upper"
    cliff_mid.scale = (1.0, 0.98, 1.0)
    cliff_mid.data.materials.append(palette["rock"])
    bpy.ops.object.shade_smooth()
    cliff_mid.parent = root_island1

    # Lower Inverted Rock Spire
    bpy.ops.mesh.primitive_cone_add(vertices=16, radius1=6.4, radius2=0.6, depth=3.6, location=(0, 0, -3.8))
    cliff_bottom = bpy.context.active_object
    cliff_bottom.name = "Cliff_Spire"
    cliff_bottom.rotation_euler = (math.radians(180), 0, 0)
    cliff_bottom.data.materials.append(palette["dark_rock"])
    bpy.ops.object.shade_smooth()
    cliff_bottom.parent = root_island1

    # Floating Detached Rock Shards hanging below
    for i, (rx, ry, rz, sc) in enumerate([(-2.2, 1.5, -5.2, 0.45), (2.0, -1.2, -5.6, 0.55), (0.5, 2.4, -4.9, 0.38)]):
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=sc, location=(rx, ry, rz))
        shard = bpy.context.active_object
        shard.name = f"FloatingShard_{i}"
        shard.scale = (0.7, 0.8, 1.4)
        shard.data.materials.append(palette["rock"])
        shard.parent = root_island1

    p1 = os.path.join(env_model_dir, "island_awakening.glb")
    p1_root = os.path.join(root_model_dir, "floating_island.glb")
    bpy.ops.export_scene.gltf(filepath=p1, export_format='GLB', use_selection=False)
    bpy.ops.export_scene.gltf(filepath=p1_root, export_format='GLB', use_selection=False)
    print(f"✓ Exported Awakening Island to {p1} & {p1_root}")

    # =========================================================================
    # 2. SANCTUARY ISLAND (island_sanctuary.glb)
    # =========================================================================
    clean_scene()
    palette = create_palette()
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
    root_sanctuary = bpy.context.active_object
    root_sanctuary.name = "Island_Sanctuary_Root"

    bpy.ops.mesh.primitive_cylinder_add(vertices=28, radius=7.0, depth=0.9, location=(0, 0, -0.45))
    s_grass = bpy.context.active_object
    s_grass.name = "SanctuaryGrass"
    s_grass.data.materials.append(palette["grass"])
    bpy.ops.object.shade_smooth()
    s_grass.parent = root_sanctuary

    bpy.ops.mesh.primitive_torus_add(major_radius=7.05, minor_radius=0.18, location=(0, 0, -0.05))
    s_rim = bpy.context.active_object
    s_rim.name = "SanctuaryGrassRim"
    s_rim.data.materials.append(palette["grass_trim"])
    bpy.ops.object.shade_smooth()
    s_rim.parent = root_sanctuary

    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=4.2, depth=0.18, location=(0, 0, 0.08))
    dais = bpy.context.active_object
    dais.name = "AncientDais"
    dais.data.materials.append(palette["ancient"])
    dais.parent = root_sanctuary

    bpy.ops.mesh.primitive_torus_add(major_radius=3.2, minor_radius=0.045, location=(0, 0, 0.18))
    rune_ring = bpy.context.active_object
    rune_ring.name = "RuneRing"
    rune_ring.data.materials.append(palette["cyan_rune"])
    rune_ring.parent = root_sanctuary

    bpy.ops.mesh.primitive_cone_add(vertices=16, radius1=6.5, radius2=0.5, depth=4.2, location=(0, 0, -3.2))
    s_cliff = bpy.context.active_object
    s_cliff.name = "SanctuaryCliff"
    s_cliff.rotation_euler = (math.radians(180), 0, 0)
    s_cliff.data.materials.append(palette["rock"])
    bpy.ops.object.shade_smooth()
    s_cliff.parent = root_sanctuary

    p2 = os.path.join(env_model_dir, "island_sanctuary.glb")
    bpy.ops.export_scene.gltf(filepath=p2, export_format='GLB', use_selection=False)
    print(f"✓ Exported Sanctuary Island to {p2}")

    # =========================================================================
    # 3. EXIT PORTAL ISLAND (island_portal.glb)
    # =========================================================================
    clean_scene()
    palette = create_palette()
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
    root_portal_isl = bpy.context.active_object
    root_portal_isl.name = "Island_Portal_Root"

    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=5.5, depth=0.9, location=(0, 0, -0.45))
    p_grass = bpy.context.active_object
    p_grass.name = "PortalGrass"
    p_grass.data.materials.append(palette["grass"])
    bpy.ops.object.shade_smooth()
    p_grass.parent = root_portal_isl

    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=3.2, depth=0.25, location=(0, 0, 0.12))
    p_dais = bpy.context.active_object
    p_dais.name = "PortalDais"
    p_dais.data.materials.append(palette["ancient"])
    p_dais.parent = root_portal_isl

    bpy.ops.mesh.primitive_cone_add(vertices=16, radius1=5.2, radius2=0.4, depth=3.8, location=(0, 0, -3.0))
    p_cliff = bpy.context.active_object
    p_cliff.name = "PortalCliff"
    p_cliff.rotation_euler = (math.radians(180), 0, 0)
    p_cliff.data.materials.append(palette["rock"])
    bpy.ops.object.shade_smooth()
    p_cliff.parent = root_portal_isl

    p3 = os.path.join(env_model_dir, "island_portal.glb")
    bpy.ops.export_scene.gltf(filepath=p3, export_format='GLB', use_selection=False)
    print(f"✓ Exported Portal Island to {p3}")

    # =========================================================================
    # 4. MODULAR STEPPING STONE (stepping_stone.glb)
    # =========================================================================
    clean_scene()
    palette = create_palette()
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
    root_step = bpy.context.active_object
    root_step.name = "SteppingStone_Root"

    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=1.35, depth=0.35, location=(0, 0, 0))
    step_body = bpy.context.active_object
    step_body.name = "StepBody"
    step_body.data.materials.append(palette["ancient"])
    step_body.parent = root_step

    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=1.20, depth=0.06, location=(0, 0, 0.18))
    step_moss = bpy.context.active_object
    step_moss.name = "StepMoss"
    step_moss.data.materials.append(palette["grass"])
    step_moss.parent = root_step

    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=0.32, location=(0, 0, -0.42))
    step_crystal = bpy.context.active_object
    step_crystal.name = "LevitationCrystal"
    step_crystal.scale = (0.7, 0.7, 1.3)
    step_crystal.data.materials.append(palette["cyan_rune"])
    step_crystal.parent = root_step

    p4 = os.path.join(env_model_dir, "stepping_stone.glb")
    bpy.ops.export_scene.gltf(filepath=p4, export_format='GLB', use_selection=False)
    print(f"✓ Exported Stepping Stone to {p4}")

    # =========================================================================
    # 5. DISTANT FLOATING VISTA ISLANDS (distant_island.glb)
    # =========================================================================
    clean_scene()
    palette = create_palette()
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
    root_dist = bpy.context.active_object
    root_dist.name = "DistantIsland_Root"

    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=4.0, depth=0.6, location=(0, 0, 0))
    dist_top = bpy.context.active_object
    dist_top.data.materials.append(palette["grass"])
    dist_top.parent = root_dist

    bpy.ops.mesh.primitive_cone_add(vertices=8, radius1=3.8, radius2=0.2, depth=3.0, location=(0, 0, -1.8))
    dist_bot = bpy.context.active_object
    dist_bot.rotation_euler = (math.radians(180), 0, 0)
    dist_bot.data.materials.append(palette["rock"])
    dist_bot.parent = root_dist

    p5 = os.path.join(env_model_dir, "distant_island.glb")
    bpy.ops.export_scene.gltf(filepath=p5, export_format='GLB', use_selection=False)
    print(f"✓ Exported Distant Island to {p5}")

    # =========================================================================
    # 6. STYLIZED FLUFFY CLOUD (cloud_stylized.glb)
    # =========================================================================
    clean_scene()
    palette = create_palette()
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
    root_cloud = bpy.context.active_object
    root_cloud.name = "Cloud_Root"

    cloud_spheres = [
        (0, 0, 0, 1.2),
        (1.1, 0.2, -0.1, 0.95),
        (-1.0, -0.1, -0.1, 0.90),
        (0.5, -0.5, 0.1, 0.80),
        (-0.6, 0.5, 0.0, 0.85),
    ]
    for idx, (cx, cy, cz, cr) in enumerate(cloud_spheres):
        bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=12, radius=cr, location=(cx, cy, cz))
        puff = bpy.context.active_object
        puff.name = f"CloudPuff_{idx}"
        puff.data.materials.append(palette["cloud"])
        bpy.ops.object.shade_smooth()
        puff.parent = root_cloud

    p6 = os.path.join(env_model_dir, "cloud_stylized.glb")
    bpy.ops.export_scene.gltf(filepath=p6, export_format='GLB', use_selection=False)
    print(f"✓ Exported Cloud to {p6}")

    # Save complete environment source .blend
    blend_path = os.path.join(source_dir, "environment_islands.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print(f"✓ Saved Environment islands source .blend to {blend_path}")

if __name__ == "__main__":
    build_environment()
    print("Environment islands generation complete!")
