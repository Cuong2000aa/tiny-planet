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

def create_props_palette():
    return {
        "trunk": get_or_create_mat("Mat_Wood_Trunk", (0.42, 0.28, 0.18, 1.0), roughness=0.85),
        "leaves_main": get_or_create_mat("Mat_Leaves_Green", (0.22, 0.62, 0.28, 1.0), roughness=0.65),
        "leaves_light": get_or_create_mat("Mat_Leaves_Light", (0.34, 0.74, 0.32, 1.0), roughness=0.6),
        "bush": get_or_create_mat("Mat_Bush_Green", (0.26, 0.68, 0.30, 1.0), roughness=0.7),
        "flower_stem": get_or_create_mat("Mat_Plant_Stem", (0.28, 0.58, 0.22, 1.0), roughness=0.6),
        "flower_pink": get_or_create_mat("Mat_Petal_Pink", (0.95, 0.35, 0.65, 1.0), roughness=0.4, emission=(0.9, 0.2, 0.5, 1.0), emission_strength=1.2),
        "flower_blue": get_or_create_mat("Mat_Petal_Blue", (0.15, 0.65, 0.95, 1.0), roughness=0.4, emission=(0.1, 0.6, 1.0, 1.0), emission_strength=1.5),
        "flower_yellow": get_or_create_mat("Mat_Petal_Yellow", (1.0, 0.85, 0.25, 1.0), roughness=0.4),
        "mush_cap": get_or_create_mat("Mat_Mushroom_Cap", (0.92, 0.25, 0.28, 1.0), roughness=0.4, emission=(0.9, 0.15, 0.2, 1.0), emission_strength=1.5),
        "mush_stem": get_or_create_mat("Mat_Mushroom_Stem", (0.92, 0.90, 0.82, 1.0), roughness=0.5),
        "stone": get_or_create_mat("Mat_Prop_Stone", (0.52, 0.48, 0.45, 1.0), roughness=0.8),
        "ancient_ruin": get_or_create_mat("Mat_Ancient_Ruin", (0.58, 0.55, 0.50, 1.0), roughness=0.7),
        "gold_trim": get_or_create_mat("Mat_Ruin_Gold", (0.95, 0.78, 0.22, 1.0), metallic=0.85, roughness=0.3),
        "crystal_cyan": get_or_create_mat("Mat_Crystal_Cyan", (0.05, 0.85, 1.0, 1.0), metallic=0.1, roughness=0.15, emission=(0.0, 0.95, 1.0, 1.0), emission_strength=4.0),
        "crystal_gold": get_or_create_mat("Mat_Crystal_Gold", (1.0, 0.82, 0.25, 1.0), metallic=0.2, roughness=0.15, emission=(1.0, 0.75, 0.1, 1.0), emission_strength=3.5),
    }

