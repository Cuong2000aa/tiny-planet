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
            if "Emission Color" in bsdf.inputs:
                bsdf.inputs["Emission Color"].default_value = emission
                bsdf.inputs["Emission Strength"].default_value = emission_strength
            elif "Emission" in bsdf.inputs:
                bsdf.inputs["Emission"].default_value = emission
                bsdf.inputs["Emission Strength"].default_value = emission_strength
    return mat

def create_bone(arm_data, name, parent_name=None, head=(0,0,0), tail=(0,0,1)):
    eb = arm_data.edit_bones.new(name)
    eb.head = head
    eb.tail = tail
    if parent_name and parent_name in arm_data.edit_bones:
        eb.parent = arm_data.edit_bones[parent_name]
    return eb

def assign_vertex_group(obj, vg_name):
    vg = obj.vertex_groups.new(name=vg_name)
    v_indices = list(range(len(obj.data.vertices)))
    vg.add(v_indices, 1.0, 'REPLACE')

def keyframe_bone(pose_bone, frame, loc=None, rot_deg=None, scale=None):
    if loc is not None:
        pose_bone.location = loc
        pose_bone.keyframe_insert(data_path="location", frame=frame)
    if rot_deg is not None:
        pose_bone.rotation_mode = 'XYZ'
        pose_bone.rotation_euler = (math.radians(rot_deg[0]), math.radians(rot_deg[1]), math.radians(rot_deg[2]))
        pose_bone.keyframe_insert(data_path="rotation_euler", frame=frame)
    if scale is not None:
        pose_bone.scale = scale
        pose_bone.keyframe_insert(data_path="scale", frame=frame)

