import bpy
import os
import math

def clean_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)

def get_or_create_mat(name, base_color, metallic=0.0, roughness=0.5, emission=None, emission_strength=1.0):
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

def create_interactive_palette():
    return {
        "stone": get_or_create_mat("Mat_Ancient_Stone", (0.52, 0.49, 0.45, 1.0), roughness=0.75),
        "dark_stone": get_or_create_mat("Mat_Dark_Ruin_Stone", (0.35, 0.33, 0.30, 1.0), roughness=0.8),
        "gold_trim": get_or_create_mat("Mat_Ornamental_Gold", (0.98, 0.82, 0.22, 1.0), metallic=0.85, roughness=0.25),
        "cyan_crystal": get_or_create_mat("Mat_Energy_CyanCore", (0.0, 0.92, 1.0, 1.0), metallic=0.15, roughness=0.1, emission=(0.0, 0.98, 1.0, 1.0), emission_strength=4.5),
        "cyan_portal": get_or_create_mat("Mat_Portal_CyanVortex", (0.05, 0.75, 1.0, 1.0), metallic=0.0, roughness=0.1, emission=(0.0, 0.85, 1.0, 1.0), emission_strength=4.0),
        "gold_rune": get_or_create_mat("Mat_Rune_Gold", (1.0, 0.80, 0.15, 1.0), metallic=0.8, roughness=0.2, emission=(0.9, 0.6, 0.05, 1.0), emission_strength=2.0),
    }