def build_props():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    source_dir = os.path.join(script_dir, "..", "source")
    props_dir = os.path.join(script_dir, "..", "..", "models", "props")
    os.makedirs(source_dir, exist_ok=True)
    os.makedirs(props_dir, exist_ok=True)

    # =========================================================================
    # 1. STYLIZED CANOPY TREE (tree_stylized.glb)
    # =========================================================================
    clean_scene()
    palette = create_props_palette()
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
    root_tree = bpy.context.active_object
    root_tree.name = "Tree_Root"

    # Tapered stylized trunk with slight organic lean
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.32, depth=2.4, location=(0, 0, 1.2))
    trunk = bpy.context.active_object
    trunk.name = "TreeTrunk"
    trunk.scale = (1.0, 0.9, 1.0)
    trunk.rotation_euler = (math.radians(3), math.radians(-2), 0)
    trunk.data.materials.append(palette["trunk"])
    bpy.ops.object.shade_smooth()
    trunk.parent = root_tree

    # Fluffy Foliage Canopies (low-poly stacked puff clusters)
    foliage_specs = [
        (0.0, 0.05, 2.5, 1.25, palette["leaves_main"]),
        (0.45, -0.3, 2.9, 0.95, palette["leaves_light"]),
        (-0.4, 0.35, 2.8, 0.90, palette["leaves_light"]),
        (0.05, 0.1, 3.4, 0.85, palette["leaves_main"]),
    ]
    for idx, (fx, fy, fz, fr, mat) in enumerate(foliage_specs):
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=fr, location=(fx, fy, fz))
        f_puff = bpy.context.active_object
        f_puff.name = f"Foliage_{idx}"
        f_puff.scale = (1.1, 1.1, 0.9)
        f_puff.data.materials.append(mat)
        bpy.ops.object.shade_smooth()
        f_puff.parent = root_tree

    p_tree = os.path.join(props_dir, "tree_stylized.glb")
    bpy.ops.export_scene.gltf(filepath=p_tree, export_format='GLB', use_selection=False)
    print(f"✓ Exported Stylized Tree to {p_tree}")

    # =========================================================================
    # 2. STYLIZED BUSH (bush_stylized.glb)
    # =========================================================================
    clean_scene()
    palette = create_props_palette()
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
    root_bush = bpy.context.active_object
    root_bush.name = "Bush_Root"

    bush_spheres = [
        (0, 0, 0.45, 0.55),
        (-0.35, 0.1, 0.35, 0.42),
        (0.35, -0.1, 0.38, 0.45),
        (0.1, 0.32, 0.32, 0.38),
    ]
    for idx, (bx, by, bz, br) in enumerate(bush_spheres):
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=br, location=(bx, by, bz))
        b_puff = bpy.context.active_object
        b_puff.name = f"BushPuff_{idx}"
        b_puff.data.materials.append(palette["bush"])
        bpy.ops.object.shade_smooth()
        b_puff.parent = root_bush

    p_bush = os.path.join(props_dir, "bush_stylized.glb")
    bpy.ops.export_scene.gltf(filepath=p_bush, export_format='GLB', use_selection=False)
    print(f"✓ Exported Stylized Bush to {p_bush}")

    # =========================================================================
    # 3. COLORFUL FLOWER CLUSTER (flower_cluster.glb)
    # =========================================================================
    clean_scene()
    palette = create_props_palette()
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
    root_flower = bpy.context.active_object
    root_flower.name = "FlowerCluster_Root"

    flower_specs = [
        (-0.25, -0.15, 0.25, palette["flower_pink"]),
        (0.20, 0.22, 0.32, palette["flower_blue"]),
        (-0.05, 0.30, 0.22, palette["flower_yellow"]),
        (0.28, -0.22, 0.28, palette["flower_pink"]),
    ]
    for idx, (fx, fy, fz, petal_mat) in enumerate(flower_specs):
        # Stem
        bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.02, depth=fz, location=(fx, fy, fz/2.0))
        stem = bpy.context.active_object
        stem.name = f"Stem_{idx}"
        stem.data.materials.append(palette["flower_stem"])
        stem.parent = root_flower

        # Blossom head
        bpy.ops.mesh.primitive_cylinder_add(vertices=10, radius=0.10, depth=0.05, location=(fx, fy, fz))
        blossom = bpy.context.active_object
        blossom.name = f"Blossom_{idx}"
        blossom.data.materials.append(petal_mat)
        blossom.parent = root_flower

    p_flower = os.path.join(props_dir, "flower_cluster.glb")
    bpy.ops.export_scene.gltf(filepath=p_flower, export_format='GLB', use_selection=False)
    print(f"✓ Exported Flower Cluster to {p_flower}")

    # =========================================================================
    # 4. GLOWING MUSHROOMS (mushrooms_stylized.glb)
    # =========================================================================
    clean_scene()
    palette = create_props_palette()
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
    root_mush = bpy.context.active_object
    root_mush.name = "Mushrooms_Root"

    mush_specs = [
        (0, 0, 0.35, 0.28),
        (-0.24, 0.15, 0.24, 0.20),
        (0.22, -0.12, 0.18, 0.15),
    ]
    for idx, (mx, my, mz, cap_r) in enumerate(mush_specs):
        # Stem
        bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=cap_r * 0.28, depth=mz, location=(mx, my, mz/2.0))
        m_stem = bpy.context.active_object
        m_stem.name = f"MushStem_{idx}"
        m_stem.data.materials.append(palette["mush_stem"])
        m_stem.parent = root_mush

        # Cap (hemisphere)
        bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=8, radius=cap_r, location=(mx, my, mz))
        m_cap = bpy.context.active_object
        m_cap.name = f"MushCap_{idx}"
        m_cap.scale = (1.0, 1.0, 0.65)
        m_cap.data.materials.append(palette["mush_cap"])
        bpy.ops.object.shade_smooth()
        m_cap.parent = root_mush

    p_mush = os.path.join(props_dir, "mushrooms_stylized.glb")
    bpy.ops.export_scene.gltf(filepath=p_mush, export_format='GLB', use_selection=False)
    print(f"✓ Exported Mushrooms to {p_mush}")

    # =========================================================================
    # 5. CHISELED ROCK BOULDER (rock_boulder.glb)
    # =========================================================================
    clean_scene()
    palette = create_props_palette()
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
    root_rock = bpy.context.active_object
    root_rock.name = "RockBoulder_Root"

    # Main chiseled boulder (Ico sphere with 1 subdivision scale-flattened and beveled)
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=0.9, location=(0, 0, 0.55))
    rock_main = bpy.context.active_object
    rock_main.name = "RockMain"
    rock_main.scale = (1.2, 0.9, 0.75)
    rock_main.data.materials.append(palette["stone"])
    rock_main.parent = root_rock

    # Secondary side pebble
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=0.45, location=(0.85, 0.35, 0.30))
    rock_sub = bpy.context.active_object
    rock_sub.name = "RockSub"
    rock_sub.scale = (0.8, 1.1, 0.7)
    rock_sub.data.materials.append(palette["stone"])
    rock_sub.parent = root_rock

    p_rock = os.path.join(props_dir, "rock_boulder.glb")
    bpy.ops.export_scene.gltf(filepath=p_rock, export_format='GLB', use_selection=False)
    print(f"✓ Exported Rock Boulder to {p_rock}")

    # =========================================================================
    # 6. GLOWING CRYSTAL CLUSTER (crystal_cluster.glb)
    # =========================================================================
    clean_scene()
    palette = create_props_palette()
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
    root_crys = bpy.context.active_object
    root_crys.name = "CrystalCluster_Root"

    # Base rock mound
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.65, depth=0.2, location=(0, 0, 0.1))
    c_base = bpy.context.active_object
    c_base.data.materials.append(palette["stone"])
    c_base.parent = root_crys

    # Central tall cyan crystal
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.22, depth=1.3, location=(0, 0, 0.75))
    c_tall = bpy.context.active_object
    c_tall.name = "Crystal_Main"
    c_tall.rotation_euler = (math.radians(6), math.radians(-4), 0)
    c_tall.data.materials.append(palette["crystal_cyan"])
    c_tall.parent = root_crys

    # Side secondary crystals
    bpy.ops.mesh.primitive_cylinder_add(vertices=5, radius=0.14, depth=0.85, location=(-0.30, 0.15, 0.45))
    c_side1 = bpy.context.active_object
    c_side1.name = "Crystal_Side1"
    c_side1.rotation_euler = (math.radians(-18), math.radians(12), 0)
    c_side1.data.materials.append(palette["crystal_cyan"])
    c_side1.parent = root_crys

    bpy.ops.mesh.primitive_cylinder_add(vertices=5, radius=0.12, depth=0.75, location=(0.28, -0.22, 0.40))
    c_side2 = bpy.context.active_object
    c_side2.name = "Crystal_Side2"
    c_side2.rotation_euler = (math.radians(22), math.radians(18), 0)
    c_side2.data.materials.append(palette["crystal_gold"])
    c_side2.parent = root_crys

    p_crys = os.path.join(props_dir, "crystal_cluster.glb")
    bpy.ops.export_scene.gltf(filepath=p_crys, export_format='GLB', use_selection=False)
    print(f"✓ Exported Crystal Cluster to {p_crys}")

    # =========================================================================
    # 7. ANCIENT RUIN PILLAR (ancient_pillar.glb)
    # =========================================================================
    clean_scene()
    palette = create_props_palette()
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
    root_pillar = bpy.context.active_object
    root_pillar.name = "AncientPillar_Root"

    # Pedestal base
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.6, depth=0.3, location=(0, 0, 0.15))
    pil_base = bpy.context.active_object
    pil_base.data.materials.append(palette["ancient_ruin"])
    pil_base.parent = root_pillar

    # Broken Column shaft
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.42, depth=2.2, location=(0, 0, 1.35))
    pil_shaft = bpy.context.active_object
    pil_shaft.name = "PillarShaft"
    pil_shaft.data.materials.append(palette["ancient_ruin"])
    pil_shaft.parent = root_pillar

    # Golden Rune Collar Ring
    bpy.ops.mesh.primitive_torus_add(major_radius=0.46, minor_radius=0.06, location=(0, 0, 1.8))
    pil_gold = bpy.context.active_object
    pil_gold.name = "PillarGold"
    pil_gold.data.materials.append(palette["gold_trim"])
    pil_gold.parent = root_pillar

    p_pil = os.path.join(props_dir, "ancient_pillar.glb")
    bpy.ops.export_scene.gltf(filepath=p_pil, export_format='GLB', use_selection=False)
    print(f"✓ Exported Ancient Pillar to {p_pil}")

    # =========================================================================
    # 8. CELESTIAL LANTERN (lantern_pedestal.glb)
    # =========================================================================
    clean_scene()
    palette = create_props_palette()
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
    root_lan = bpy.context.active_object
    root_lan.name = "Lantern_Root"

    # Base & Post
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.35, depth=0.2, location=(0, 0, 0.1))
    lan_base = bpy.context.active_object
    lan_base.data.materials.append(palette["ancient_ruin"])
    lan_base.parent = root_lan

    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.12, depth=1.6, location=(0, 0, 0.95))
    lan_post = bpy.context.active_object
    lan_post.data.materials.append(palette["ancient_ruin"])
    lan_post.parent = root_lan

    # Lantern Housing & Glowing Core
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.32, depth=0.4, location=(0, 0, 1.9))
    lan_cage = bpy.context.active_object
    lan_cage.data.materials.append(palette["gold_trim"])
    lan_cage.parent = root_lan

    bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=8, radius=0.18, location=(0, 0, 1.9))
    lan_orb = bpy.context.active_object
    lan_orb.name = "LanternOrb"
    lan_orb.data.materials.append(palette["crystal_cyan"])
    lan_orb.parent = root_lan

    p_lan = os.path.join(props_dir, "lantern_pedestal.glb")
    bpy.ops.export_scene.gltf(filepath=p_lan, export_format='GLB', use_selection=False)
    print(f"✓ Exported Lantern Pedestal to {p_lan}")

    # Save complete source .blend file for all props
    blend_path = os.path.join(source_dir, "environment_props.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print(f"✓ Saved Props source .blend to {blend_path}")

if __name__ == "__main__":
    build_props()
    print("All environment props generated successfully!")