def build_model_sheet_bot():
    clean_scene()
    script_dir = os.path.dirname(os.path.abspath(__file__))
    source_dir = os.path.join(script_dir, "..", "source")
    char_model_dir = os.path.join(script_dir, "..", "..", "models", "characters")
    root_model_dir = os.path.join(script_dir, "..", "..", "models")
    os.makedirs(source_dir, exist_ok=True)
    os.makedirs(char_model_dir, exist_ok=True)

    # 1. PBR Materials from Official Character Model Sheet Palette
    # Primary: Ivory Warm White Porcelain Ceramic
    mat_white = create_pbr_material("Mat_Bot_WhiteCeramic", (0.96, 0.96, 0.98, 1.0), metallic=0.06, roughness=0.20)
    # Secondary: Rich Royal Blue
    mat_royal_blue = create_pbr_material("Mat_Bot_RoyalBlue", (0.10, 0.32, 0.88, 1.0), metallic=0.30, roughness=0.24)
    # Accent: Bright Golden Yellow (Scarf, Sprout, Toe Caps, Ear Rims)
    mat_yellow = create_pbr_material("Mat_Bot_BrightYellow", (0.98, 0.74, 0.08, 1.0), metallic=0.12, roughness=0.28)
    # Dark Details: Deep Navy / Graphite for Ball Joints & Hands
    mat_navy = create_pbr_material("Mat_Bot_DeepNavy", (0.08, 0.10, 0.16, 1.0), metallic=0.65, roughness=0.32)
    # Deep Glossy Obsidian Visor
    mat_visor = create_pbr_material("Mat_Bot_GlossVisor", (0.02, 0.03, 0.05, 1.0), metallic=0.92, roughness=0.08)
    # Luminous Glowing Cyan for LED Eyes, Concentric Ear Rings, & Triangle Energy Cores
    mat_cyan_glow = create_pbr_material("Mat_Bot_CyanGlow", (0.0, 0.95, 1.0, 1.0), metallic=0.0, roughness=0.15, emission=(0.0, 0.95, 1.0, 1.0), emission_strength=4.5)

    # 2. Armature Setup (13 Deformation Bones)
    bpy.ops.object.armature_add(enter_editmode=True, align='WORLD', location=(0, 0, 0))
    arm_obj = bpy.context.active_object
    arm_obj.name = "BOT_Armature"
    arm_data = arm_obj.data
    arm_data.name = "BOT_ArmatureData"

    eb_root = arm_data.edit_bones['Bone']
    eb_root.name = 'Root'
    eb_root.head = (0, 0, 0)
    eb_root.tail = (0, 0, 0.15)

    # Torso (Chassis & Scarf anchor)
    create_bone(arm_data, 'Torso', 'Root', head=(0, 0, 0.34), tail=(0, 0, 0.66))
    # Head (Rounded helmet & visor)
    create_bone(arm_data, 'Head', 'Torso', head=(0, 0, 0.66), tail=(0, 0, 1.05))
    # Yellow Sprout Leaf Antenna on head crown
    create_bone(arm_data, 'Antenna.L', 'Head', head=(0, -0.04, 1.05), tail=(0, -0.12, 1.25))
    create_bone(arm_data, 'Antenna.R', 'Head', head=(0, -0.04, 1.05), tail=(0, -0.12, 1.25))

    # Articulated Arms & Hands
    create_bone(arm_data, 'Arm.L', 'Torso', head=(-0.20, 0.0, 0.54), tail=(-0.31, 0.02, 0.40))
    create_bone(arm_data, 'Hand.L', 'Arm.L', head=(-0.31, 0.02, 0.40), tail=(-0.38, 0.05, 0.22))

    create_bone(arm_data, 'Arm.R', 'Torso', head=(0.20, 0.0, 0.54), tail=(0.31, 0.02, 0.40))
    create_bone(arm_data, 'Hand.R', 'Arm.R', head=(0.31, 0.02, 0.40), tail=(0.38, 0.05, 0.22))

    # Articulated Legs & Boots
    create_bone(arm_data, 'Leg.L', 'Root', head=(-0.13, 0.0, 0.34), tail=(-0.13, 0.0, 0.16))
    create_bone(arm_data, 'Foot.L', 'Leg.L', head=(-0.13, 0.0, 0.16), tail=(-0.13, 0.14, 0.0))

    create_bone(arm_data, 'Leg.R', 'Root', head=(0.13, 0.0, 0.34), tail=(0.13, 0.0, 0.16))
    create_bone(arm_data, 'Foot.R', 'Leg.R', head=(0.13, 0.0, 0.16), tail=(0.13, 0.14, 0.0))

    bpy.ops.object.mode_set(mode='OBJECT')

    mesh_parts = []

    # =========================================================================
    # A. HEAD GROUP (Rounded White Helmet + Blue Crown + Visor + LED Eyes + Ear Discs + Sprout)
    # =========================================================================
    # 1. Main White Helmet Dome
    bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=24, radius=0.235, location=(0, 0, 0.85))
    m_helmet = bpy.context.active_object
    m_helmet.name = "Part_Helmet"
    m_helmet.scale = (1.02, 0.96, 0.94)
    bpy.ops.object.transform_apply(scale=True)
    bpy.ops.object.shade_smooth()
    m_helmet.data.materials.append(mat_white)
    assign_vertex_group(m_helmet, "Head")
    mesh_parts.append(m_helmet)

    # 2. Royal Blue Helmet Crown Cap (Arching over top and visor brow)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=20, radius=0.24, location=(0, 0.01, 0.88))
    m_blue_cap = bpy.context.active_object
    m_blue_cap.name = "Part_HelmetBlueCap"
    m_blue_cap.scale = (0.95, 0.88, 0.75)
    bpy.ops.object.transform_apply(scale=True)
    bpy.ops.object.shade_smooth()
    m_blue_cap.data.materials.append(mat_royal_blue)
    assign_vertex_group(m_blue_cap, "Head")
    mesh_parts.append(m_blue_cap)

    # 3. Glossy Dark Visor Screen (Inset curved front face)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=28, ring_count=20, radius=0.18, location=(0, 0.12, 0.84))
    m_visor = bpy.context.active_object
    m_visor.name = "Part_Visor"
    m_visor.scale = (1.08, 0.44, 0.72)
    bpy.ops.object.transform_apply(scale=True)
    bpy.ops.object.shade_smooth()
    m_visor.data.materials.append(mat_visor)
    assign_vertex_group(m_visor, "Head")
    mesh_parts.append(m_visor)

    # 4. Bright Cyan LED Eyes (Large expressive capsule pills)
    for side, x, rot in [("L", -0.088, -3), ("R", 0.088, 3)]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.038, depth=0.025, location=(x, 0.205, 0.84))
        eye = bpy.context.active_object
        eye.name = f"Part_Eye_{side}"
        eye.rotation_euler = (math.radians(90), 0, math.radians(rot))
        eye.scale = (0.85, 1.0, 1.35)
        bpy.ops.object.transform_apply(rotation=True, scale=True)
        bpy.ops.object.shade_smooth()
        eye.data.materials.append(mat_cyan_glow)
        assign_vertex_group(eye, "Head")
        mesh_parts.append(eye)

    # 5. Ear Canister Modules (Left and Right: Yellow Outer Rim + Blue Middle + Glowing Cyan Concentric Ring)
    for side, x, rot in [("L", -0.235, 90), ("R", 0.235, -90)]:
        # Outer Yellow Rim Disc
        bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=0.075, depth=0.025, location=(x, 0, 0.84))
        ear_rim = bpy.context.active_object
        ear_rim.name = f"Part_EarRim_{side}"
        ear_rim.rotation_euler = (0, math.radians(rot), 0)
        bpy.ops.object.transform_apply(rotation=True)
        bpy.ops.object.shade_smooth()
        ear_rim.data.materials.append(mat_yellow)
        assign_vertex_group(ear_rim, "Head")
        mesh_parts.append(ear_rim)

        # Middle Royal Blue Housing Disc
        bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=0.065, depth=0.032, location=(x * 1.04, 0, 0.84))
        ear_mid = bpy.context.active_object
        ear_mid.name = f"Part_EarMid_{side}"
        ear_mid.rotation_euler = (0, math.radians(rot), 0)
        bpy.ops.object.transform_apply(rotation=True)
        bpy.ops.object.shade_smooth()
        ear_mid.data.materials.append(mat_royal_blue)
        assign_vertex_group(ear_mid, "Head")
        mesh_parts.append(ear_mid)

        # Glowing Cyan Concentric Donut Ring (Model Sheet Detail Feature)
        bpy.ops.mesh.primitive_torus_add(major_radius=0.040, minor_radius=0.010, major_segments=24, minor_segments=8, location=(x * 1.09, 0, 0.84))
        ear_ring = bpy.context.active_object
        ear_ring.name = f"Part_EarRing_{side}"
        ear_ring.rotation_euler = (0, math.radians(rot), 0)
        bpy.ops.object.transform_apply(rotation=True)
        ear_ring.data.materials.append(mat_cyan_glow)
        assign_vertex_group(ear_ring, "Head")
        mesh_parts.append(ear_ring)

        # Dark Navy Center Hub
        bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.025, depth=0.035, location=(x * 1.08, 0, 0.84))
        ear_hub = bpy.context.active_object
        ear_hub.name = f"Part_EarHub_{side}"
        ear_hub.rotation_euler = (0, math.radians(rot), 0)
        bpy.ops.object.transform_apply(rotation=True)
        ear_hub.data.materials.append(mat_navy)
        assign_vertex_group(ear_hub, "Head")
        mesh_parts.append(ear_hub)

    # 6. Yellow Sprout Leaf Antenna (Top Crown Mascot Feature)
    # Curved stem
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.014, depth=0.10, location=(0, -0.03, 1.09))
    sprout_stem = bpy.context.active_object
    sprout_stem.name = "Part_SproutStem"
    sprout_stem.rotation_euler = (math.radians(-22), 0, 0)
    bpy.ops.object.transform_apply(rotation=True)
    bpy.ops.object.shade_smooth()
    sprout_stem.data.materials.append(mat_yellow)
    assign_vertex_group(sprout_stem, "Antenna.L")
    mesh_parts.append(sprout_stem)

    # Sprout Leaf / Teardrop Fin
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=12, radius=0.065, location=(0, -0.08, 1.18))
    sprout_leaf = bpy.context.active_object
    sprout_leaf.name = "Part_SproutLeaf"
    sprout_leaf.scale = (0.42, 1.25, 0.45)
    sprout_leaf.rotation_euler = (math.radians(-38), 0, 0)
    bpy.ops.object.transform_apply(rotation=True, scale=True)
    bpy.ops.object.shade_smooth()
    sprout_leaf.data.materials.append(mat_yellow)
    assign_vertex_group(sprout_leaf, "Antenna.L")
    mesh_parts.append(sprout_leaf)

    # =========================================================================
    # B. NECK & BRIGHT YELLOW SCARF (Iconic Visual Identity Element)
    # =========================================================================
    # 1. Scarf Neck Collar Wrap
    bpy.ops.mesh.primitive_torus_add(major_radius=0.14, minor_radius=0.035, major_segments=24, minor_segments=8, location=(0, 0, 0.65))
    m_scarf_neck = bpy.context.active_object
    m_scarf_neck.name = "Part_ScarfCollar"
    m_scarf_neck.scale = (1.0, 0.92, 1.0)
    bpy.ops.object.transform_apply(scale=True)
    m_scarf_neck.data.materials.append(mat_yellow)
    assign_vertex_group(m_scarf_neck, "Torso")
    mesh_parts.append(m_scarf_neck)

    # 2. Front Triangular Neckerchief Point (Pointing down over chest)
    bpy.ops.mesh.primitive_cone_add(vertices=3, radius1=0.09, radius2=0.0, depth=0.10, location=(0, 0.155, 0.60))
    m_scarf_front = bpy.context.active_object
    m_scarf_front.name = "Part_ScarfFront"
    m_scarf_front.rotation_euler = (math.radians(160), 0, math.radians(180))
    m_scarf_front.scale = (1.2, 0.35, 1.0)
    bpy.ops.object.transform_apply(rotation=True, scale=True)
    bpy.ops.object.shade_smooth()
    m_scarf_front.data.materials.append(mat_yellow)
    assign_vertex_group(m_scarf_front, "Torso")
    mesh_parts.append(m_scarf_front)

    # Front Blue Inlay Emblem on Scarf
    bpy.ops.mesh.primitive_cone_add(vertices=3, radius1=0.045, radius2=0.0, depth=0.02, location=(0, 0.165, 0.61))
    m_scarf_emblem = bpy.context.active_object
    m_scarf_emblem.name = "Part_ScarfEmblem"
    m_scarf_emblem.rotation_euler = (math.radians(160), 0, math.radians(180))
    m_scarf_emblem.scale = (1.1, 0.3, 1.0)
    bpy.ops.object.transform_apply(rotation=True, scale=True)
    m_scarf_emblem.data.materials.append(mat_royal_blue)
    assign_vertex_group(m_scarf_emblem, "Torso")
    mesh_parts.append(m_scarf_emblem)

    # 3. Dual Flying Scarf Tails (Fluttering over shoulders)
    for side, x, rot_y in [("L", -0.13, -18), ("R", 0.13, 18)]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(x, -0.16, 0.58))
        tail = bpy.context.active_object
        tail.name = f"Part_ScarfTail_{side}"
        tail.scale = (0.05, 0.14, 0.02)
        tail.rotation_euler = (math.radians(-32), math.radians(rot_y), math.radians(rot_y * 0.5))
        bpy.ops.object.transform_apply(rotation=True, scale=True)
        bpy.ops.object.shade_smooth()
        tail.data.materials.append(mat_yellow)
        assign_vertex_group(tail, "Torso")
        mesh_parts.append(tail)

    # =========================================================================
    # C. TORSO & BACKPACK (White Armor + Chest Cyan Core + Blue Backpack)
    # =========================================================================
    # 1. Main Torso (Compact sturdy chassis)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=16, radius=0.18, location=(0, 0, 0.48))
    m_torso = bpy.context.active_object
    m_torso.name = "Part_Torso"
    m_torso.scale = (0.95, 0.82, 0.95)
    bpy.ops.object.transform_apply(scale=True)
    bpy.ops.object.shade_smooth()
    m_torso.data.materials.append(mat_white)
    assign_vertex_group(m_torso, "Torso")
    mesh_parts.append(m_torso)

    # 2. Glowing Cyan Chest Core (Downward-pointing Triangle / Chevron)
    bpy.ops.mesh.primitive_cylinder_add(vertices=3, radius=0.055, depth=0.03, location=(0, 0.14, 0.51))
    m_chest_core = bpy.context.active_object
    m_chest_core.name = "Part_ChestCore"
    m_chest_core.rotation_euler = (math.radians(90), 0, math.radians(180))
    bpy.ops.object.transform_apply(rotation=True)
    m_chest_core.data.materials.append(mat_cyan_glow)
    assign_vertex_group(m_chest_core, "Torso")
    mesh_parts.append(m_chest_core)

    # Chest Core Blue Housing Border
    bpy.ops.mesh.primitive_cylinder_add(vertices=3, radius=0.070, depth=0.02, location=(0, 0.135, 0.51))
    m_chest_rim = bpy.context.active_object
    m_chest_rim.name = "Part_ChestRim"
    m_chest_rim.rotation_euler = (math.radians(90), 0, math.radians(180))
    bpy.ops.object.transform_apply(rotation=True)
    m_chest_rim.data.materials.append(mat_royal_blue)
    assign_vertex_group(m_chest_rim, "Torso")
    mesh_parts.append(m_chest_rim)

    # 3. Royal Blue Backpack Unit (Model Sheet Detail Feature)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -0.15, 0.51))
    m_backpack = bpy.context.active_object
    m_backpack.name = "Part_Backpack"
    m_backpack.scale = (0.19, 0.08, 0.18)
    bpy.ops.object.transform_apply(scale=True)
    mod_b_bev = m_backpack.modifiers.new(name="Bevel", type='BEVEL')
    mod_b_bev.width = 0.02
    mod_b_bev.segments = 2
    bpy.ops.object.modifier_apply(modifier="Bevel")
    bpy.ops.object.shade_smooth()
    m_backpack.data.materials.append(mat_royal_blue)
    assign_vertex_group(m_backpack, "Torso")
    mesh_parts.append(m_backpack)

    # Glowing Cyan Triangular Energy Core on Backpack
    bpy.ops.mesh.primitive_cylinder_add(vertices=3, radius=0.050, depth=0.02, location=(0, -0.195, 0.51))
    m_back_core = bpy.context.active_object
    m_back_core.name = "Part_BackCore"
    m_back_core.rotation_euler = (math.radians(-90), 0, math.radians(180))
    bpy.ops.object.transform_apply(rotation=True)
    m_back_core.data.materials.append(mat_cyan_glow)
    assign_vertex_group(m_back_core, "Torso")
    mesh_parts.append(m_back_core)

    # =========================================================================
    # D. ARTICULATED ARMS & MECH HANDS (Navy Ball Joints + White Sleeves + Blue Cuffs)
    # =========================================================================
    for side, x, s_mult in [("L", -0.19, 1), ("R", 0.19, -1)]:
        # Shoulder Ball Joint (Deep Navy)
        bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=8, radius=0.055, location=(x, 0.01, 0.52))
        shoulder = bpy.context.active_object
        shoulder.name = f"Part_Shoulder_{side}"
        shoulder.data.materials.append(mat_navy)
        assign_vertex_group(shoulder, f"Arm.{side}")
        mesh_parts.append(shoulder)

        # White Upper Arm Cylinder
        bpy.ops.mesh.primitive_cylinder_add(vertices=14, radius=0.040, depth=0.14, location=(x * 1.22, 0.02, 0.44))
        u_arm = bpy.context.active_object
        u_arm.name = f"Part_UpperArm_{side}"
        u_arm.rotation_euler = (math.radians(10), math.radians(s_mult * 14), 0)
        bpy.ops.object.transform_apply(rotation=True)
        bpy.ops.object.shade_smooth()
        u_arm.data.materials.append(mat_white)
        assign_vertex_group(u_arm, f"Arm.{side}")
        mesh_parts.append(u_arm)

        # Elbow Joint Ring (Deep Navy)
        bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=8, radius=0.042, location=(x * 1.35, 0.03, 0.35))
        elbow = bpy.context.active_object
        elbow.name = f"Part_Elbow_{side}"
        elbow.data.materials.append(mat_navy)
        assign_vertex_group(elbow, f"Arm.{side}")
        mesh_parts.append(elbow)

        # Forearm Sleeve with Royal Blue Trim Cuff
        bpy.ops.mesh.primitive_cylinder_add(vertices=14, radius=0.044, depth=0.12, location=(x * 1.48, 0.05, 0.28))
        f_arm = bpy.context.active_object
        f_arm.name = f"Part_Forearm_{side}"
        f_arm.rotation_euler = (math.radians(14), math.radians(s_mult * 10), 0)
        bpy.ops.object.transform_apply(rotation=True)
        bpy.ops.object.shade_smooth()
        f_arm.data.materials.append(mat_white)
        assign_vertex_group(f_arm, f"Hand.{side}")
        mesh_parts.append(f_arm)

        # Forearm Royal Blue Trim Band
        bpy.ops.mesh.primitive_cylinder_add(vertices=14, radius=0.048, depth=0.03, location=(x * 1.46, 0.05, 0.31))
        arm_trim = bpy.context.active_object
        arm_trim.name = f"Part_ArmTrim_{side}"
        arm_trim.rotation_euler = (math.radians(14), math.radians(s_mult * 10), 0)
        bpy.ops.object.transform_apply(rotation=True)
        arm_trim.data.materials.append(mat_royal_blue)
        assign_vertex_group(arm_trim, f"Hand.{side}")
        mesh_parts.append(arm_trim)

        # Rounded Deep Navy Mech Hand
        bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=12, radius=0.055, location=(x * 1.60, 0.07, 0.20))
        hand = bpy.context.active_object
        hand.name = f"Part_Hand_{side}"
        hand.scale = (0.85, 1.15, 1.0)
        bpy.ops.object.transform_apply(scale=True)
        bpy.ops.object.shade_smooth()
        hand.data.materials.append(mat_navy)
        assign_vertex_group(hand, f"Hand.{side}")
        mesh_parts.append(hand)

        # Back-of-Hand White Armor Plate
        bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.032, depth=0.015, location=(x * 1.63, 0.04, 0.21))
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
        # Hip Ball Joint (Deep Navy)
        bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=8, radius=0.055, location=(x, 0, 0.32))
        hip = bpy.context.active_object
        hip.name = f"Part_Hip_{side}"
        hip.data.materials.append(mat_navy)
        assign_vertex_group(hip, f"Leg.{side}")
        mesh_parts.append(hip)

        # Thigh Armor Shell (White)
        bpy.ops.mesh.primitive_cylinder_add(vertices=14, radius=0.045, depth=0.12, location=(x, 0, 0.24))
        thigh = bpy.context.active_object
        thigh.name = f"Part_Thigh_{side}"
        bpy.ops.object.shade_smooth()
        thigh.data.materials.append(mat_white)
        assign_vertex_group(thigh, f"Leg.{side}")
        mesh_parts.append(thigh)

        # Knee Joint (Deep Navy)
        bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=8, radius=0.046, location=(x, 0.01, 0.17))
        knee = bpy.context.active_object
        knee.name = f"Part_Knee_{side}"
        knee.data.materials.append(mat_navy)
        assign_vertex_group(knee, f"Leg.{side}")
        mesh_parts.append(knee)

        # Shin Boot Cuff (White with Blue Base)
        bpy.ops.mesh.primitive_cylinder_add(vertices=14, radius=0.048, depth=0.10, location=(x, 0.01, 0.11))
        shin = bpy.context.active_object
        shin.name = f"Part_Shin_{side}"
        bpy.ops.object.shade_smooth()
        shin.data.materials.append(mat_white)
        assign_vertex_group(shin, f"Foot.{side}")
        mesh_parts.append(shin)

        # Front Half: Golden Yellow Rounded Toe Cap (Model Sheet Feature)
        bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=12, radius=0.080, location=(x, 0.055, 0.065))
        toe_cap = bpy.context.active_object
        toe_cap.name = f"Part_ToeCap_{side}"
        toe_cap.scale = (0.95, 1.15, 0.75)
        bpy.ops.object.transform_apply(scale=True)
        bpy.ops.object.shade_smooth()
        toe_cap.data.materials.append(mat_yellow)
        assign_vertex_group(toe_cap, f"Foot.{side}")
        mesh_parts.append(toe_cap)

        # Rear Half: Royal Blue Heel and Sole
        bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.076, depth=0.045, location=(x, -0.03, 0.025))
        heel_sole = bpy.context.active_object
        heel_sole.name = f"Part_HeelSole_{side}"
        heel_sole.scale = (1.0, 1.35, 1.0)
        bpy.ops.object.transform_apply(scale=True)
        heel_sole.data.materials.append(mat_royal_blue)
        assign_vertex_group(heel_sole, f"Foot.{side}")
        mesh_parts.append(heel_sole)

        # Glowing Cyan Circular Dot on Outer Ankle (Model Sheet Detail Feature)
        sign_x = -1 if side == "L" else 1
        bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.018, depth=0.015, location=(x + sign_x * 0.076, 0.01, 0.065))
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
    bpy.ops.object.shade_smooth()

    # Add Armature Modifier
    mod = char_mesh.modifiers.new(name="Armature", type='ARMATURE')
    mod.object = arm_obj
    char_mesh.parent = arm_obj

    # 5. Author Skeletal Animations Tailored to Model Sheet Anatomy
    bpy.context.view_layer.objects.active = arm_obj
    bpy.ops.object.mode_set(mode='POSE')
    arm_obj.animation_data_create()

    p_torso = arm_obj.pose.bones['Torso']
    p_head = arm_obj.pose.bones['Head']
    p_ant_l = arm_obj.pose.bones['Antenna.L']
    p_ant_r = arm_obj.pose.bones['Antenna.R']
    p_arm_l = arm_obj.pose.bones['Arm.L']
    p_hand_l = arm_obj.pose.bones['Hand.L']
    p_arm_r = arm_obj.pose.bones['Arm.R']
    p_hand_r = arm_obj.pose.bones['Hand.R']
    p_leg_l = arm_obj.pose.bones['Leg.L']
    p_foot_l = arm_obj.pose.bones['Foot.L']
    p_leg_r = arm_obj.pose.bones['Leg.R']
    p_foot_r = arm_obj.pose.bones['Foot.R']

    all_pose_bones = [p_torso, p_head, p_ant_l, p_ant_r, p_arm_l, p_hand_l, p_arm_r, p_hand_r, p_leg_l, p_foot_l, p_leg_r, p_foot_r]
    for pb in all_pose_bones:
        pb.rotation_mode = 'XYZ'

    def create_action(name):
        act = bpy.data.actions.new(name)
        act.use_fake_user = True
        arm_obj.animation_data.action = act
        for pb in all_pose_bones:
            pb.location = (0, 0, 0)
            pb.rotation_euler = (0, 0, 0)
            pb.scale = (1, 1, 1)
        return act

    def push_to_nla(act):
        track = arm_obj.animation_data.nla_tracks.new()
        track.name = act.name
        track.strips.new(act.name, 1, act)
        arm_obj.animation_data.action = None

    # --- 1. Idle (60 frames / 2.0s loop) ---
    act_idle = create_action("Idle")
    for frame, bob, ant_rot in [(1, 0.0, 0.0), (30, 0.022, -3.5), (60, 0.0, 0.0)]:
        keyframe_bone(p_torso, frame, loc=(0, 0, bob), rot_deg=(0, 0, 0))
        keyframe_bone(p_head, frame, rot_deg=(bob * 30.0, 0, 0))
        keyframe_bone(p_ant_l, frame, rot_deg=(ant_rot, 0, -ant_rot * 0.4))
        keyframe_bone(p_ant_r, frame, rot_deg=(ant_rot, 0, ant_rot * 0.4))
        keyframe_bone(p_arm_l, frame, rot_deg=(bob * -15.0, 0, 2.0))
        keyframe_bone(p_arm_r, frame, rot_deg=(bob * -15.0, 0, -2.0))
        keyframe_bone(p_leg_l, frame, rot_deg=(0, 0, 0))
        keyframe_bone(p_leg_r, frame, rot_deg=(0, 0, 0))
        keyframe_bone(p_foot_l, frame, rot_deg=(0, 0, 0))
        keyframe_bone(p_foot_r, frame, rot_deg=(0, 0, 0))
    push_to_nla(act_idle)

    # --- 2. Idle_Secondary (90 frames / 3.0s) ---
    act_idle_sec = create_action("Idle_Secondary")
    keyframe_bone(p_torso, 1, loc=(0, 0, 0), rot_deg=(0, 0, 0))
    keyframe_bone(p_head, 1, rot_deg=(0, 0, 0))
    keyframe_bone(p_arm_r, 1, rot_deg=(0, 0, 0))
    # Curious head tilt left, hand raising to wave
    keyframe_bone(p_head, 25, rot_deg=(6, -14, 14))
    keyframe_bone(p_ant_l, 25, rot_deg=(0, 0, 16))
    keyframe_bone(p_ant_r, 25, rot_deg=(0, 0, 16))
    keyframe_bone(p_arm_r, 25, rot_deg=(75, 0, -35))
    keyframe_bone(p_hand_r, 25, rot_deg=(0, 0, 25))
    # Wave right
    keyframe_bone(p_arm_r, 35, rot_deg=(78, 0, -20))
    keyframe_bone(p_hand_r, 35, rot_deg=(0, 0, -30))
    # Wave left
    keyframe_bone(p_arm_r, 45, rot_deg=(78, 0, -40))
    keyframe_bone(p_hand_r, 45, rot_deg=(0, 0, 30))
    # Curious look right
    keyframe_bone(p_head, 55, rot_deg=(-4, 14, -12))
    keyframe_bone(p_ant_l, 55, rot_deg=(0, 0, -12))
    keyframe_bone(p_ant_r, 55, rot_deg=(0, 0, -12))
    keyframe_bone(p_arm_r, 55, rot_deg=(40, 0, -15))
    keyframe_bone(p_hand_r, 55, rot_deg=(0, 0, 0))
    # Return to neutral
    keyframe_bone(p_torso, 90, loc=(0, 0, 0), rot_deg=(0, 0, 0))
    keyframe_bone(p_head, 90, rot_deg=(0, 0, 0))
    keyframe_bone(p_ant_l, 90, rot_deg=(0, 0, 0))
    keyframe_bone(p_ant_r, 90, rot_deg=(0, 0, 0))
    keyframe_bone(p_arm_r, 90, rot_deg=(0, 0, 0))
    keyframe_bone(p_hand_r, 90, rot_deg=(0, 0, 0))
    push_to_nla(act_idle_sec)

    # --- 3. Walk (30 frames / 1.0s loop) ---
    act_walk = create_action("Walk")
    walk_keys = [
        # frame, torso_z, torso_yaw, l_rot, l_pos_z, r_rot, r_pos_z, arm_l, arm_r
        (1,  0.0,   -3,  26, 0.0,   -26, 0.0,   -26,  26),
        (8,  0.025,  0,   0, 0.0,     0, 0.08,    0,   0),
        (15, 0.0,    3, -26, 0.0,    26, 0.0,    26, -26),
        (23, 0.025,  0,   0, 0.08,    0, 0.0,     0,   0),
        (30, 0.0,   -3,  26, 0.0,   -26, 0.0,   -26,  26)
    ]
    for frame, tz, tyaw, l_rot, l_pz, r_rot, r_pz, al, ar in walk_keys:
        keyframe_bone(p_torso, frame, loc=(0, 0, tz), rot_deg=(3, tyaw, -tyaw * 0.5))
        keyframe_bone(p_head, frame, rot_deg=(0, -tyaw * 0.7, 0))
        keyframe_bone(p_ant_l, frame, rot_deg=(al * 0.25, 0, -tyaw))
        keyframe_bone(p_ant_r, frame, rot_deg=(ar * 0.25, 0, -tyaw))
        keyframe_bone(p_arm_l, frame, rot_deg=(al, 0, 6))
        keyframe_bone(p_arm_r, frame, rot_deg=(ar, 0, -6))
        keyframe_bone(p_leg_l, frame, loc=(0, 0, l_pz), rot_deg=(l_rot, 0, 0))
        keyframe_bone(p_leg_r, frame, loc=(0, 0, r_pz), rot_deg=(r_rot, 0, 0))
        keyframe_bone(p_foot_l, frame, rot_deg=(-l_rot * 0.45, 0, 0))
        keyframe_bone(p_foot_r, frame, rot_deg=(-r_rot * 0.45, 0, 0))
    push_to_nla(act_walk)

    # --- 4. Run (20 frames / 0.67s loop) ---
    act_run = create_action("Run")
    run_keys = [
        (1,  0.01,  -6,  44, 0.0,   -44, 0.0,   -48,  48),
        (5,  0.045,  0,   0, 0.0,     0, 0.13,    0,   0),
        (10, 0.01,   6, -44, 0.0,    44, 0.0,    48, -48),
        (15, 0.045,  0,   0, 0.13,    0, 0.0,     0,   0),
        (20, 0.01,  -6,  44, 0.0,   -44, 0.0,   -48,  48)
    ]
    for frame, tz, tyaw, l_rot, l_pz, r_rot, r_pz, al, ar in run_keys:
        keyframe_bone(p_torso, frame, loc=(0, 0, tz), rot_deg=(-14, tyaw, -tyaw * 0.6))
        keyframe_bone(p_head, frame, rot_deg=(9, -tyaw * 0.5, 0))
        keyframe_bone(p_ant_l, frame, rot_deg=(-20, 0, -tyaw * 1.5))
        keyframe_bone(p_ant_r, frame, rot_deg=(-20, 0, -tyaw * 1.5))
        keyframe_bone(p_arm_l, frame, rot_deg=(al, 0, 12))
        keyframe_bone(p_arm_r, frame, rot_deg=(ar, 0, -12))
        keyframe_bone(p_leg_l, frame, loc=(0, 0, l_pz), rot_deg=(l_rot, 0, 0))
        keyframe_bone(p_leg_r, frame, loc=(0, 0, r_pz), rot_deg=(r_rot, 0, 0))
        keyframe_bone(p_foot_l, frame, rot_deg=(-l_rot * 0.55, 0, 0))
        keyframe_bone(p_foot_r, frame, rot_deg=(-r_rot * 0.55, 0, 0))
    push_to_nla(act_run)

    # --- 5. Jump_Start (10 frames / 0.33s) ---
    act_jump_start = create_action("Jump_Start")
    keyframe_bone(p_torso, 1, loc=(0, 0, 0), rot_deg=(0, 0, 0))
    # Anticipation crouch
    keyframe_bone(p_torso, 4, loc=(0, 0, -0.10), rot_deg=(-8, 0, 0))
    keyframe_bone(p_head, 4, rot_deg=(12, 0, 0))
    keyframe_bone(p_ant_l, 4, rot_deg=(-16, 0, 0))
    keyframe_bone(p_ant_r, 4, rot_deg=(-16, 0, 0))
    keyframe_bone(p_arm_l, 4, rot_deg=(-38, 0, 18))
    keyframe_bone(p_arm_r, 4, rot_deg=(-38, 0, -18))
    keyframe_bone(p_leg_l, 4, rot_deg=(-18, 0, 0))
    keyframe_bone(p_leg_r, 4, rot_deg=(-18, 0, 0))
    # Takeoff launch
    keyframe_bone(p_torso, 10, loc=(0, 0, 0.14), rot_deg=(14, 0, 0))
    keyframe_bone(p_head, 10, rot_deg=(-9, 0, 0))
    keyframe_bone(p_ant_l, 10, rot_deg=(28, 0, 0))
    keyframe_bone(p_ant_r, 10, rot_deg=(28, 0, 0))
    keyframe_bone(p_arm_l, 10, rot_deg=(70, 0, 22))
    keyframe_bone(p_arm_r, 10, rot_deg=(70, 0, -22))
    keyframe_bone(p_leg_l, 10, rot_deg=(22, 0, 0))
    keyframe_bone(p_leg_r, 10, rot_deg=(22, 0, 0))
    push_to_nla(act_jump_start)

    # --- 6. Jump_Loop (20 frames / 0.67s loop) ---
    act_jump_loop = create_action("Jump_Loop")
    for frame, float_y in [(1, 0.07), (10, 0.09), (20, 0.07)]:
        keyframe_bone(p_torso, frame, loc=(0, 0, float_y), rot_deg=(6, 0, 0))
        keyframe_bone(p_head, frame, rot_deg=(-5, 0, 0))
        keyframe_bone(p_ant_l, frame, rot_deg=(-12, 0, -6))
        keyframe_bone(p_ant_r, frame, rot_deg=(-12, 0, 6))
        keyframe_bone(p_arm_l, frame, rot_deg=(38, 0, 32))
        keyframe_bone(p_arm_r, frame, rot_deg=(38, 0, -32))
        keyframe_bone(p_leg_l, frame, rot_deg=(-14, 0, 0))
        keyframe_bone(p_leg_r, frame, rot_deg=(-14, 0, 0))
        keyframe_bone(p_foot_l, frame, rot_deg=(26, 0, 0))
        keyframe_bone(p_foot_r, frame, rot_deg=(26, 0, 0))
    push_to_nla(act_jump_loop)

    # --- 7. Fall (20 frames / 0.67s loop) ---
    act_fall = create_action("Fall")
    for frame, flail in [(1, 0), (10, 1), (20, 0)]:
        deg_flail = 16 if flail == 1 else -16
        keyframe_bone(p_torso, frame, loc=(0, 0, 0), rot_deg=(12, 0, 0))
        keyframe_bone(p_head, frame, rot_deg=(-9, 0, 0))
        keyframe_bone(p_ant_l, frame, rot_deg=(22, 0, 12))
        keyframe_bone(p_ant_r, frame, rot_deg=(22, 0, -12))
        keyframe_bone(p_arm_l, frame, rot_deg=(60 + deg_flail, 0, 38))
        keyframe_bone(p_arm_r, frame, rot_deg=(60 - deg_flail, 0, -38))
        keyframe_bone(p_leg_l, frame, rot_deg=(16 - deg_flail * 0.5, 0, 6))
        keyframe_bone(p_leg_r, frame, rot_deg=(16 + deg_flail * 0.5, 0, -6))
        keyframe_bone(p_foot_l, frame, rot_deg=(-22, 0, 0))
        keyframe_bone(p_foot_r, frame, rot_deg=(-22, 0, 0))
    push_to_nla(act_fall)

    # --- 8. Landing (15 frames / 0.5s) ---
    act_landing = create_action("Landing")
    keyframe_bone(p_torso, 1, loc=(0, 0, 0), rot_deg=(0, 0, 0))
    # Squash compression
    keyframe_bone(p_torso, 4, loc=(0, 0, -0.13), rot_deg=(-6, 0, 0))
    keyframe_bone(p_head, 4, rot_deg=(10, 0, 0))
    keyframe_bone(p_ant_l, 4, rot_deg=(24, 0, 0))
    keyframe_bone(p_ant_r, 4, rot_deg=(24, 0, 0))
    keyframe_bone(p_arm_l, 4, rot_deg=(-28, 0, 38))
    keyframe_bone(p_arm_r, 4, rot_deg=(-28, 0, -38))
    keyframe_bone(p_leg_l, 4, rot_deg=(-22, 0, 0))
    keyframe_bone(p_leg_r, 4, rot_deg=(-22, 0, 0))
    # Rebound
    keyframe_bone(p_torso, 9, loc=(0, 0, 0.04), rot_deg=(2, 0, 0))
    keyframe_bone(p_head, 9, rot_deg=(-3, 0, 0))
    keyframe_bone(p_ant_l, 9, rot_deg=(-10, 0, 0))
    keyframe_bone(p_ant_r, 9, rot_deg=(-10, 0, 0))
    keyframe_bone(p_arm_l, 9, rot_deg=(16, 0, 12))
    keyframe_bone(p_arm_r, 9, rot_deg=(16, 0, -12))
    # Neutral
    keyframe_bone(p_torso, 15, loc=(0, 0, 0), rot_deg=(0, 0, 0))
    keyframe_bone(p_head, 15, rot_deg=(0, 0, 0))
    keyframe_bone(p_ant_l, 15, rot_deg=(0, 0, 0))
    keyframe_bone(p_ant_r, 15, rot_deg=(0, 0, 0))
    keyframe_bone(p_arm_l, 15, rot_deg=(0, 0, 0))
    keyframe_bone(p_arm_r, 15, rot_deg=(0, 0, 0))
    keyframe_bone(p_leg_l, 15, rot_deg=(0, 0, 0))
    keyframe_bone(p_leg_r, 15, rot_deg=(0, 0, 0))
    push_to_nla(act_landing)

    # --- 9. Turn_Left (12 frames / 0.4s) ---
    act_turn_l = create_action("Turn_Left")
    keyframe_bone(p_torso, 1, rot_deg=(0, 0, 0))
    keyframe_bone(p_torso, 5, rot_deg=(2, 19, 11))
    keyframe_bone(p_head, 5, rot_deg=(0, 30, 9))
    keyframe_bone(p_ant_l, 5, rot_deg=(0, 0, 19))
    keyframe_bone(p_ant_r, 5, rot_deg=(0, 0, 19))
    keyframe_bone(p_arm_l, 5, rot_deg=(-22, 0, 16))
    keyframe_bone(p_arm_r, 5, rot_deg=(26, 0, -16))
    keyframe_bone(p_torso, 12, rot_deg=(0, 0, 0))
    keyframe_bone(p_head, 12, rot_deg=(0, 0, 0))
    keyframe_bone(p_ant_l, 12, rot_deg=(0, 0, 0))
    keyframe_bone(p_ant_r, 12, rot_deg=(0, 0, 0))
    keyframe_bone(p_arm_l, 12, rot_deg=(0, 0, 0))
    keyframe_bone(p_arm_r, 12, rot_deg=(0, 0, 0))
    push_to_nla(act_turn_l)

    # --- 10. Turn_Right (12 frames / 0.4s) ---
    act_turn_r = create_action("Turn_Right")
    keyframe_bone(p_torso, 1, rot_deg=(0, 0, 0))
    keyframe_bone(p_torso, 5, rot_deg=(2, -19, -11))
    keyframe_bone(p_head, 5, rot_deg=(0, -30, -9))
    keyframe_bone(p_ant_l, 5, rot_deg=(0, 0, -19))
    keyframe_bone(p_ant_r, 5, rot_deg=(0, 0, -19))
    keyframe_bone(p_arm_l, 5, rot_deg=(26, 0, 16))
    keyframe_bone(p_arm_r, 5, rot_deg=(-22, 0, -16))
    keyframe_bone(p_torso, 12, rot_deg=(0, 0, 0))
    keyframe_bone(p_head, 12, rot_deg=(0, 0, 0))
    keyframe_bone(p_ant_l, 12, rot_deg=(0, 0, 0))
    keyframe_bone(p_ant_r, 12, rot_deg=(0, 0, 0))
    keyframe_bone(p_arm_l, 12, rot_deg=(0, 0, 0))
    keyframe_bone(p_arm_r, 12, rot_deg=(0, 0, 0))
    push_to_nla(act_turn_r)

    # --- 11. Collect (24 frames / 0.8s) ---
    act_collect = create_action("Collect")
    keyframe_bone(p_torso, 1, loc=(0, 0, 0), rot_deg=(0, 0, 0))
    keyframe_bone(p_torso, 5, loc=(0, 0, -0.06), rot_deg=(0, 0, 0))
    # Double fist pump leap
    keyframe_bone(p_torso, 12, loc=(0, 0, 0.17), rot_deg=(-9, 0, 0))
    keyframe_bone(p_head, 12, rot_deg=(-20, 0, 0))
    keyframe_bone(p_ant_l, 12, rot_deg=(16, 0, -14))
    keyframe_bone(p_ant_r, 12, rot_deg=(16, 0, 14))
    keyframe_bone(p_arm_l, 12, rot_deg=(98, 0, 32))
    keyframe_bone(p_arm_r, 12, rot_deg=(98, 0, -32))
    keyframe_bone(p_hand_l, 12, rot_deg=(28, 0, 0))
    keyframe_bone(p_hand_r, 12, rot_deg=(28, 0, 0))
    keyframe_bone(p_leg_l, 12, rot_deg=(16, 0, 0))
    keyframe_bone(p_leg_r, 12, rot_deg=(16, 0, 0))
    # Land
    keyframe_bone(p_torso, 18, loc=(0, 0, -0.04), rot_deg=(0, 0, 0))
    keyframe_bone(p_arm_l, 18, rot_deg=(32, 0, 12))
    keyframe_bone(p_arm_r, 18, rot_deg=(32, 0, -12))
    # Neutral
    keyframe_bone(p_torso, 24, loc=(0, 0, 0), rot_deg=(0, 0, 0))
    keyframe_bone(p_head, 24, rot_deg=(0, 0, 0))
    keyframe_bone(p_ant_l, 24, rot_deg=(0, 0, 0))
    keyframe_bone(p_ant_r, 24, rot_deg=(0, 0, 0))
    keyframe_bone(p_arm_l, 24, rot_deg=(0, 0, 0))
    keyframe_bone(p_arm_r, 24, rot_deg=(0, 0, 0))
    keyframe_bone(p_leg_l, 24, rot_deg=(0, 0, 0))
    keyframe_bone(p_leg_r, 24, rot_deg=(0, 0, 0))
    push_to_nla(act_collect)

    # --- 12. Interact (24 frames / 0.8s) ---
    act_interact = create_action("Interact")
    keyframe_bone(p_torso, 1, rot_deg=(0, 0, 0))
    keyframe_bone(p_torso, 6, rot_deg=(-9, 0, 0))
    keyframe_bone(p_head, 6, rot_deg=(12, 0, 0))
    # Reaching out with right mechanical hand
    keyframe_bone(p_torso, 12, rot_deg=(-13, 6, 0))
    keyframe_bone(p_head, 12, rot_deg=(15, 0, 0))
    keyframe_bone(p_arm_r, 12, rot_deg=(88, 0, -12))
    keyframe_bone(p_hand_r, 12, rot_deg=(28, 0, 0))
    # Decisive press
    keyframe_bone(p_arm_r, 16, rot_deg=(94, 0, -10))
    keyframe_bone(p_head, 16, rot_deg=(20, 0, 0))
    # Return
    keyframe_bone(p_torso, 24, rot_deg=(0, 0, 0))
    keyframe_bone(p_head, 24, rot_deg=(0, 0, 0))
    keyframe_bone(p_arm_r, 24, rot_deg=(0, 0, 0))
    keyframe_bone(p_hand_r, 24, rot_deg=(0, 0, 0))
    push_to_nla(act_interact)

    # --- 13. Victory (75 frames / 2.5s) ---
    act_victory = create_action("Victory")
    keyframe_bone(p_torso, 1, loc=(0, 0, 0), rot_deg=(0, 0, 0))
    # 360-degree pirouette spin
    keyframe_bone(p_torso, 10, loc=(0, 0, 0.12), rot_deg=(0, 180, 0))
    keyframe_bone(p_arm_l, 10, rot_deg=(48, 0, 48))
    keyframe_bone(p_arm_r, 10, rot_deg=(48, 0, -48))
    keyframe_bone(p_torso, 20, loc=(0, 0, 0.0), rot_deg=(0, 360, 0))
    # Hop 1
    keyframe_bone(p_torso, 30, loc=(0, 0, 0.20), rot_deg=(-6, 360, 0))
    keyframe_bone(p_arm_l, 30, rot_deg=(88, 0, 38))
    keyframe_bone(p_arm_r, 30, rot_deg=(88, 0, -38))
    keyframe_bone(p_torso, 40, loc=(0, 0, -0.04), rot_deg=(0, 360, 0))
    # Hop 2
    keyframe_bone(p_torso, 50, loc=(0, 0, 0.20), rot_deg=(-6, 360, 0))
    keyframe_bone(p_head, 50, rot_deg=(-16, 0, 12))
    keyframe_bone(p_arm_l, 50, rot_deg=(98, 0, 42))
    keyframe_bone(p_arm_r, 50, rot_deg=(98, 0, -42))
    # Side-to-side cute torso sway
    keyframe_bone(p_torso, 60, loc=(0, 0, 0), rot_deg=(0, 360, 14))
    keyframe_bone(p_head, 60, rot_deg=(0, 0, -12))
    # Final hero freeze pose waving to player!
    keyframe_bone(p_torso, 75, loc=(0, 0, 0), rot_deg=(0, 360, -9))
    keyframe_bone(p_head, 75, rot_deg=(-6, 0, 14))
    keyframe_bone(p_ant_l, 75, rot_deg=(0, 0, 16))
    keyframe_bone(p_ant_r, 75, rot_deg=(0, 0, 16))
    keyframe_bone(p_arm_r, 75, rot_deg=(-22, 0, -28)) # right hand on hip
    keyframe_bone(p_hand_r, 75, rot_deg=(42, 0, 0))
    keyframe_bone(p_arm_l, 75, rot_deg=(78, 0, 32))   # left hand waving
    keyframe_bone(p_hand_l, 75, rot_deg=(0, 0, 22))
    push_to_nla(act_victory)

    # --- 14. Respawn (30 frames / 1.0s) ---
    act_respawn = create_action("Respawn")
    # Compact crouch reboot
    keyframe_bone(p_torso, 1, loc=(0, 0, -0.13), rot_deg=(16, 0, 0))
    keyframe_bone(p_head, 1, rot_deg=(28, 0, 0))
    keyframe_bone(p_ant_l, 1, rot_deg=(-28, 0, -12))
    keyframe_bone(p_ant_r, 1, rot_deg=(-28, 0, 12))
    keyframe_bone(p_arm_l, 1, rot_deg=(-22, 0, 12))
    keyframe_bone(p_arm_r, 1, rot_deg=(-22, 0, -12))
    # System boot head snap
    keyframe_bone(p_torso, 10, loc=(0, 0, -0.06), rot_deg=(-6, 0, 0))
    keyframe_bone(p_head, 10, rot_deg=(-16, 0, 0))
    keyframe_bone(p_ant_l, 10, rot_deg=(28, 0, 16))
    keyframe_bone(p_ant_r, 10, rot_deg=(28, 0, -16))
    # Dust shake
    keyframe_bone(p_torso, 18, loc=(0, 0, 0), rot_deg=(0, 22, 6))
    keyframe_bone(p_head, 18, rot_deg=(0, -28, 0))
    keyframe_bone(p_torso, 24, loc=(0, 0, 0), rot_deg=(0, -22, -6))
    keyframe_bone(p_head, 24, rot_deg=(0, 28, 0))
    # Alert ready
    keyframe_bone(p_torso, 30, loc=(0, 0, 0), rot_deg=(0, 0, 0))
    keyframe_bone(p_head, 30, rot_deg=(0, 0, 0))
    keyframe_bone(p_ant_l, 30, rot_deg=(0, 0, 0))
    keyframe_bone(p_ant_r, 30, rot_deg=(0, 0, 0))
    keyframe_bone(p_arm_l, 30, rot_deg=(0, 0, 0))
    keyframe_bone(p_arm_r, 30, rot_deg=(0, 0, 0))
    push_to_nla(act_respawn)

    bpy.ops.object.mode_set(mode='OBJECT')

    # 6. Save Blender Source .blend
    blend_path = os.path.join(source_dir, "bot_character.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print(f"✓ Saved Blender source to: {blend_path}")

    # 7. Export GLB with Armature, Skinning, and All 14 Actions
    glb_char_path = os.path.join(char_model_dir, "bot.glb")
    glb_root_path = os.path.join(root_model_dir, "bot.glb")

    bpy.ops.export_scene.gltf(
        filepath=glb_char_path,
        export_format='GLB',
        use_selection=False,
        export_animations=True,
        export_animation_mode='ACTIONS',
        export_anim_single_armature=True,
        export_optimize_animation_size=True,
        export_skins=True
    )

    bpy.ops.export_scene.gltf(
        filepath=glb_root_path,
        export_format='GLB',
        use_selection=False,
        export_animations=True,
        export_animation_mode='ACTIONS',
        export_anim_single_armature=True,
        export_optimize_animation_size=True,
        export_skins=True
    )
    print(f"✓ Exported official B.O.T GLB to: {glb_char_path} & {glb_root_path}")

if __name__ == "__main__":
    build_model_sheet_bot()
    print("B.O.T Model Sheet Character production complete!")