def build_interactives():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    source_dir = os.path.join(script_dir, "..", "source")
    arch_dir = os.path.join(script_dir, "..", "..", "models", "architecture")
    col_dir = os.path.join(script_dir, "..", "..", "models", "collectibles")
    root_model_dir = os.path.join(script_dir, "..", "..", "models")
    os.makedirs(source_dir, exist_ok=True)
    os.makedirs(arch_dir, exist_ok=True)
    os.makedirs(col_dir, exist_ok=True)

    # =========================================================================
    # 1. UPGRADED ENERGY FRAGMENT (energy_fragment.glb)
    # =========================================================================
    clean_scene()
    palette = create_interactive_palette()
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
    root_frag = bpy.context.active_object
    root_frag.name = "EnergyFragment_Root"

    # Faceted Core Diamond Crystal
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=0.45, location=(0, 0, 0.55))
    crystal = bpy.context.active_object
    crystal.name = "CrystalCore"
    crystal.scale = (0.75, 0.75, 1.25)
    crystal.data.materials.append(palette["cyan_crystal"])
    crystal.parent = root_frag

    # Inner Gold Gyro Ring (inclined 35°)
    bpy.ops.mesh.primitive_torus_add(major_radius=0.55, minor_radius=0.038, location=(0, 0, 0.55))
    ring1 = bpy.context.active_object
    ring1.name = "OrbitRing_Inner"
    ring1.rotation_euler = (math.radians(35), math.radians(20), 0)
    ring1.data.materials.append(palette["gold_trim"])
    ring1.parent = root_frag

    # Outer Gold Gyro Ring (inclined -45°)
    bpy.ops.mesh.primitive_torus_add(major_radius=0.68, minor_radius=0.032, location=(0, 0, 0.55))
    ring2 = bpy.context.active_object
    ring2.name = "OrbitRing_Outer"
    ring2.rotation_euler = (math.radians(-45), math.radians(-30), 0)
    ring2.data.materials.append(palette["gold_trim"])
    ring2.parent = root_frag

    # Floating Orbit Satellite Dots
    for s_idx, (sx, sy, sz) in enumerate([(0.65, 0, 0.55), (-0.65, 0, 0.55), (0, 0.65, 0.55)]):
        bpy.ops.mesh.primitive_uv_sphere_add(segments=8, ring_count=6, radius=0.045, location=(sx, sy, sz))
        sat = bpy.context.active_object
        sat.name = f"OrbitDot_{s_idx}"
        sat.data.materials.append(palette["cyan_crystal"])
        sat.parent = root_frag

    p_frag_col = os.path.join(col_dir, "energy_fragment.glb")
    p_frag_root = os.path.join(root_model_dir, "energy_fragment.glb")
    bpy.ops.export_scene.gltf(filepath=p_frag_col, export_format='GLB', use_selection=False)
    bpy.ops.export_scene.gltf(filepath=p_frag_root, export_format='GLB', use_selection=False)
    print(f"✓ Exported Energy Fragment to {p_frag_col} & {p_frag_root}")

    # =========================================================================
    # 2. UPGRADED SWITCH PEDESTAL (switch_pedestal.glb)
    # =========================================================================
    clean_scene()
    palette = create_interactive_palette()
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
    root_switch = bpy.context.active_object
    root_switch.name = "Switch_Root"

    # Octagonal Carved Stone Base
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.72, depth=0.25, location=(0, 0, 0.125))
    s_base = bpy.context.active_object
    s_base.name = "PedestalBase"
    s_base.data.materials.append(palette["dark_stone"])
    s_base.parent = root_switch

    # Mid Stone Tier
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.60, depth=0.35, location=(0, 0, 0.35))
    s_mid = bpy.context.active_object
    s_mid.name = "PedestalMid"
    s_mid.data.materials.append(palette["stone"])
    s_mid.parent = root_switch

    # Golden Rune Inlay Collar
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.55, depth=0.10, location=(0, 0, 0.55))
    s_collar = bpy.context.active_object
    s_collar.name = "PedestalTrim"
    s_collar.data.materials.append(palette["gold_trim"])
    s_collar.parent = root_switch

    # Depressible Central Glowing Switch Button
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.36, depth=0.14, location=(0, 0, 0.62))
    s_btn = bpy.context.active_object
    s_btn.name = "PedestalButton"
    s_btn.data.materials.append(palette["cyan_crystal"])
    s_btn.parent = root_switch

    p_switch_arch = os.path.join(arch_dir, "switch_pedestal.glb")
    p_switch_root = os.path.join(root_model_dir, "switch_pedestal.glb")
    bpy.ops.export_scene.gltf(filepath=p_switch_arch, export_format='GLB', use_selection=False)
    bpy.ops.export_scene.gltf(filepath=p_switch_root, export_format='GLB', use_selection=False)
    print(f"✓ Exported Switch Pedestal to {p_switch_arch} & {p_switch_root}")

    # =========================================================================
    # 3. UPGRADED PORTAL GATE (portal_gate.glb)
    # =========================================================================
    clean_scene()
    palette = create_interactive_palette()
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
    root_portal = bpy.context.active_object
    root_portal.name = "Portal_Root"

    # Massive Ancient Stone Arch Ring
    bpy.ops.mesh.primitive_torus_add(major_radius=1.85, minor_radius=0.24, location=(0, 0, 1.95))
    arch = bpy.context.active_object
    arch.name = "PortalArch"
    arch.rotation_euler = (math.radians(90), 0, 0)
    arch.data.materials.append(palette["stone"])
    arch.parent = root_portal

    # Golden Inlay Ring
    bpy.ops.mesh.primitive_torus_add(major_radius=1.65, minor_radius=0.045, location=(0, 0, 1.95))
    arch_gold = bpy.context.active_object
    arch_gold.name = "PortalGoldRing"
    arch_gold.rotation_euler = (math.radians(90), 0, 0)
    arch_gold.data.materials.append(palette["gold_trim"])
    arch_gold.parent = root_portal

    # Left & Right Stone Anchor Pillars
    for side, x in [("L", -1.75), ("R", 1.75)]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.35, depth=1.2, location=(x, 0, 0.6))
        pil = bpy.context.active_object
        pil.name = f"PortalPillar_{side}"
        pil.data.materials.append(palette["dark_stone"])
        pil.parent = root_portal

        # Golden capital top on pillar
        bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.42, depth=0.15, location=(x, 0, 1.25))
        cap = bpy.context.active_object
        cap.name = f"PillarCap_{side}"
        cap.data.materials.append(palette["gold_trim"])
        cap.parent = root_portal

        # Floating Levitating Focus Shard
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=0.22, location=(x, 0, 1.75))
        shard = bpy.context.active_object
        shard.name = f"FocusShard_{side}"
        shard.scale = (0.7, 0.7, 1.4)
        shard.data.materials.append(palette["cyan_crystal"])
        shard.parent = root_portal

    # Swirling Central Portal Vortex Disc
    bpy.ops.mesh.primitive_cylinder_add(vertices=28, radius=1.60, depth=0.04, location=(0, 0, 1.95))
    vortex = bpy.context.active_object
    vortex.name = "PortalVortex"
    vortex.rotation_euler = (math.radians(90), 0, 0)
    vortex.data.materials.append(palette["cyan_portal"])
    vortex.parent = root_portal

    # Concentric inner ripple ring
    bpy.ops.mesh.primitive_torus_add(major_radius=0.9, minor_radius=0.035, location=(0, 0, 1.95))
    ripple = bpy.context.active_object
    ripple.name = "PortalRipple"
    ripple.rotation_euler = (math.radians(90), 0, 0)
    ripple.data.materials.append(palette["gold_rune"])
    ripple.parent = root_portal

    p_portal_arch = os.path.join(arch_dir, "portal_gate.glb")
    p_portal_root = os.path.join(root_model_dir, "portal_gate.glb")
    bpy.ops.export_scene.gltf(filepath=p_portal_arch, export_format='GLB', use_selection=False)
    bpy.ops.export_scene.gltf(filepath=p_portal_root, export_format='GLB', use_selection=False)
    print(f"✓ Exported Portal Gate to {p_portal_arch} & {p_portal_root}")

    # Save complete source .blend file
    blend_path = os.path.join(source_dir, "interactive_props.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print(f"✓ Saved Interactive source .blend to {blend_path}")

if __name__ == "__main__":
    build_interactives()
    print("All interactive models generated successfully!")
