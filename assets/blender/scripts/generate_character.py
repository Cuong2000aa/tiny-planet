"""
Tiny Planet — B.O.T Protagonist Character Production Script (Master-Class Polish)
Authoritative Implementation matching "Character Turnaround Sheet"
Blender 5.2.3 LTS | Godot 4.7.1 Compatibility | WebGL 2.0 Web-First
"""

import bpy
import math
import os

def create_pbr_material(name, base_color, roughness=0.18, metallic=0.0, emission=None, emission_strength=1.0, coat=0.0):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    if not bsdf:
        bsdf = nodes.new(type="ShaderNodeBsdfPrincipled")
    if bsdf:
        bsdf.inputs['Base Color'].default_value = base_color
        bsdf.inputs['Roughness'].default_value = roughness
        bsdf.inputs['Metallic'].default_value = metallic
        if 'Coat' in bsdf.inputs and coat > 0:
            bsdf.inputs['Coat'].default_value = coat
        if emission:
            bsdf.inputs['Emission Color'].default_value = emission
            bsdf.inputs['Emission Strength'].default_value = emission_strength
    return mat

def create_bone(arm_data, name, parent_name=None, head=(0,0,0), tail=(0,0,1)):
    b = arm_data.edit_bones.new(name)
    b.head = head
    b.tail = tail
    if parent_name and parent_name in arm_data.edit_bones:
        b.parent = arm_data.edit_bones[parent_name]
    return b

def assign_vertex_group(obj, group_name, weight=1.0):
    vg = obj.vertex_groups.new(name=group_name)
    verts = [v.index for v in obj.data.vertices]
    if verts:
        vg.add(verts, weight, 'REPLACE')

def apply_bevel_subsurf(obj, bevel_width=0.06, bevel_segments=3, subsurf_levels=2):
    bpy.context.view_layer.objects.active = obj
    if bevel_width > 0:
        mod_bev = obj.modifiers.new(name="Bevel", type='BEVEL')
        mod_bev.width = bevel_width
        mod_bev.segments = bevel_segments
        bpy.ops.object.modifier_apply(modifier="Bevel")
    if subsurf_levels > 0:
        mod_sub = obj.modifiers.new(name="Subsurf", type='SUBSURF')
        mod_sub.levels = subsurf_levels
        bpy.ops.object.modifier_apply(modifier="Subsurf")
    bpy.ops.object.shade_smooth()

