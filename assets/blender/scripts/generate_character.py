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

def build_new_bot_character():
    clean_scene()
    script_dir = os.path.dirname(os.path.abspath(__file__))
    source_dir = os.path.join(script_dir, "..", "source")
    char_model_dir = os.path.join(script_dir, "..", "..", "models", "characters")
    root_model_dir = os.path.join(script_dir, "..", "..", "models")
    os.makedirs(source_dir, exist_ok=True)
    os.makedirs(char_model_dir, exist_ok=True)

    # 1. High-Quality Stylized PBR Materials
    # Premium satin white ceramic armor panels
    mat_white = create_pbr_material("Mat_Bot_WhiteArmor", (0.94, 0.94, 0.97, 1.0), metallic=0.08, roughness=0.22)
    # Gunmetal / dark titanium for mechanical joints, neck, chassis, sole
    mat_dark = create_pbr_material("Mat_Bot_DarkChassis", (0.16, 0.18, 0.22, 1.0), metallic=0.85, roughness=0.30)
    # Deep gloss obsidian visor screen
    mat_visor = create_pbr_material("Mat_Bot_Visor", (0.02, 0.03, 0.05, 1.0), metallic=0.95, roughness=0.08)
    # High-intensity glowing cyan LED for eyes and power matrices
    mat_cyan_glow = create_pbr_material("Mat_Bot_CyanLED", (0.0, 0.95, 1.0, 1.0), metallic=0.0, roughness=0.15, emission=(0.0, 0.95, 1.0, 1.0), emission_strength=4.0)
    # Sunset energetic orange / warm gold trim accents
    mat_orange = create_pbr_material("Mat_Bot_OrangeAccent", (1.0, 0.48, 0.08, 1.0), metallic=0.45, roughness=0.28)

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

    # Torso (Center of mass, chassis)
    create_bone(arm_data, 'Torso', 'Root', head=(0, 0, 0.36), tail=(0, 0, 0.68))
    # Head (Separate neck and monitor helmet)
    create_bone(arm_data, 'Head', 'Torso', head=(0, 0, 0.68), tail=(0, 0, 1.04))
    # Antennas
    create_bone(arm_data, 'Antenna.L', 'Head', head=(-0.16, 0.02, 1.04), tail=(-0.24, 0.02, 1.28))
    create_bone(arm_data, 'Antenna.R', 'Head', head=(0.16, 0.02, 1.04), tail=(0.24, 0.02, 1.28))

    # Segmented Arms
    create_bone(arm_data, 'Arm.L', 'Torso', head=(-0.24, 0.0, 0.60), tail=(-0.36, 0.02, 0.44))
    create_bone(arm_data, 'Hand.L', 'Arm.L', head=(-0.36, 0.02, 0.44), tail=(-0.44, 0.06, 0.24))

    create_bone(arm_data, 'Arm.R', 'Torso', head=(0.24, 0.0, 0.60), tail=(0.36, 0.02, 0.44))
    create_bone(arm_data, 'Hand.R', 'Arm.R', head=(0.36, 0.02, 0.44), tail=(0.44, 0.06, 0.24))

    # Segmented Legs
    create_bone(arm_data, 'Leg.L', 'Root', head=(-0.15, 0.0, 0.36), tail=(-0.15, 0.0, 0.16))
    create_bone(arm_data, 'Foot.L', 'Leg.L', head=(-0.15, 0.0, 0.16), tail=(-0.15, 0.16, 0.0))

    create_bone(arm_data, 'Leg.R', 'Root', head=(0.15, 0.0, 0.36), tail=(0.15, 0.0, 0.16))
    create_bone(arm_data, 'Foot.R', 'Leg.R', head=(0.15, 0.0, 0.16), tail=(0.15, 0.16, 0.0))

    bpy.ops.object.mode_set(mode='OBJECT')

    # 3. Model Meshes — Concept A: "The Modular Retro-Chibi Explorer"
    mesh_parts = []

    # =========================================================================
    # A. HEAD GROUP (Chamfered TV-Monitor Helmet + Curved Visor + Expressive Eyes)
    # =========================================================================
    # 1. Main Helmet: Beveled chamfered box (NOT egg-shaped!)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.86))
    m_helmet = bpy.context.active_object
    m_helmet.name = "Part_Helmet"
    m_helmet.scale = (0.44, 0.38, 0.34)
    bpy.ops.object.transform_apply(scale=True)
    mod_bev = m_helmet.modifiers.new(name="Bevel", type='BEVEL')
    mod_bev.width = 0.07
    mod_bev.segments = 3
    bpy.ops.object.modifier_apply(modifier="Bevel")
    bpy.ops.object.shade_smooth()
    m_helmet.data.materials.append(mat_white)
    assign_vertex_group(m_helmet, "Head")
    mesh_parts.append(m_helmet)

    # 2. Visor Screen: Dark glossy curved front panel
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0.18, 0.86))
    m_visor = bpy.context.active_object
    m_visor.name = "Part_Visor"
    m_visor.scale = (0.36, 0.05, 0.24)
    bpy.ops.object.transform_apply(scale=True)
    mod_vbev = m_visor.modifiers.new(name="Bevel", type='BEVEL')
    mod_vbev.width = 0.03
    mod_vbev.segments = 2
    bpy.ops.object.modifier_apply(modifier="Bevel")
    bpy.ops.object.shade_smooth()
    m_visor.data.materials.append(mat_visor)
    assign_vertex_group(m_visor, "Head")
    mesh_parts.append(m_visor)

    # 3. Expressive Cyan LED Eyes: Bold rounded capsules on visor
    for side, x, rot in [("L", -0.095, -4), ("R", 0.095, 4)]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.045, depth=0.03, location=(x, 0.21, 0.86))
        eye = bpy.context.active_object
        eye.name = f"Part_Eye_{side}"
        eye.rotation_euler = (math.radians(90), 0, math.radians(rot))
        eye.scale = (0.9, 1.0, 1.4) # Chibi pill shape
        bpy.ops.object.transform_apply(rotation=True, scale=True)
        bpy.ops.object.shade_smooth()
        eye.data.materials.append(mat_cyan_glow)
        assign_vertex_group(eye, "Head")
        mesh_parts.append(eye)

    # 4. Audio Headphone Canisters (Left and Right ears)
    for side, x, rot in [("L", -0.23, 90), ("R", 0.23, -90)]:
        # Dark ear base
        bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.08, depth=0.05, location=(x, 0, 0.86))
        ear_base = bpy.context.active_object
        ear_base.name = f"Part_EarBase_{side}"
        ear_base.rotation_euler = (0, math.radians(rot), 0)
        bpy.ops.object.transform_apply(rotation=True)
        bpy.ops.object.shade_smooth()
        ear_base.data.materials.append(mat_dark)
        assign_vertex_group(ear_base, "Head")
        mesh_parts.append(ear_base)

        # Orange outer accent ring
        bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.065, depth=0.06, location=(x * 1.08, 0, 0.86))
        ear_ring = bpy.context.active_object
        ear_ring.name = f"Part_EarRing_{side}"
        ear_ring.rotation_euler = (0, math.radians(rot), 0)
        bpy.ops.object.transform_apply(rotation=True)
        bpy.ops.object.shade_smooth()
        ear_ring.data.materials.append(mat_orange)
        assign_vertex_group(ear_ring, "Head")
        mesh_parts.append(ear_ring)

        # Cyan inner sensor dot
        bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=8, radius=0.03, location=(x * 1.15, 0, 0.86))
        ear_dot = bpy.context.active_object
        ear_dot.name = f"Part_EarDot_{side}"
        bpy.ops.object.shade_smooth()
        ear_dot.data.materials.append(mat_cyan_glow)
        assign_vertex_group(ear_dot, "Head")
        mesh_parts.append(ear_dot)

    # =========================================================================
    # B. ANTENNA SYSTEM (Communication Fin + Beacon array)
    # =========================================================================
    for side, x, sign in [("L", -0.15, -1), ("R", 0.15, 1)]:
        # Angled titanium stem
        bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.016, depth=0.20, location=(x, 0.02, 1.12))
        stem = bpy.context.active_object
        stem.name = f"Part_AntennaStem_{side}"
        stem.rotation_euler = (math.radians(-6), math.radians(sign * 18), 0)
        bpy.ops.object.transform_apply(rotation=True)
        bpy.ops.object.shade_smooth()
        stem.data.materials.append(mat_dark)
        assign_vertex_group(stem, f"Antenna.{side}")
        mesh_parts.append(stem)

        # Orange mid-joint ring
        bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.028, depth=0.03, location=(x * 1.25, 0.02, 1.12))
        ring = bpy.context.active_object
        ring.name = f"Part_AntennaRing_{side}"
        ring.rotation_euler = (math.radians(-6), math.radians(sign * 18), 0)
        bpy.ops.object.transform_apply(rotation=True)
        ring.data.materials.append(mat_orange)
        assign_vertex_group(ring, f"Antenna.{side}")
        mesh_parts.append(ring)

        # Glowing Cyan Beacon Orb
        bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=12, radius=0.05, location=(x * 1.48, 0.02, 1.23))
        orb = bpy.context.active_object
        orb.name = f"Part_AntennaOrb_{side}"
        bpy.ops.object.shade_smooth()
        orb.data.materials.append(mat_cyan_glow)
        assign_vertex_group(orb, f"Antenna.{side}")
        mesh_parts.append(orb)

    # =========================================================================
    # C. TORSO & CHASSIS (Tapered Chest + Visible Neck + Reactor Pack)
    # =========================================================================
    # 1. Visible Mechanical Neck Collar (connects Head to Torso)
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.11, depth=0.08, location=(0, 0, 0.70))
    m_neck = bpy.context.active_object
    m_neck.name = "Part_Neck"
    bpy.ops.object.shade_smooth()
    m_neck.data.materials.append(mat_dark)
    assign_vertex_group(m_neck, "Torso")
    mesh_parts.append(m_neck)

    # 2. Main Chest Chassis: Tapered trapezoid (wider at shoulders, compact at waist)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.52))
    m_chest = bpy.context.active_object
    m_chest.name = "Part_Chest"
    m_chest.scale = (0.34, 0.26, 0.28)
    bpy.ops.object.transform_apply(scale=True)
    mod_cbev = m_chest.modifiers.new(name="Bevel", type='BEVEL')
    mod_cbev.width = 0.04
    mod_cbev.segments = 3
    bpy.ops.object.modifier_apply(modifier="Bevel")
    bpy.ops.object.shade_smooth()
    m_chest.data.materials.append(mat_white)
    assign_vertex_group(m_chest, "Torso")
    mesh_parts.append(m_chest)

    # 3. Orange Chest Trim Vents / Side Shoulders
    for side, x in [("L", -0.16), ("R", 0.16)]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(x, 0.02, 0.56))
        vent = bpy.context.active_object
        vent.name = f"Part_ChestVent_{side}"
        vent.scale = (0.04, 0.22, 0.08)
        bpy.ops.object.transform_apply(scale=True)
        bpy.ops.object.shade_smooth()
        vent.data.materials.append(mat_orange)
        assign_vertex_group(vent, "Torso")
        mesh_parts.append(vent)

    # 4. Center Reactor Core Medallion
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.08, depth=0.03, location=(0, 0.14, 0.53))
    m_core_rim = bpy.context.active_object
    m_core_rim.name = "Part_CoreRim"
    m_core_rim.rotation_euler = (math.radians(90), 0, 0)
    bpy.ops.object.transform_apply(rotation=True)
    bpy.ops.object.shade_smooth()
    m_core_rim.data.materials.append(mat_dark)
    assign_vertex_group(m_core_rim, "Torso")
    mesh_parts.append(m_core_rim)

    # Glowing Cyan Core Center
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.06, depth=0.04, location=(0, 0.15, 0.53))
    m_core_light = bpy.context.active_object
    m_core_light.name = "Part_CoreLight"
    m_core_light.rotation_euler = (math.radians(90), 0, 0)
    bpy.ops.object.transform_apply(rotation=True)
    bpy.ops.object.shade_smooth()
    m_core_light.data.materials.append(mat_cyan_glow)
    assign_vertex_group(m_core_light, "Torso")
    mesh_parts.append(m_core_light)

    # 5. High-Tech Backpack Generator
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -0.18, 0.53))
    m_backpack = bpy.context.active_object
    m_backpack.name = "Part_Backpack"
    m_backpack.scale = (0.26, 0.12, 0.22)
    bpy.ops.object.transform_apply(scale=True)
    mod_bbev = m_backpack.modifiers.new(name="Bevel", type='BEVEL')
    mod_bbev.width = 0.025
    mod_bbev.segments = 2
    bpy.ops.object.modifier_apply(modifier="Bevel")
    bpy.ops.object.shade_smooth()
    m_backpack.data.materials.append(mat_dark)
    assign_vertex_group(m_backpack, "Torso")
    mesh_parts.append(m_backpack)

    # Cyan Energy Canister Cell on Backpack
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.05, depth=0.18, location=(0, -0.25, 0.53))
    m_back_core = bpy.context.active_object
    m_back_core.name = "Part_BackCore"
    m_back_core.rotation_euler = (0, math.radians(90), 0)
    bpy.ops.object.transform_apply(rotation=True)
    bpy.ops.object.shade_smooth()
    m_back_core.data.materials.append(mat_cyan_glow)
    assign_vertex_group(m_back_core, "Torso")
    mesh_parts.append(m_back_core)

    # Dual Angled Rocket Thruster Nozzles
    for side, x in [("L", -0.09), ("R", 0.09)]:
        bpy.ops.mesh.primitive_cone_add(vertices=16, radius1=0.045, radius2=0.03, depth=0.11, location=(x, -0.21, 0.38))
        nozzle = bpy.context.active_object
        nozzle.name = f"Part_Thruster_{side}"
        nozzle.rotation_euler = (math.radians(160), 0, 0)
        bpy.ops.object.transform_apply(rotation=True)
        bpy.ops.object.shade_smooth()
        nozzle.data.materials.append(mat_orange)
        assign_vertex_group(nozzle, "Torso")
        mesh_parts.append(nozzle)

    # Mechanical Pelvis / Waist Bar
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.37))
    m_pelvis = bpy.context.active_object
    m_pelvis.name = "Part_Pelvis"
    m_pelvis.scale = (0.24, 0.16, 0.08)
    bpy.ops.object.transform_apply(scale=True)
    bpy.ops.object.shade_smooth()
    m_pelvis.data.materials.append(mat_dark)
    assign_vertex_group(m_pelvis, "Torso")
    mesh_parts.append(m_pelvis)

    # =========================================================================
    # D. ARTICULATED ARMS & MECH HANDS
    # =========================================================================
    for side, x, s_mult in [("L", -0.24, 1), ("R", 0.24, -1)]:
        # Shoulder Armor Pad (White with Orange Trim)
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(x * 1.08, 0, 0.59))
        sh_pad = bpy.context.active_object
        sh_pad.name = f"Part_ShoulderPad_{side}"
        sh_pad.scale = (0.08, 0.14, 0.10)
        bpy.ops.object.transform_apply(scale=True)
        bpy.ops.object.shade_smooth()
        sh_pad.data.materials.append(mat_orange)
        assign_vertex_group(sh_pad, f"Arm.{side}")
        mesh_parts.append(sh_pad)

        # Upper Arm Strut
        bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.038, depth=0.16, location=(x * 1.25, 0.02, 0.50))
        u_arm = bpy.context.active_object
        u_arm.name = f"Part_UpperArm_{side}"
        u_arm.rotation_euler = (math.radians(12), math.radians(s_mult * 15), 0)
        bpy.ops.object.transform_apply(rotation=True)
        bpy.ops.object.shade_smooth()
        u_arm.data.materials.append(mat_white)
        assign_vertex_group(u_arm, f"Arm.{side}")
        mesh_parts.append(u_arm)

        # Elbow Joint Pivot
        bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=8, radius=0.045, location=(x * 1.40, 0.04, 0.40))
        elbow = bpy.context.active_object
        elbow.name = f"Part_Elbow_{side}"
        elbow.data.materials.append(mat_dark)
        assign_vertex_group(elbow, f"Arm.{side}")
        mesh_parts.append(elbow)

        # Forearm Cuff with White Shielding
        bpy.ops.mesh.primitive_cylinder_add(vertices=14, radius=0.046, depth=0.15, location=(x * 1.55, 0.06, 0.32))
        f_arm = bpy.context.active_object
        f_arm.name = f"Part_Forearm_{side}"
        f_arm.rotation_euler = (math.radians(15), math.radians(s_mult * 12), 0)
        bpy.ops.object.transform_apply(rotation=True)
        bpy.ops.object.shade_smooth()
        f_arm.data.materials.append(mat_white)
        assign_vertex_group(f_arm, f"Hand.{side}")
        mesh_parts.append(f_arm)

        # 3-Finger Robotic Grip Hand (Palm + Clamps)
        # Palm
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(x * 1.68, 0.08, 0.22))
        palm = bpy.context.active_object
        palm.name = f"Part_Palm_{side}"
        palm.scale = (0.06, 0.08, 0.07)
        bpy.ops.object.transform_apply(scale=True)
        bpy.ops.object.shade_smooth()
        palm.data.materials.append(mat_dark)
        assign_vertex_group(palm, f"Hand.{side}")
        mesh_parts.append(palm)

        # Fingers (stylized mitten clamp digits)
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(x * 1.70, 0.10, 0.17))
        fingers = bpy.context.active_object
        fingers.name = f"Part_Fingers_{side}"
        fingers.scale = (0.05, 0.07, 0.05)
        bpy.ops.object.transform_apply(scale=True)
        fingers.data.materials.append(mat_white)
        assign_vertex_group(fingers, f"Hand.{side}")
        mesh_parts.append(fingers)

    # =========================================================================
    # E. ARTICULATED LEGS & ANGULAR RUNNER SNEAKERS
    # =========================================================================
    for side, x in [("L", -0.15), ("R", 0.15)]:
        # Hip Ball Joint
        bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=8, radius=0.055, location=(x, 0, 0.32))
        hip = bpy.context.active_object
        hip.name = f"Part_Hip_{side}"
        hip.data.materials.append(mat_dark)
        assign_vertex_group(hip, f"Leg.{side}")
        mesh_parts.append(hip)

        # Thigh Strut
        bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.042, depth=0.14, location=(x, 0, 0.25))
        thigh = bpy.context.active_object
        thigh.name = f"Part_Thigh_{side}"
        bpy.ops.object.shade_smooth()
        thigh.data.materials.append(mat_white)
        assign_vertex_group(thigh, f"Leg.{side}")
        mesh_parts.append(thigh)

        # Knee Shock Absorber Ring
        bpy.ops.mesh.primitive_cylinder_add(vertices=14, radius=0.048, depth=0.04, location=(x, 0.01, 0.18))
        knee = bpy.context.active_object
        knee.name = f"Part_Knee_{side}"
        knee.data.materials.append(mat_orange)
        assign_vertex_group(knee, f"Leg.{side}")
        mesh_parts.append(knee)

        # Shin Piston
        bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.038, depth=0.10, location=(x, 0.01, 0.13))
        shin = bpy.context.active_object
        shin.name = f"Part_Shin_{side}"
        shin.data.materials.append(mat_dark)
        assign_vertex_group(shin, f"Foot.{side}")
        mesh_parts.append(shin)

        # High-Tech Runner Sneaker (White Shell)
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(x, 0.03, 0.065))
        boot = bpy.context.active_object
        boot.name = f"Part_Boot_{side}"
        boot.scale = (0.13, 0.22, 0.08)
        bpy.ops.object.transform_apply(scale=True)
        mod_bbev = boot.modifiers.new(name="Bevel", type='BEVEL')
        mod_bbev.width = 0.02
        mod_bbev.segments = 2
        bpy.ops.object.modifier_apply(modifier="Bevel")
        bpy.ops.object.shade_smooth()
        boot.data.materials.append(mat_white)
        assign_vertex_group(boot, f"Foot.{side}")
        mesh_parts.append(boot)

        # Dark Magnetic Sole Grip
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(x, 0.03, 0.015))
        sole = bpy.context.active_object
        sole.name = f"Part_Sole_{side}"
        sole.scale = (0.14, 0.23, 0.03)
        bpy.ops.object.transform_apply(scale=True)
        sole.data.materials.append(mat_dark)
        assign_vertex_group(sole, f"Foot.{side}")
        mesh_parts.append(sole)

        # Glowing Cyan Heel Energy Strip
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(x, -0.09, 0.05))
        heel_glow = bpy.context.active_object
        heel_glow.name = f"Part_HeelGlow_{side}"
        heel_glow.scale = (0.09, 0.02, 0.03)
        bpy.ops.object.transform_apply(scale=True)
        heel_glow.data.materials.append(mat_cyan_glow)
        assign_vertex_group(heel_glow, f"Foot.{side}")
        mesh_parts.append(heel_glow)

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

    # 5. Author Skeletal Animations Tailored to the New Anatomy
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
    # 25: curious head tilt left, hand raising
    keyframe_bone(p_head, 25, rot_deg=(6, -14, 14))
    keyframe_bone(p_ant_l, 25, rot_deg=(0, 0, 16))
    keyframe_bone(p_ant_r, 25, rot_deg=(0, 0, 16))
    keyframe_bone(p_arm_r, 25, rot_deg=(75, 0, -35))
    keyframe_bone(p_hand_r, 25, rot_deg=(0, 0, 25))
    # 35: hand wave right
    keyframe_bone(p_arm_r, 35, rot_deg=(78, 0, -20))
    keyframe_bone(p_hand_r, 35, rot_deg=(0, 0, -30))
    # 45: hand wave left
    keyframe_bone(p_arm_r, 45, rot_deg=(78, 0, -40))
    keyframe_bone(p_hand_r, 45, rot_deg=(0, 0, 30))
    # 55: head tilt right
    keyframe_bone(p_head, 55, rot_deg=(-4, 14, -12))
    keyframe_bone(p_ant_l, 55, rot_deg=(0, 0, -12))
    keyframe_bone(p_ant_r, 55, rot_deg=(0, 0, -12))
    keyframe_bone(p_arm_r, 55, rot_deg=(40, 0, -15))
    keyframe_bone(p_hand_r, 55, rot_deg=(0, 0, 0))
    # 90: return
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
        # Energetic athletic forward lean -14 deg
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

    # 6. Save Blender source
    blend_path = os.path.join(source_dir, "bot_character.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print(f"✓ Saved Blender source to: {blend_path}")

    # 7. Export GLB with Armature, Skins, and all 14 Actions
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
    print(f"✓ Exported new B.O.T GLB with 14 Actions to: {glb_char_path} & {glb_root_path}")

if __name__ == "__main__":
    build_new_bot_character()
    print("New B.O.T Character Redesign production complete!")