def build_refined_bot():
    print("=== Building Refined Master-Class B.O.T Character in Blender 5.2.3 LTS ===")
    
    # 1. Reset scene
    bpy.ops.wm.read_factory_settings(use_empty=True)

    # 2. PBR Materials — Exact Turnaround Sheet Palette (Vibrant, Saturated, Glossy)
    mat_white = create_pbr_material("Mat_WhiteCeramic", (0.98, 0.98, 0.99, 1.0), roughness=0.12, coat=0.45)
    mat_royal_blue = create_pbr_material("Mat_RoyalBlue", (0.04, 0.22, 0.92, 1.0), roughness=0.18, metallic=0.08)
    mat_golden_yellow = create_pbr_material("Mat_GoldenYellow", (1.0, 0.76, 0.04, 1.0), roughness=0.25, metallic=0.0)
    mat_dark_navy = create_pbr_material("Mat_DarkNavy", (0.05, 0.06, 0.10, 1.0), roughness=0.32, metallic=0.18)
    mat_visor = create_pbr_material("Mat_ObsidianVisor", (0.015, 0.015, 0.02, 1.0), roughness=0.03, coat=1.0)
    mat_cyan_glow = create_pbr_material(
        "Mat_CyanGlow",
        (0.10, 0.95, 1.0, 1.0),
        roughness=0.08,
        emission=(0.10, 0.96, 1.0, 1.0),
        emission_strength=9.0
    )

    # 3. Create Armature & Bone Hierarchy
    bpy.ops.object.armature_add(location=(0, 0, 0))
    arm_obj = bpy.context.active_object
    arm_obj.name = "BOT_Armature"
    arm_data = arm_obj.data
    arm_data.name = "BOT_ArmatureData"

    bpy.ops.object.mode_set(mode='EDIT')
    eb_root = arm_data.edit_bones['Bone']
    eb_root.name = 'Root'
    eb_root.head = (0, 0, 0)
    eb_root.tail = (0, 0, 0.15)

    # Torso & Spine Chain
    create_bone(arm_data, 'Hips', 'Root', head=(0, 0, 0.26), tail=(0, 0, 0.36))
    create_bone(arm_data, 'Torso', 'Hips', head=(0, 0, 0.36), tail=(0, 0, 0.62))
    create_bone(arm_data, 'Chest', 'Torso', head=(0, 0, 0.46), tail=(0, 0, 0.62))
    create_bone(arm_data, 'Neck', 'Chest', head=(0, 0, 0.62), tail=(0, 0, 0.68))

    # Head & Mascot Antenna
    create_bone(arm_data, 'Head', 'Neck', head=(0, 0, 0.68), tail=(0, 0, 1.06))
    create_bone(arm_data, 'Antenna.L', 'Head', head=(0, -0.04, 1.06), tail=(0, -0.14, 1.25))
    create_bone(arm_data, 'Antenna.R', 'Head', head=(0, -0.04, 1.06), tail=(0, -0.14, 1.25))

    # Left Arm
    create_bone(arm_data, 'Shoulder.L', 'Chest', head=(-0.16, 0.0, 0.54), tail=(-0.21, 0.0, 0.54))
    create_bone(arm_data, 'Arm.L', 'Shoulder.L', head=(-0.21, 0.0, 0.54), tail=(-0.30, 0.02, 0.39))
    create_bone(arm_data, 'Hand.L', 'Arm.L', head=(-0.30, 0.02, 0.39), tail=(-0.37, 0.05, 0.22))
    create_bone(arm_data, 'Thumb.L', 'Hand.L', head=(-0.34, 0.04, 0.26), tail=(-0.36, 0.08, 0.22))
    create_bone(arm_data, 'Fingers.L', 'Hand.L', head=(-0.35, 0.03, 0.24), tail=(-0.39, 0.04, 0.18))

    # Right Arm
    create_bone(arm_data, 'Shoulder.R', 'Chest', head=(0.16, 0.0, 0.54), tail=(0.21, 0.0, 0.54))
    create_bone(arm_data, 'Arm.R', 'Shoulder.R', head=(0.21, 0.0, 0.54), tail=(0.30, 0.02, 0.39))
    create_bone(arm_data, 'Hand.R', 'Arm.R', head=(0.30, 0.02, 0.39), tail=(0.37, 0.05, 0.22))
    create_bone(arm_data, 'Thumb.R', 'Hand.R', head=(0.34, 0.04, 0.26), tail=(0.36, 0.08, 0.22))
    create_bone(arm_data, 'Fingers.R', 'Hand.R', head=(0.35, 0.03, 0.24), tail=(0.39, 0.04, 0.18))

    # Left Leg & Foot
    create_bone(arm_data, 'Leg.L', 'Hips', head=(-0.13, 0.0, 0.32), tail=(-0.13, 0.0, 0.16))
    create_bone(arm_data, 'Foot.L', 'Leg.L', head=(-0.13, 0.0, 0.16), tail=(-0.13, 0.12, 0.0))

    # Right Leg & Foot
    create_bone(arm_data, 'Leg.R', 'Hips', head=(0.13, 0.0, 0.32), tail=(0.13, 0.0, 0.16))
    create_bone(arm_data, 'Foot.R', 'Leg.R', head=(0.13, 0.0, 0.16), tail=(0.13, 0.12, 0.0))

    bpy.ops.object.mode_set(mode='OBJECT')

    mesh_parts = []

    # =========================================================================
    # A. HEAD GROUP (Manufactured Helmet + Flush Visor + Cyan Eyes + Ears + Sprout)
    # =========================================================================
    # 1. Main White Helmet Shell (Rounded squircle dome)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.85))
    m_helmet = bpy.context.active_object
    m_helmet.name = "Part_Helmet"
    m_helmet.scale = (0.47, 0.43, 0.38)
    bpy.ops.object.transform_apply(scale=True)
    apply_bevel_subsurf(m_helmet, bevel_width=0.16, bevel_segments=4, subsurf_levels=2)
    m_helmet.data.materials.append(mat_white)
    assign_vertex_group(m_helmet, "Head")
    mesh_parts.append(m_helmet)

    # 2. Flush Visor Screen (Integrated curved faceplate that fits seamlessly into helmet front)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0.12, 0.84))
    m_visor = bpy.context.active_object
    m_visor.name = "Part_Visor"
    m_visor.scale = (0.36, 0.20, 0.24)
    bpy.ops.object.transform_apply(scale=True)
    apply_bevel_subsurf(m_visor, bevel_width=0.08, bevel_segments=4, subsurf_levels=2)
    m_visor.data.materials.append(mat_visor)
    assign_vertex_group(m_visor, "Head")
    mesh_parts.append(m_visor)

    # 3. Cyan LED Eyes (Expressive tall capsule pills flush on visor)
    for side, x, rot in [("L", -0.09, 4.5), ("R", 0.09, -4.5)]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=0.034, depth=0.005, location=(x, 0.222, 0.845))
        eye = bpy.context.active_object
        eye.name = f"Part_Eye_{side}"
        eye.rotation_euler = (math.radians(90), math.radians(rot), 0)
        eye.scale = (0.76, 1.48, 1.0)
        bpy.ops.object.transform_apply(scale=True, rotation=True)
        bpy.ops.object.shade_smooth()
        eye.data.materials.append(mat_cyan_glow)
        assign_vertex_group(eye, "Head")
        mesh_parts.append(eye)

    # 4. Royal Blue Helmet Crown Cap (Arches over brow, covers top-back of head)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -0.06, 0.90))
    m_blue_cap = bpy.context.active_object
    m_blue_cap.name = "Part_HelmetBlueCap"
    m_blue_cap.scale = (0.49, 0.38, 0.28)
    bpy.ops.object.transform_apply(scale=True)
    apply_bevel_subsurf(m_blue_cap, bevel_width=0.15, bevel_segments=4, subsurf_levels=2)
    m_blue_cap.data.materials.append(mat_royal_blue)
    assign_vertex_group(m_blue_cap, "Head")
    mesh_parts.append(m_blue_cap)

    # 5. Ear Canister Modules (Outer Yellow Rim + Blue Middle + Cyan Donut + Navy Hub)
    for side, x, rot in [("L", -0.25, 90), ("R", 0.25, -90)]:
        # Outer Yellow Rim Disc with chamfer
        bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=0.082, depth=0.024, location=(x, 0, 0.84))
        ear_rim = bpy.context.active_object
        ear_rim.name = f"Part_EarRim_{side}"
        ear_rim.rotation_euler = (0, math.radians(rot), 0)
        bpy.ops.object.transform_apply(rotation=True)
        apply_bevel_subsurf(ear_rim, bevel_width=0.006, bevel_segments=2, subsurf_levels=0)
        ear_rim.data.materials.append(mat_golden_yellow)
        assign_vertex_group(ear_rim, "Head")
        mesh_parts.append(ear_rim)

        # Middle Royal Blue Housing Disc
        bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=0.070, depth=0.034, location=(x * 1.03, 0, 0.84))
        ear_mid = bpy.context.active_object
        ear_mid.name = f"Part_EarMid_{side}"
        ear_mid.rotation_euler = (0, math.radians(rot), 0)
        bpy.ops.object.transform_apply(rotation=True)
        bpy.ops.object.shade_smooth()
        ear_mid.data.materials.append(mat_royal_blue)
        assign_vertex_group(ear_mid, "Head")
        mesh_parts.append(ear_mid)

        # Glowing Cyan Concentric Donut Ring
        bpy.ops.mesh.primitive_torus_add(major_radius=0.046, minor_radius=0.010, major_segments=32, minor_segments=10, location=(x * 1.07, 0, 0.84))
        ear_ring = bpy.context.active_object
        ear_ring.name = f"Part_EarRing_{side}"
        ear_ring.rotation_euler = (0, math.radians(rot), 0)
        bpy.ops.object.transform_apply(rotation=True)
        ear_ring.data.materials.append(mat_cyan_glow)
        assign_vertex_group(ear_ring, "Head")
        mesh_parts.append(ear_ring)

        # Dark Navy Center Hub
        bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=0.026, depth=0.040, location=(x * 1.06, 0, 0.84))
        ear_hub = bpy.context.active_object
        ear_hub.name = f"Part_EarHub_{side}"
        ear_hub.rotation_euler = (0, math.radians(rot), 0)
        bpy.ops.object.transform_apply(rotation=True)
        ear_hub.data.materials.append(mat_dark_navy)
        assign_vertex_group(ear_hub, "Head")
        mesh_parts.append(ear_hub)

    # 6. Yellow Sprout Leaf Antenna (Mascot Feature)
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.015, depth=0.12, location=(0, -0.04, 1.09))
    sprout_stem = bpy.context.active_object
    sprout_stem.name = "Part_SproutStem"
    sprout_stem.rotation_euler = (math.radians(-26), 0, math.radians(10))
    bpy.ops.object.transform_apply(rotation=True)
    bpy.ops.object.shade_smooth()
    sprout_stem.data.materials.append(mat_golden_yellow)
    assign_vertex_group(sprout_stem, "Antenna.L")
    mesh_parts.append(sprout_stem)

    bpy.ops.mesh.primitive_uv_sphere_add(segments=20, ring_count=14, radius=0.075, location=(0.02, -0.11, 1.20))
    sprout_leaf = bpy.context.active_object
    sprout_leaf.name = "Part_SproutLeaf"
    sprout_leaf.scale = (0.50, 1.40, 0.42)
    sprout_leaf.rotation_euler = (math.radians(-40), 0, math.radians(12))
    bpy.ops.object.transform_apply(rotation=True, scale=True)
    bpy.ops.object.shade_smooth()
    sprout_leaf.data.materials.append(mat_golden_yellow)
    assign_vertex_group(sprout_leaf, "Antenna.L")
    mesh_parts.append(sprout_leaf)

    # =========================================================================
    # B. NECK & PUFFY YELLOW SCARF (Soft Folds + Emblem Bib + S-Curve Tails)
    # =========================================================================
    # 1. Scarf Neck Collar Wrap (Soft fleece cowl)
    bpy.ops.mesh.primitive_torus_add(major_radius=0.142, minor_radius=0.040, major_segments=32, minor_segments=12, location=(0, 0, 0.64))
    m_scarf_neck = bpy.context.active_object
    m_scarf_neck.name = "Part_ScarfCollar"
    m_scarf_neck.scale = (1.0, 0.94, 1.0)
    bpy.ops.object.transform_apply(scale=True)
    bpy.ops.object.shade_smooth()
    m_scarf_neck.data.materials.append(mat_golden_yellow)
    assign_vertex_group(m_scarf_neck, "Torso")
    mesh_parts.append(m_scarf_neck)

    # 2. Front Triangular Neckerchief Bib
    bpy.ops.mesh.primitive_cone_add(vertices=3, radius1=0.10, radius2=0.0, depth=0.10, location=(0, 0.146, 0.58))
    m_scarf_front = bpy.context.active_object
    m_scarf_front.name = "Part_ScarfFront"
    m_scarf_front.rotation_euler = (math.radians(155), 0, math.radians(180))
    m_scarf_front.scale = (1.15, 0.35, 1.0)
    bpy.ops.object.transform_apply(rotation=True, scale=True)
    apply_bevel_subsurf(m_scarf_front, bevel_width=0.012, bevel_segments=2, subsurf_levels=1)
    m_scarf_front.data.materials.append(mat_golden_yellow)
    assign_vertex_group(m_scarf_front, "Torso")
    mesh_parts.append(m_scarf_front)

    # Royal Blue Inlay Border on Bib
    bpy.ops.mesh.primitive_cone_add(vertices=3, radius1=0.054, radius2=0.0, depth=0.02, location=(0, 0.162, 0.58))
    m_scarf_emblem = bpy.context.active_object
    m_scarf_emblem.name = "Part_ScarfEmblem"
    m_scarf_emblem.rotation_euler = (math.radians(155), 0, math.radians(180))
    m_scarf_emblem.scale = (1.0, 0.3, 1.0)
    bpy.ops.object.transform_apply(rotation=True, scale=True)
    m_scarf_emblem.data.materials.append(mat_royal_blue)
    assign_vertex_group(m_scarf_emblem, "Torso")
    mesh_parts.append(m_scarf_emblem)

    # Glowing Cyan Core inside Bib
    bpy.ops.mesh.primitive_cylinder_add(vertices=3, radius=0.028, depth=0.015, location=(0, 0.168, 0.58))
    m_scarf_core = bpy.context.active_object
    m_scarf_core.name = "Part_ScarfCore"
    m_scarf_core.rotation_euler = (math.radians(115), 0, math.radians(180))
    bpy.ops.object.transform_apply(rotation=True)
    m_scarf_core.data.materials.append(mat_cyan_glow)
    assign_vertex_group(m_scarf_core, "Torso")
    mesh_parts.append(m_scarf_core)

    # 3. Dual S-Curve Fluttering Scarf Tails
    for side, x, rot_y in [("L", -0.13, -18), ("R", 0.13, 18)]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(x, -0.16, 0.57))
        tail = bpy.context.active_object
        tail.name = f"Part_ScarfTail_{side}"
        tail.scale = (0.05, 0.15, 0.022)
        tail.rotation_euler = (math.radians(-32), math.radians(rot_y), math.radians(rot_y * 0.5))
        bpy.ops.object.transform_apply(rotation=True, scale=True)
        apply_bevel_subsurf(tail, bevel_width=0.008, bevel_segments=2, subsurf_levels=1)
        tail.data.materials.append(mat_golden_yellow)
        assign_vertex_group(tail, "Torso")
        mesh_parts.append(tail)

    # =========================================================================
    # C. TORSO & BACKPACK (Beveled White Chassis + Chest Core + Blue Backpack)
    # =========================================================================
    # 1. Main Robotic Breastplate (Beveled, structured chassis)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.48))
    m_torso = bpy.context.active_object
    m_torso.name = "Part_Torso"
    m_torso.scale = (0.31, 0.24, 0.24)
    bpy.ops.object.transform_apply(scale=True)
    apply_bevel_subsurf(m_torso, bevel_width=0.05, bevel_segments=3, subsurf_levels=1)
    m_torso.data.materials.append(mat_white)
    assign_vertex_group(m_torso, "Torso")
    mesh_parts.append(m_torso)

    # 2. Glowing Cyan Triangular Chest Core in Blue Rim
    bpy.ops.mesh.primitive_cylinder_add(vertices=3, radius=0.052, depth=0.03, location=(0, 0.125, 0.50))
    m_chest_core = bpy.context.active_object
    m_chest_core.name = "Part_ChestCore"
    m_chest_core.rotation_euler = (math.radians(90), 0, math.radians(180))
    bpy.ops.object.transform_apply(rotation=True)
    m_chest_core.data.materials.append(mat_cyan_glow)
    assign_vertex_group(m_chest_core, "Torso")
    mesh_parts.append(m_chest_core)

    bpy.ops.mesh.primitive_cylinder_add(vertices=3, radius=0.068, depth=0.02, location=(0, 0.120, 0.50))
    m_chest_rim = bpy.context.active_object
    m_chest_rim.name = "Part_ChestRim"
    m_chest_rim.rotation_euler = (math.radians(90), 0, math.radians(180))
    bpy.ops.object.transform_apply(rotation=True)
    m_chest_rim.data.materials.append(mat_royal_blue)
    assign_vertex_group(m_chest_rim, "Torso")
    mesh_parts.append(m_chest_rim)

    # 3. Royal Blue Backpack Module with Glowing Triangle
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -0.14, 0.50))
    m_backpack = bpy.context.active_object
    m_backpack.name = "Part_Backpack"
    m_backpack.scale = (0.20, 0.08, 0.18)
    bpy.ops.object.transform_apply(scale=True)
    apply_bevel_subsurf(m_backpack, bevel_width=0.02, bevel_segments=2, subsurf_levels=1)
    m_backpack.data.materials.append(mat_royal_blue)
    assign_vertex_group(m_backpack, "Torso")
    mesh_parts.append(m_backpack)

    bpy.ops.mesh.primitive_cylinder_add(vertices=3, radius=0.048, depth=0.02, location=(0, -0.185, 0.50))
    m_back_core = bpy.context.active_object
    m_back_core.name = "Part_BackCore"
    m_back_core.rotation_euler = (math.radians(-90), 0, math.radians(180))
    bpy.ops.object.transform_apply(rotation=True)
    m_back_core.data.materials.append(mat_cyan_glow)
    assign_vertex_group(m_back_core, "Torso")
    mesh_parts.append(m_back_core)

    # 4. Dark Navy Pelvis Harness
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.36))
    m_pelvis = bpy.context.active_object
    m_pelvis.name = "Part_Pelvis"
    m_pelvis.scale = (0.24, 0.16, 0.08)
    bpy.ops.object.transform_apply(scale=True)
    apply_bevel_subsurf(m_pelvis, bevel_width=0.02, bevel_segments=2, subsurf_levels=1)
    m_pelvis.data.materials.append(mat_dark_navy)
    assign_vertex_group(m_pelvis, "Hips")
    mesh_parts.append(m_pelvis)

    # =========================================================================
    # D. ARTICULATED ARMS & MECH HANDS (Navy Ball Joints + White Sleeves + Blue Cuffs)
    # =========================================================================
    for side, x, s_mult in [("L", -0.19, 1), ("R", 0.19, -1)]:
        # Shoulder Pauldron Cap (White curved cap)
        bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=12, radius=0.065, location=(x * 1.05, 0.01, 0.54))
        sh_cap = bpy.context.active_object
        sh_cap.name = f"Part_ShoulderCap_{side}"
        sh_cap.scale = (0.85, 1.0, 0.75)
        bpy.ops.object.transform_apply(scale=True)
        bpy.ops.object.shade_smooth()
        sh_cap.data.materials.append(mat_white)
        assign_vertex_group(sh_cap, f"Arm.{side}")
        mesh_parts.append(sh_cap)

        # Compact Navy Shoulder Ball Joint
        bpy.ops.mesh.primitive_uv_sphere_add(segments=14, ring_count=10, radius=0.050, location=(x, 0.01, 0.52))
        shoulder = bpy.context.active_object
        shoulder.name = f"Part_Shoulder_{side}"
        shoulder.data.materials.append(mat_dark_navy)
        assign_vertex_group(shoulder, f"Arm.{side}")
        mesh_parts.append(shoulder)

        # White Upper Arm Cylinder
        bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.038, depth=0.13, location=(x * 1.20, 0.02, 0.44))
        u_arm = bpy.context.active_object
        u_arm.name = f"Part_UpperArm_{side}"
        u_arm.rotation_euler = (math.radians(10), math.radians(s_mult * 14), 0)
        bpy.ops.object.transform_apply(rotation=True)
        bpy.ops.object.shade_smooth()
        u_arm.data.materials.append(mat_white)
        assign_vertex_group(u_arm, f"Arm.{side}")
        mesh_parts.append(u_arm)

        # Elbow Joint (Dark Navy)
        bpy.ops.mesh.primitive_uv_sphere_add(segments=14, ring_count=10, radius=0.038, location=(x * 1.34, 0.03, 0.35))
        elbow = bpy.context.active_object
        elbow.name = f"Part_Elbow_{side}"
        elbow.data.materials.append(mat_dark_navy)
        assign_vertex_group(elbow, f"Arm.{side}")
        mesh_parts.append(elbow)

        # Forearm Sleeve
        bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.044, depth=0.12, location=(x * 1.48, 0.05, 0.28))
        f_arm = bpy.context.active_object
        f_arm.name = f"Part_Forearm_{side}"
        f_arm.rotation_euler = (math.radians(14), math.radians(s_mult * 10), 0)
        bpy.ops.object.transform_apply(rotation=True)
        bpy.ops.object.shade_smooth()
        f_arm.data.materials.append(mat_white)
        assign_vertex_group(f_arm, f"Hand.{side}")
        mesh_parts.append(f_arm)

        # Forearm Royal Blue Trim Cuff Ring
        bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.048, depth=0.03, location=(x * 1.46, 0.05, 0.31))
        arm_trim = bpy.context.active_object
        arm_trim.name = f"Part_ArmTrim_{side}"
        arm_trim.rotation_euler = (math.radians(14), math.radians(s_mult * 10), 0)
        bpy.ops.object.transform_apply(rotation=True)
        arm_trim.data.materials.append(mat_royal_blue)
        assign_vertex_group(arm_trim, f"Hand.{side}")
        mesh_parts.append(arm_trim)

        # Forearm Outer Cyan Decal Glyph
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(x * 1.54, 0.05, 0.28))
        arm_glyph = bpy.context.active_object
        arm_glyph.name = f"Part_ArmGlyph_{side}"
        arm_glyph.scale = (0.008, 0.024, 0.024)
        arm_glyph.rotation_euler = (math.radians(14), math.radians(s_mult * 10), 0)
        bpy.ops.object.transform_apply(rotation=True, scale=True)
        arm_glyph.data.materials.append(mat_cyan_glow)
        assign_vertex_group(arm_glyph, f"Hand.{side}")
        mesh_parts.append(arm_glyph)

        # Modeled Chibi Robot Hand with Palm, Thumb & Sculpted Fingers
        bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=12, radius=0.052, location=(x * 1.60, 0.07, 0.20))
        hand = bpy.context.active_object
        hand.name = f"Part_Hand_{side}"
        hand.scale = (0.85, 1.15, 1.0)
        bpy.ops.object.transform_apply(scale=True)
        bpy.ops.object.shade_smooth()
        hand.data.materials.append(mat_dark_navy)
        assign_vertex_group(hand, f"Hand.{side}")
        mesh_parts.append(hand)

        # Opposable Thumb
        bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.016, depth=0.038, location=(x * 1.55, 0.10, 0.21))
        thumb = bpy.context.active_object
        thumb.name = f"Part_Thumb_{side}"
        thumb.rotation_euler = (math.radians(45), math.radians(s_mult * 30), 0)
        bpy.ops.object.transform_apply(rotation=True)
        bpy.ops.object.shade_smooth()
        thumb.data.materials.append(mat_dark_navy)
        assign_vertex_group(thumb, f"Hand.{side}")
        mesh_parts.append(thumb)

        # Sculpted Fingers (cute curled chibi robotic grip)
        for f_idx, f_z in enumerate([0.22, 0.19, 0.16]):
            bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.014, depth=0.032, location=(x * 1.66, 0.08, f_z))
            finger = bpy.context.active_object
            finger.name = f"Part_Finger_{side}_{f_idx}"
            finger.rotation_euler = (math.radians(15), 0, math.radians(s_mult * 20))
            bpy.ops.object.transform_apply(rotation=True)
            bpy.ops.object.shade_smooth()
            finger.data.materials.append(mat_dark_navy)
            assign_vertex_group(finger, f"Hand.{side}")
            mesh_parts.append(finger)

        # Protective White Backplate on Hand
        bpy.ops.mesh.primitive_cylinder_add(vertices=14, radius=0.032, depth=0.015, location=(x * 1.63, 0.04, 0.21))
        hand_plate = bpy.context.active_object
        hand_plate.name = f"Part_HandPlate_{side}"
        hand_plate.rotation_euler = (0, math.radians(90), 0)
        bpy.ops.object.transform_apply(rotation=True)
        hand_plate.data.materials.append(mat_white)
        assign_vertex_group(hand_plate, f"Hand.{side}")
        mesh_parts.append(hand_plate)

    # =========================================================================
    # E. LEGS & ICONIC BOOTS (Yellow Toe Cap + Blue Heel/Sole + Cyan Ankle Dot)
    # =========================================================================
    for side, x in [("L", -0.13), ("R", 0.13)]:
        # Inset Hip Ball Joint (Dark Navy)
        bpy.ops.mesh.primitive_uv_sphere_add(segments=14, ring_count=10, radius=0.050, location=(x, 0, 0.32))
        hip = bpy.context.active_object
        hip.name = f"Part_Hip_{side}"
        hip.data.materials.append(mat_dark_navy)
        assign_vertex_group(hip, f"Leg.{side}")
        mesh_parts.append(hip)

        # Thigh Armor Shell (White ceramic)
        bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.044, depth=0.12, location=(x, 0, 0.24))
        thigh = bpy.context.active_object
        thigh.name = f"Part_Thigh_{side}"
        bpy.ops.object.shade_smooth()
        thigh.data.materials.append(mat_white)
        assign_vertex_group(thigh, f"Leg.{side}")
        mesh_parts.append(thigh)

        # Knee Joint (Dark Navy)
        bpy.ops.mesh.primitive_uv_sphere_add(segments=14, ring_count=10, radius=0.042, location=(x, 0.01, 0.17))
        knee = bpy.context.active_object
        knee.name = f"Part_Knee_{side}"
        knee.data.materials.append(mat_dark_navy)
        assign_vertex_group(knee, f"Leg.{side}")
        mesh_parts.append(knee)

        # Sculpted Shin Boot Cuff (White)
        bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.047, depth=0.10, location=(x, 0.01, 0.11))
        shin = bpy.context.active_object
        shin.name = f"Part_Shin_{side}"
        bpy.ops.object.shade_smooth()
        shin.data.materials.append(mat_white)
        assign_vertex_group(shin, f"Foot.{side}")
        mesh_parts.append(shin)

        # Front Half: Golden Yellow Rounded Bulbous Toe Cap
        bpy.ops.mesh.primitive_uv_sphere_add(segments=18, ring_count=14, radius=0.080, location=(x, 0.055, 0.065))
        toe_cap = bpy.context.active_object
        toe_cap.name = f"Part_ToeCap_{side}"
        toe_cap.scale = (0.95, 1.15, 0.75)
        bpy.ops.object.transform_apply(scale=True)
        bpy.ops.object.shade_smooth()
        toe_cap.data.materials.append(mat_golden_yellow)
        assign_vertex_group(toe_cap, f"Foot.{side}")
        mesh_parts.append(toe_cap)

        # Rear Half: Royal Blue Heel and Sole Wrap
        bpy.ops.mesh.primitive_cylinder_add(vertices=20, radius=0.076, depth=0.045, location=(x, -0.03, 0.025))
        heel_sole = bpy.context.active_object
        heel_sole.name = f"Part_HeelSole_{side}"
        heel_sole.scale = (1.0, 1.35, 1.0)
        bpy.ops.object.transform_apply(scale=True)
        heel_sole.data.materials.append(mat_royal_blue)
        assign_vertex_group(heel_sole, f"Foot.{side}")
        mesh_parts.append(heel_sole)

        # Glowing Cyan Circular Dot on Outer Ankle
        sign_x = -1 if side == "L" else 1
        bpy.ops.mesh.primitive_cylinder_add(vertices=14, radius=0.018, depth=0.012, location=(x + sign_x * 0.076, 0.01, 0.065))
        ankle_dot = bpy.context.active_object
        ankle_dot.name = f"Part_AnkleDot_{side}"
        ankle_dot.rotation_euler = (0, math.radians(sign_x * 90), 0)
        bpy.ops.object.transform_apply(rotation=True)
        ankle_dot.data.materials.append(mat_cyan_glow)
        assign_vertex_group(ankle_dot, f"Foot.{side}")
        mesh_parts.append(ankle_dot)

    # 4. Join all parts into unified skinned mesh BOT_Character
    bpy.ops.object.select_all(action='DESELECT')
    for p in mesh_parts:
        p.select_set(True)
    bpy.context.view_layer.objects.active = mesh_parts[0]
    bpy.ops.object.join()
    char_mesh = bpy.context.active_object
    char_mesh.name = "BOT_Character"

    # Parent mesh to armature with Armature modifier
    char_mesh.parent = arm_obj
    arm_mod = char_mesh.modifiers.new(name="Armature", type='ARMATURE')
    arm_mod.object = arm_obj

    # 5. Author Keyframed Actions
    bpy.context.view_layer.objects.active = arm_obj
    bpy.ops.object.mode_set(mode='POSE')
    pose_bones = arm_obj.pose.bones

    def clear_pose():
        for pb in pose_bones:
            pb.location = (0, 0, 0)
            pb.rotation_euler = (0, 0, 0)
            pb.scale = (1, 1, 1)

    def rot_k(pb_name, rot_deg, frame):
        if pb_name in pose_bones:
            pb = pose_bones[pb_name]
            pb.rotation_mode = 'XYZ'
            pb.rotation_euler = (math.radians(rot_deg[0]), math.radians(rot_deg[1]), math.radians(rot_deg[2]))
            pb.keyframe_insert(data_path="rotation_euler", frame=frame)

    def loc_k(pb_name, loc, frame):
        if pb_name in pose_bones:
            pb = pose_bones[pb_name]
            pb.location = loc
            pb.keyframe_insert(data_path="location", frame=frame)

    def new_action(action_name):
        action = bpy.data.actions.new(name=action_name)
        action.use_fake_user = True
        arm_obj.animation_data_create()
        arm_obj.animation_data.action = action
        clear_pose()
        return action

    # 1. Idle (Breathing cycle, head swivel, bouncing sprout antenna, scarf sway)
    new_action("Idle")
    for f in [1, 60]:
        loc_k("Torso", (0, 0, 0), f)
        rot_k("Torso", (0, 0, 0), f)
        rot_k("Head", (0, 0, 0), f)
        rot_k("Antenna.L", (0, 0, 0), f)
        rot_k("Arm.L", (0, 0, 5), f)
        rot_k("Arm.R", (0, 0, -5), f)
    loc_k("Torso", (0, 0, 0.018), 30)
    rot_k("Torso", (-1.5, 0, 0.5), 30)
    rot_k("Head", (2.0, 0, -1.0), 30)
    rot_k("Antenna.L", (-8.0, 0, 4.0), 30)
    rot_k("Arm.L", (3, 0, 9), 30)
    rot_k("Arm.R", (3, 0, -9), 30)

    # 2. Idle_Secondary
    new_action("Idle_Secondary")
    for f in [1, 75]:
        loc_k("Torso", (0, 0, 0), f)
        rot_k("Head", (0, 0, 0), f)
        rot_k("Antenna.L", (0, 0, 0), f)
    rot_k("Head", (5.0, 16.0, 4.0), 25)
    rot_k("Antenna.L", (-12.0, 0, 14.0), 25)
    rot_k("Foot.R", (-15.0, 0, 0), 25)
    rot_k("Head", (-4.0, -14.0, -3.0), 50)
    rot_k("Antenna.L", (6.0, 0, -12.0), 50)
    rot_k("Foot.R", (0.0, 0, 0), 50)

    # 3. Walk
    new_action("Walk")
    frames = [1, 8, 16, 24, 32]
    for idx, f in enumerate(frames):
        p = idx / 4.0
        wave = math.sin(p * math.pi * 2)
        c_wave = math.cos(p * math.pi * 2)
        loc_k("Torso", (0, 0, abs(c_wave) * 0.025), f)
        rot_k("Torso", (c_wave * 2.0, 0, -wave * 4.0), f)
        rot_k("Head", (-c_wave * 2.0, 0, wave * 2.0), f)
        rot_k("Antenna.L", (-wave * 12.0, 0, 0), f)
        rot_k("Leg.L", (wave * 28.0, 0, 0), f)
        rot_k("Foot.L", (-wave * 14.0, 0, 0), f)
        rot_k("Leg.R", (-wave * 28.0, 0, 0), f)
        rot_k("Foot.R", (wave * 14.0, 0, 0), f)
        rot_k("Arm.L", (-wave * 30.0, 0, 8.0), f)
        rot_k("Arm.R", (wave * 30.0, 0, -8.0), f)

    # 4. Run
    new_action("Run")
    r_frames = [1, 6, 12, 18, 24]
    for idx, f in enumerate(r_frames):
        p = idx / 4.0
        wave = math.sin(p * math.pi * 2)
        c_wave = math.cos(p * math.pi * 2)
        loc_k("Torso", (0, 0, abs(c_wave) * 0.038), f)
        rot_k("Torso", (14.0 + c_wave * 3.0, 0, -wave * 6.0), f)
        rot_k("Head", (-10.0, 0, wave * 3.0), f)
        rot_k("Antenna.L", (-26.0 - wave * 8.0, 0, 0), f)
        rot_k("Leg.L", (wave * 44.0, 0, 0), f)
        rot_k("Foot.L", (-wave * 22.0, 0, 0), f)
        rot_k("Leg.R", (-wave * 44.0, 0, 0), f)
        rot_k("Foot.R", (wave * 22.0, 0, 0), f)
        rot_k("Arm.L", (-wave * 52.0, 0, 12.0), f)
        rot_k("Arm.R", (wave * 52.0, 0, -12.0), f)

    # 5. Jump_Start
    new_action("Jump_Start")
    for f in [1, 15]:
        loc_k("Torso", (0, 0, 0), f)
        rot_k("Torso", (0, 0, 0), f)
        rot_k("Leg.L", (0, 0, 0), f)
        rot_k("Leg.R", (0, 0, 0), f)
    loc_k("Torso", (0, 0, -0.06), 6)
    rot_k("Torso", (10.0, 0, 0), 6)
    rot_k("Leg.L", (-25.0, 0, 0), 6)
    rot_k("Leg.R", (-25.0, 0, 0), 6)
    rot_k("Arm.L", (-25.0, 0, 15.0), 6)
    rot_k("Arm.R", (-25.0, 0, -15.0), 6)
    loc_k("Torso", (0, 0, 0.08), 12)
    rot_k("Torso", (-8.0, 0, 0), 12)
    rot_k("Leg.L", (18.0, 0, 0), 12)
    rot_k("Leg.R", (18.0, 0, 0), 12)
    rot_k("Antenna.L", (-25.0, 0, 0), 12)

    # 6. Jump_Loop
    new_action("Jump_Loop")
    for f in [1, 20]:
        loc_k("Torso", (0, 0, 0.06), f)
        rot_k("Torso", (-6.0, 0, 0), f)
        rot_k("Antenna.L", (-22.0, 0, 0), f)
        rot_k("Leg.L", (14.0, 0, 0), f)
        rot_k("Leg.R", (18.0, 0, 0), f)
        rot_k("Arm.L", (35.0, 0, 24.0), f)
        rot_k("Arm.R", (35.0, 0, -24.0), f)
    loc_k("Torso", (0, 0, 0.08), 10)
    rot_k("Antenna.L", (-28.0, 0, 0), 10)

    # 7. Fall
    new_action("Fall")
    for f in [1, 20]:
        loc_k("Torso", (0, 0, 0), f)
        rot_k("Torso", (12.0, 0, 0), f)
        rot_k("Antenna.L", (18.0, 0, 0), f)
        rot_k("Leg.L", (-16.0, 0, 0), f)
        rot_k("Leg.R", (-12.0, 0, 0), f)
        rot_k("Arm.L", (-20.0, 0, 32.0), f)
        rot_k("Arm.R", (-20.0, 0, -32.0), f)
    rot_k("Antenna.L", (24.0, 0, 0), 10)

    # 8. Landing
    new_action("Landing")
    for f in [1, 16]:
        loc_k("Torso", (0, 0, 0), f)
        rot_k("Torso", (0, 0, 0), f)
        rot_k("Leg.L", (0, 0, 0), f)
        rot_k("Leg.R", (0, 0, 0), f)
    loc_k("Torso", (0, 0, -0.07), 4)
    rot_k("Torso", (12.0, 0, 0), 4)
    rot_k("Leg.L", (-30.0, 0, 0), 4)
    rot_k("Leg.R", (-30.0, 0, 0), 4)
    rot_k("Antenna.L", (20.0, 0, 0), 4)
    rot_k("Arm.L", (-15.0, 0, 20.0), 4)
    rot_k("Arm.R", (-15.0, 0, -20.0), 4)

    # 9. Turn_Left
    new_action("Turn_Left")
    for f in [1, 12]:
        rot_k("Torso", (0, 0, 0), f)
    rot_k("Torso", (0, 22.0, 10.0), 6)
    rot_k("Antenna.L", (0, 0, -20.0), 6)

    # 10. Turn_Right
    new_action("Turn_Right")
    for f in [1, 12]:
        rot_k("Torso", (0, 0, 0), f)
    rot_k("Torso", (0, -22.0, -10.0), 6)
    rot_k("Antenna.L", (0, 0, 20.0), 6)

    # 11. Collect
    new_action("Collect")
    for f in [1, 30]:
        loc_k("Torso", (0, 0, 0), f)
        rot_k("Torso", (0, 0, 0), f)
        rot_k("Arm.R", (0, 0, 0), f)
    loc_k("Torso", (0, 0, 0.08), 8)
    rot_k("Arm.R", (95.0, 0, -15.0), 8)
    rot_k("Arm.L", (20.0, 0, 20.0), 8)
    rot_k("Antenna.L", (-20.0, 0, 0), 8)
    loc_k("Torso", (0, 0, 0), 16)
    loc_k("Torso", (0, 0, 0.10), 22)
    rot_k("Arm.R", (110.0, 0, -10.0), 22)
    rot_k("Head", (15.0, 0, 0), 22)

    # 12. Interact
    new_action("Interact")
    for f in [1, 26]:
        loc_k("Torso", (0, 0, 0), f)
        rot_k("Torso", (0, 0, 0), f)
        rot_k("Arm.R", (0, 0, 0), f)
    loc_k("Torso", (0, 0.05, 0), 10)
    rot_k("Torso", (8.0, -10.0, 0), 10)
    rot_k("Arm.R", (85.0, -20.0, -15.0), 10)
    rot_k("Hand.R", (20.0, 0, 0), 10)
    rot_k("Head", (-8.0, 10.0, 0), 10)

    # 13. Victory
    new_action("Victory")
    v_frames = [1, 15, 30, 45, 60]
    for idx, f in enumerate(v_frames):
        p = idx / 4.0
        loc_k("Torso", (0, 0, math.sin(p * math.pi * 2) * 0.08), f)
        rot_k("Torso", (0, p * 360.0, 0), f)
        rot_k("Arm.L", (100.0 + math.sin(p * math.pi * 4) * 20.0, 0, 25.0), f)
        rot_k("Arm.R", (100.0 - math.sin(p * math.pi * 4) * 20.0, 0, -25.0), f)
        rot_k("Antenna.L", (-20.0, 0, math.sin(p * math.pi * 4) * 20.0), f)
        rot_k("Head", (10.0, 0, 0), f)

    # 14. Respawn
    new_action("Respawn")
    for f in [1, 30]:
        loc_k("Torso", (0, 0, 0), f)
        rot_k("Torso", (0, 0, 0), f)
        rot_k("Head", (0, 0, 0), f)
    loc_k("Torso", (0, 0, -0.15), 1)
    rot_k("Torso", (25.0, 0, 0), 1)
    rot_k("Head", (-30.0, 0, 0), 1)
    loc_k("Torso", (0, 0, 0.05), 18)
    rot_k("Head", (15.0, 0, 0), 18)

    bpy.ops.object.mode_set(mode='OBJECT')

    # Set active action to Idle
    arm_obj.animation_data.action = bpy.data.actions["Idle"]

    # 6. Save Editable Blender Files in all requested paths
    source_dirs = [
        os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../assets/models/character")),
        os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../assets/models/source")),
        os.path.abspath(os.path.join(os.path.dirname(__file__), "../source"))
    ]
    for s_dir in source_dirs:
        os.makedirs(s_dir, exist_ok=True)
        blend_path = os.path.join(s_dir, "bot.blend")
        bpy.ops.wm.save_as_mainfile(filepath=blend_path)
        print(f"✓ Saved Blender source to: {blend_path}")

    # Backward compatibility alias
    alt_blend = os.path.join(source_dirs[2], "bot_character.blend")
    bpy.ops.wm.save_as_mainfile(filepath=alt_blend)
    print(f"✓ Saved Blender source alias to: {alt_blend}")

    # 7. Export GLB with Armature, Skinning, and Actions
    target_glb_dirs = [
        os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../assets/models/character")),
        os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../assets/models/characters")),
        os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../assets/models"))
    ]
    for g_dir in target_glb_dirs:
        os.makedirs(g_dir, exist_ok=True)
        glb_path = os.path.join(g_dir, "bot.glb")
        bpy.ops.export_scene.gltf(
            filepath=glb_path,
            export_format='GLB',
            use_selection=False,
            export_animations=True,
            export_animation_mode='ACTIONS',
            export_anim_single_armature=True,
            export_optimize_animation_size=True,
            export_skins=True
        )
        print(f"✓ Exported refined B.O.T GLB to: {glb_path}")

    print("B.O.T Refined Master-Class Production complete!")

if __name__ == "__main__":
    build_refined_bot()
