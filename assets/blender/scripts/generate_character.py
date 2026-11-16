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

def build_bot_character():
    clean_scene()
    script_dir = os.path.dirname(os.path.abspath(__file__))
    source_dir = os.path.join(script_dir, "..", "source")
    char_model_dir = os.path.join(script_dir, "..", "..", "models", "characters")
    root_model_dir = os.path.join(script_dir, "..", "..", "models")
    os.makedirs(source_dir, exist_ok=True)
    os.makedirs(char_model_dir, exist_ok=True)

    # 1. Materials
    # Warm ivory porcelain ceramic
    mat_white = create_pbr_material("Mat_Bot_Porcelain", (0.95, 0.95, 0.97, 1.0), metallic=0.08, roughness=0.22)
    # Glossy dark reflective visor glass
    mat_visor = create_pbr_material("Mat_Bot_Visor", (0.03, 0.04, 0.06, 1.0), metallic=0.92, roughness=0.10)
    # Bright emissive cyan for eyes and energy details
    mat_cyan_glow = create_pbr_material("Mat_Bot_CyanGlow", (0.0, 0.95, 1.0, 1.0), metallic=0.0, roughness=0.2, emission=(0.0, 0.95, 1.0, 1.0), emission_strength=3.5)
    # Warm gold metallic accents
    mat_gold = create_pbr_material("Mat_Bot_Gold", (1.0, 0.82, 0.22, 1.0), metallic=0.85, roughness=0.25)
    # Dark titanium joints and boot soles
    mat_dark = create_pbr_material("Mat_Bot_Titanium", (0.18, 0.20, 0.24, 1.0), metallic=0.8, roughness=0.35)

    # 2. Armature Setup
    bpy.ops.object.armature_add(enter_editmode=True, align='WORLD', location=(0, 0, 0))
    arm_obj = bpy.context.active_object
    arm_obj.name = "BOT_Armature"
    arm_data = arm_obj.data
    arm_data.name = "BOT_ArmatureData"

    # Bone Definitions
    eb_root = arm_data.edit_bones['Bone']
    eb_root.name = 'Root'
    eb_root.head = (0, 0, 0)
    eb_root.tail = (0, 0, 0.15)

    create_bone(arm_data, 'Torso', 'Root', head=(0, 0, 0.28), tail=(0, 0, 0.68))
    create_bone(arm_data, 'Head', 'Torso', head=(0, 0, 0.68), tail=(0, 0, 0.98))
    create_bone(arm_data, 'Antenna.L', 'Head', head=(-0.09, 0, 0.98), tail=(-0.13, 0, 1.22))
    create_bone(arm_data, 'Antenna.R', 'Head', head=(0.09, 0, 0.98), tail=(0.13, 0, 1.22))

    create_bone(arm_data, 'Arm.L', 'Torso', head=(-0.40, 0.02, 0.58), tail=(-0.46, 0.05, 0.40))
    create_bone(arm_data, 'Hand.L', 'Arm.L', head=(-0.46, 0.05, 0.40), tail=(-0.50, 0.08, 0.26))

    create_bone(arm_data, 'Arm.R', 'Torso', head=(0.40, 0.02, 0.58), tail=(0.46, 0.05, 0.40))
    create_bone(arm_data, 'Hand.R', 'Arm.R', head=(0.46, 0.05, 0.40), tail=(0.50, 0.08, 0.26))

    create_bone(arm_data, 'Leg.L', 'Root', head=(-0.18, 0.0, 0.30), tail=(-0.18, 0.0, 0.15))
    create_bone(arm_data, 'Foot.L', 'Leg.L', head=(-0.18, 0.0, 0.15), tail=(-0.18, 0.15, 0.0))

    create_bone(arm_data, 'Leg.R', 'Root', head=(0.18, 0.0, 0.30), tail=(0.18, 0.0, 0.15))
    create_bone(arm_data, 'Foot.R', 'Leg.R', head=(0.18, 0.0, 0.15), tail=(0.18, 0.15, 0.0))

    bpy.ops.object.mode_set(mode='OBJECT')

    # 3. Model Meshes
    mesh_parts = []

    # --- Torso Group ---
    # Main Body: rounded egg capsule
    bpy.ops.mesh.primitive_uv_sphere_add(segments=28, ring_count=20, radius=0.46, location=(0, 0, 0.58))
    m_body = bpy.context.active_object
    m_body.name = "Part_Body"
    m_body.scale = (0.92, 0.88, 1.05)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    m_body.data.materials.append(mat_white)
    assign_vertex_group(m_body, "Torso")
    mesh_parts.append(m_body)

    # Chest Badge: embossed gold circle
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.10, depth=0.04, location=(0, 0.38, 0.45))
    m_badge = bpy.context.active_object
    m_badge.name = "Part_ChestBadge"
    m_badge.rotation_euler = (math.radians(72), 0, 0)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
    m_badge.data.materials.append(mat_gold)
    assign_vertex_group(m_badge, "Torso")
    mesh_parts.append(m_badge)

    # Chest Core: cyan glow
    bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=8, radius=0.045, location=(0, 0.40, 0.45))
    m_badge_core = bpy.context.active_object
    m_badge_core.name = "Part_ChestCore"
    m_badge_core.data.materials.append(mat_cyan_glow)
    assign_vertex_group(m_badge_core, "Torso")
    mesh_parts.append(m_badge_core)

    # Jetpack Body
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -0.36, 0.58))
    m_jetpack = bpy.context.active_object
    m_jetpack.name = "Part_Jetpack"
    m_jetpack.scale = (0.36, 0.16, 0.38)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    m_jetpack.data.materials.append(mat_white)
    assign_vertex_group(m_jetpack, "Torso")
    mesh_parts.append(m_jetpack)

    # Jetpack Cyan Core Cell
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.07, depth=0.22, location=(0, -0.44, 0.58))
    m_jet_core = bpy.context.active_object
    m_jet_core.name = "Part_JetCore"
    m_jet_core.rotation_euler = (math.radians(90), 0, 0)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
    m_jet_core.data.materials.append(mat_cyan_glow)
    assign_vertex_group(m_jet_core, "Torso")
    mesh_parts.append(m_jet_core)

    # Jetpack Thruster Nozzles
    for side, x in [("L", -0.12), ("R", 0.12)]:
        bpy.ops.mesh.primitive_cone_add(vertices=16, radius1=0.06, radius2=0.035, depth=0.10, location=(x, -0.38, 0.34))
        nozzle = bpy.context.active_object
        nozzle.name = f"Part_Nozzle_{side}"
        nozzle.rotation_euler = (math.radians(180), 0, 0)
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
        nozzle.data.materials.append(mat_gold)
        assign_vertex_group(nozzle, "Torso")
        mesh_parts.append(nozzle)

    # --- Head Group ---
    # Curved Visor
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=16, radius=0.26, location=(0, 0.27, 0.65))
    m_visor = bpy.context.active_object
    m_visor.name = "Part_Visor"
    m_visor.scale = (1.12, 0.52, 0.68)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    m_visor.data.materials.append(mat_visor)
    assign_vertex_group(m_visor, "Head")
    mesh_parts.append(m_visor)

    # Expressive Cyan Glowing Eyes
    for side, x, rot in [("L", -0.115, -5), ("R", 0.115, 5)]:
        bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=12, radius=0.055, location=(x, 0.38, 0.66))
        eye = bpy.context.active_object
        eye.name = f"Part_Eye_{side}"
        eye.scale = (1.0, 0.45, 1.25)
        eye.rotation_euler = (0, 0, math.radians(rot))
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
        eye.data.materials.append(mat_cyan_glow)
        assign_vertex_group(eye, "Head")
        mesh_parts.append(eye)

    # Ear Dials & Indicators
    for side, x, rot in [("L", -0.42, 90), ("R", 0.42, -90)]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.09, depth=0.05, location=(x, 0, 0.62))
        ear = bpy.context.active_object
        ear.name = f"Part_Ear_{side}"
        ear.rotation_euler = (0, math.radians(rot), 0)
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
        ear.data.materials.append(mat_gold)
        assign_vertex_group(ear, "Head")
        mesh_parts.append(ear)

        bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=8, radius=0.035, location=(x * 1.05, 0, 0.62))
        ear_dot = bpy.context.active_object
        ear_dot.name = f"Part_EarDot_{side}"
        ear_dot.data.materials.append(mat_cyan_glow)
        assign_vertex_group(ear_dot, "Head")
        mesh_parts.append(ear_dot)

    # --- Antenna Groups ---
    # Left Antenna Stem & Orb
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.018, depth=0.18, location=(-0.08, 0, 1.10))
    stem_l = bpy.context.active_object
    stem_l.name = "Part_Stem_L"
    stem_l.rotation_euler = (0, math.radians(-12), 0)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
    stem_l.data.materials.append(mat_dark)
    assign_vertex_group(stem_l, "Antenna.L")
    mesh_parts.append(stem_l)

    bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=12, radius=0.06, location=(-0.11, 0, 1.21))
    orb_l = bpy.context.active_object
    orb_l.name = "Part_Orb_L"
    orb_l.data.materials.append(mat_cyan_glow)
    assign_vertex_group(orb_l, "Antenna.L")
    mesh_parts.append(orb_l)

    # Right Antenna Stem & Orb
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.018, depth=0.18, location=(0.08, 0, 1.10))
    stem_r = bpy.context.active_object
    stem_r.name = "Part_Stem_R"
    stem_r.rotation_euler = (0, math.radians(12), 0)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
    stem_r.data.materials.append(mat_dark)
    assign_vertex_group(stem_r, "Antenna.R")
    mesh_parts.append(stem_r)

    bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=12, radius=0.06, location=(0.11, 0, 1.21))
    orb_r = bpy.context.active_object
    orb_r.name = "Part_Orb_R"
    orb_r.data.materials.append(mat_cyan_glow)
    assign_vertex_group(orb_r, "Antenna.R")
    mesh_parts.append(orb_r)

    # --- Arm & Hand Groups ---
    for side, x, s_mult in [("L", -0.42, 1), ("R", 0.42, -1)]:
        # Shoulder ball joint
        bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=8, radius=0.07, location=(x, 0.02, 0.52))
        shoulder = bpy.context.active_object
        shoulder.name = f"Part_Shoulder_{side}"
        shoulder.data.materials.append(mat_dark)
        assign_vertex_group(shoulder, f"Arm.{side}")
        mesh_parts.append(shoulder)

        # Upper arm
        bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.045, depth=0.18, location=(x * 1.10, 0.04, 0.40))
        arm_mesh = bpy.context.active_object
        arm_mesh.name = f"Part_Arm_{side}"
        arm_mesh.rotation_euler = (math.radians(15), math.radians(s_mult * 18), 0)
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
        arm_mesh.data.materials.append(mat_white)
        assign_vertex_group(arm_mesh, f"Arm.{side}")
        mesh_parts.append(arm_mesh)

        # Rounded mitten hand
        bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=12, radius=0.075, location=(x * 1.18, 0.08, 0.28))
        hand = bpy.context.active_object
        hand.name = f"Part_Hand_{side}"
        hand.scale = (0.85, 1.0, 1.1)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        hand.data.materials.append(mat_white)
        assign_vertex_group(hand, f"Hand.{side}")
        mesh_parts.append(hand)

    # --- Leg & Foot Groups ---
    for side, x in [("L", -0.19), ("R", 0.19)]:
        # Hip ball joint
        bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=8, radius=0.065, location=(x, 0, 0.22))
        hip = bpy.context.active_object
        hip.name = f"Part_Hip_{side}"
        hip.data.materials.append(mat_dark)
        assign_vertex_group(hip, f"Leg.{side}")
        mesh_parts.append(hip)

        # Foot Porcelain Dome
        bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=12, radius=0.13, location=(x, 0.03, 0.13))
        foot = bpy.context.active_object
        foot.name = f"Part_Foot_{side}"
        foot.scale = (0.88, 1.28, 0.65)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        foot.data.materials.append(mat_white)
        assign_vertex_group(foot, f"Foot.{side}")
        mesh_parts.append(foot)

        # Magnetic Sole
        bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.12, depth=0.03, location=(x, 0.03, 0.035))
        sole = bpy.context.active_object
        sole.name = f"Part_Sole_{side}"
        sole.scale = (0.85, 1.25, 1.0)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        sole.data.materials.append(mat_dark)
        assign_vertex_group(sole, f"Foot.{side}")
        mesh_parts.append(sole)

        # Cyan Heel Glow Strip
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(x, -0.09, 0.07))
        glow_strip = bpy.context.active_object
        glow_strip.name = f"Part_HeelGlow_{side}"
        glow_strip.scale = (0.08, 0.025, 0.03)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        glow_strip.data.materials.append(mat_cyan_glow)
        assign_vertex_group(glow_strip, f"Foot.{side}")
        mesh_parts.append(glow_strip)

    # 4. Join all mesh parts into unified skinned mesh
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

    # 5. Author Skeletal Animations
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
        # Reset all bones to neutral
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
    for frame, bob, ant_rot in [(1, 0.0, 0.0), (30, 0.025, -4.0), (60, 0.0, 0.0)]:
        keyframe_bone(p_torso, frame, loc=(0, 0, bob), rot_deg=(0, 0, 0))
        keyframe_bone(p_head, frame, rot_deg=(bob * 40.0, 0, 0))
        keyframe_bone(p_ant_l, frame, rot_deg=(ant_rot, 0, -ant_rot * 0.5))
        keyframe_bone(p_ant_r, frame, rot_deg=(ant_rot, 0, ant_rot * 0.5))
        keyframe_bone(p_arm_l, frame, rot_deg=(bob * -20.0, 0, 2.0))
        keyframe_bone(p_arm_r, frame, rot_deg=(bob * -20.0, 0, -2.0))
        keyframe_bone(p_leg_l, frame, rot_deg=(0, 0, 0))
        keyframe_bone(p_leg_r, frame, rot_deg=(0, 0, 0))
        keyframe_bone(p_foot_l, frame, rot_deg=(0, 0, 0))
        keyframe_bone(p_foot_r, frame, rot_deg=(0, 0, 0))
    push_to_nla(act_idle)

    # --- 2. Idle_Secondary (90 frames / 3.0s) ---
    act_idle_sec = create_action("Idle_Secondary")
    # 1: neutral
    keyframe_bone(p_torso, 1, loc=(0, 0, 0), rot_deg=(0, 0, 0))
    keyframe_bone(p_head, 1, rot_deg=(0, 0, 0))
    keyframe_bone(p_arm_r, 1, rot_deg=(0, 0, 0))
    keyframe_bone(p_hand_r, 1, rot_deg=(0, 0, 0))
    # 25: curious head tilt left, hand raising
    keyframe_bone(p_head, 25, rot_deg=(5, -15, 12))
    keyframe_bone(p_ant_l, 25, rot_deg=(0, 0, 15))
    keyframe_bone(p_ant_r, 25, rot_deg=(0, 0, 15))
    keyframe_bone(p_arm_r, 25, rot_deg=(70, 0, -35))
    keyframe_bone(p_hand_r, 25, rot_deg=(0, 0, 20))
    # 35: hand wave right
    keyframe_bone(p_arm_r, 35, rot_deg=(75, 0, -20))
    keyframe_bone(p_hand_r, 35, rot_deg=(0, 0, -25))
    # 45: hand wave left
    keyframe_bone(p_arm_r, 45, rot_deg=(75, 0, -40))
    keyframe_bone(p_hand_r, 45, rot_deg=(0, 0, 25))
    # 55: head tilt right
    keyframe_bone(p_head, 55, rot_deg=(-4, 15, -10))
    keyframe_bone(p_ant_l, 55, rot_deg=(0, 0, -10))
    keyframe_bone(p_ant_r, 55, rot_deg=(0, 0, -10))
    keyframe_bone(p_arm_r, 55, rot_deg=(40, 0, -15))
    keyframe_bone(p_hand_r, 55, rot_deg=(0, 0, 0))
    # 90: return to neutral
    keyframe_bone(p_torso, 90, loc=(0, 0, 0), rot_deg=(0, 0, 0))
    keyframe_bone(p_head, 90, rot_deg=(0, 0, 0))
    keyframe_bone(p_ant_l, 90, rot_deg=(0, 0, 0))
    keyframe_bone(p_ant_r, 90, rot_deg=(0, 0, 0))
    keyframe_bone(p_arm_r, 90, rot_deg=(0, 0, 0))
    keyframe_bone(p_hand_r, 90, rot_deg=(0, 0, 0))
    push_to_nla(act_idle_sec)

    # --- 3. Walk (30 frames / 1.0s loop) ---
    act_walk = create_action("Walk")
    # Stride phases at 1, 8, 15, 23, 30
    walk_keys = [
        # frame, torso_z, torso_yaw, l_rot, l_pos_z, r_rot, r_pos_z, arm_l, arm_r
        (1,  0.0,   -3,  25, 0.0,   -25, 0.0,   -25,  25),
        (8,  0.025,  0,   0, 0.0,     0, 0.07,    0,   0),
        (15, 0.0,    3, -25, 0.0,    25, 0.0,    25, -25),
        (23, 0.025,  0,   0, 0.07,    0, 0.0,     0,   0),
        (30, 0.0,   -3,  25, 0.0,   -25, 0.0,   -25,  25)
    ]
    for frame, tz, tyaw, l_rot, l_pz, r_rot, r_pz, al, ar in walk_keys:
        keyframe_bone(p_torso, frame, loc=(0, 0, tz), rot_deg=(2, tyaw, -tyaw * 0.5))
        keyframe_bone(p_head, frame, rot_deg=(0, -tyaw * 0.8, 0))
        keyframe_bone(p_ant_l, frame, rot_deg=(al * 0.3, 0, -tyaw))
        keyframe_bone(p_ant_r, frame, rot_deg=(ar * 0.3, 0, -tyaw))
        keyframe_bone(p_arm_l, frame, rot_deg=(al, 0, 5))
        keyframe_bone(p_arm_r, frame, rot_deg=(ar, 0, -5))
        keyframe_bone(p_leg_l, frame, loc=(0, 0, l_pz), rot_deg=(l_rot, 0, 0))
        keyframe_bone(p_leg_r, frame, loc=(0, 0, r_pz), rot_deg=(r_rot, 0, 0))
        keyframe_bone(p_foot_l, frame, rot_deg=(-l_rot * 0.4, 0, 0))
        keyframe_bone(p_foot_r, frame, rot_deg=(-r_rot * 0.4, 0, 0))
    push_to_nla(act_walk)

    # --- 4. Run (20 frames / 0.67s loop) ---
    act_run = create_action("Run")
    run_keys = [
        (1,  0.01,  -6,  42, 0.0,   -42, 0.0,   -45,  45),
        (5,  0.045,  0,   0, 0.0,     0, 0.12,    0,   0),
        (10, 0.01,   6, -42, 0.0,    42, 0.0,    45, -45),
        (15, 0.045,  0,   0, 0.12,    0, 0.0,     0,   0),
        (20, 0.01,  -6,  42, 0.0,   -42, 0.0,   -45,  45)
    ]
    for frame, tz, tyaw, l_rot, l_pz, r_rot, r_pz, al, ar in run_keys:
        # Energetic forward lean -12 deg
        keyframe_bone(p_torso, frame, loc=(0, 0, tz), rot_deg=(-12, tyaw, -tyaw * 0.6))
        keyframe_bone(p_head, frame, rot_deg=(8, -tyaw * 0.5, 0))
        keyframe_bone(p_ant_l, frame, rot_deg=(-18, 0, -tyaw * 1.5))
        keyframe_bone(p_ant_r, frame, rot_deg=(-18, 0, -tyaw * 1.5))
        keyframe_bone(p_arm_l, frame, rot_deg=(al, 0, 10))
        keyframe_bone(p_arm_r, frame, rot_deg=(ar, 0, -10))
        keyframe_bone(p_leg_l, frame, loc=(0, 0, l_pz), rot_deg=(l_rot, 0, 0))
        keyframe_bone(p_leg_r, frame, loc=(0, 0, r_pz), rot_deg=(r_rot, 0, 0))
        keyframe_bone(p_foot_l, frame, rot_deg=(-l_rot * 0.5, 0, 0))
        keyframe_bone(p_foot_r, frame, rot_deg=(-r_rot * 0.5, 0, 0))
    push_to_nla(act_run)

    # --- 5. Jump_Start (10 frames / 0.33s) ---
    act_jump_start = create_action("Jump_Start")
    # 1: neutral
    keyframe_bone(p_torso, 1, loc=(0, 0, 0), rot_deg=(0, 0, 0))
    # 4: anticipation crouch
    keyframe_bone(p_torso, 4, loc=(0, 0, -0.09), rot_deg=(-6, 0, 0))
    keyframe_bone(p_head, 4, rot_deg=(10, 0, 0))
    keyframe_bone(p_ant_l, 4, rot_deg=(-15, 0, 0))
    keyframe_bone(p_ant_r, 4, rot_deg=(-15, 0, 0))
    keyframe_bone(p_arm_l, 4, rot_deg=(-35, 0, 15))
    keyframe_bone(p_arm_r, 4, rot_deg=(-35, 0, -15))
    keyframe_bone(p_leg_l, 4, rot_deg=(-15, 0, 0))
    keyframe_bone(p_leg_r, 4, rot_deg=(-15, 0, 0))
    # 10: explosive launch extension
    keyframe_bone(p_torso, 10, loc=(0, 0, 0.12), rot_deg=(12, 0, 0))
    keyframe_bone(p_head, 10, rot_deg=(-8, 0, 0))
    keyframe_bone(p_ant_l, 10, rot_deg=(25, 0, 0))
    keyframe_bone(p_ant_r, 10, rot_deg=(25, 0, 0))
    keyframe_bone(p_arm_l, 10, rot_deg=(65, 0, 20))
    keyframe_bone(p_arm_r, 10, rot_deg=(65, 0, -20))
    keyframe_bone(p_leg_l, 10, rot_deg=(20, 0, 0))
    keyframe_bone(p_leg_r, 10, rot_deg=(20, 0, 0))
    push_to_nla(act_jump_start)

    # --- 6. Jump_Loop (20 frames / 0.67s loop) ---
    act_jump_loop = create_action("Jump_Loop")
    for frame, float_y in [(1, 0.06), (10, 0.08), (20, 0.06)]:
        keyframe_bone(p_torso, frame, loc=(0, 0, float_y), rot_deg=(5, 0, 0))
        keyframe_bone(p_head, frame, rot_deg=(-4, 0, 0))
        keyframe_bone(p_ant_l, frame, rot_deg=(-10, 0, -5))
        keyframe_bone(p_ant_r, frame, rot_deg=(-10, 0, 5))
        keyframe_bone(p_arm_l, frame, rot_deg=(35, 0, 30))
        keyframe_bone(p_arm_r, frame, rot_deg=(35, 0, -30))
        keyframe_bone(p_leg_l, frame, rot_deg=(-12, 0, 0))
        keyframe_bone(p_leg_r, frame, rot_deg=(-12, 0, 0))
        keyframe_bone(p_foot_l, frame, rot_deg=(25, 0, 0))
        keyframe_bone(p_foot_r, frame, rot_deg=(25, 0, 0))
    push_to_nla(act_jump_loop)

    # --- 7. Fall (20 frames / 0.67s loop) ---
    act_fall = create_action("Fall")
    # Descending flail motion
    for frame, flail in [(1, 0), (10, 1), (20, 0)]:
        deg_flail = 15 if flail == 1 else -15
        keyframe_bone(p_torso, frame, loc=(0, 0, 0), rot_deg=(10, 0, 0))
        keyframe_bone(p_head, frame, rot_deg=(-8, 0, 0))
        keyframe_bone(p_ant_l, frame, rot_deg=(20, 0, 10))
        keyframe_bone(p_ant_r, frame, rot_deg=(20, 0, -10))
        keyframe_bone(p_arm_l, frame, rot_deg=(55 + deg_flail, 0, 35))
        keyframe_bone(p_arm_r, frame, rot_deg=(55 - deg_flail, 0, -35))
        keyframe_bone(p_leg_l, frame, rot_deg=(15 - deg_flail * 0.5, 0, 5))
        keyframe_bone(p_leg_r, frame, rot_deg=(15 + deg_flail * 0.5, 0, -5))
        keyframe_bone(p_foot_l, frame, rot_deg=(-20, 0, 0))
        keyframe_bone(p_foot_r, frame, rot_deg=(-20, 0, 0))
    push_to_nla(act_fall)

    # --- 8. Landing (15 frames / 0.5s) ---
    act_landing = create_action("Landing")
    # 1: touchdown
    keyframe_bone(p_torso, 1, loc=(0, 0, 0), rot_deg=(0, 0, 0))
    # 4: deep squash compression
    keyframe_bone(p_torso, 4, loc=(0, 0, -0.12), rot_deg=(-5, 0, 0))
    keyframe_bone(p_head, 4, rot_deg=(8, 0, 0))
    keyframe_bone(p_ant_l, 4, rot_deg=(22, 0, 0))
    keyframe_bone(p_ant_r, 4, rot_deg=(22, 0, 0))
    keyframe_bone(p_arm_l, 4, rot_deg=(-25, 0, 35))
    keyframe_bone(p_arm_r, 4, rot_deg=(-25, 0, -35))
    keyframe_bone(p_leg_l, 4, rot_deg=(-20, 0, 0))
    keyframe_bone(p_leg_r, 4, rot_deg=(-20, 0, 0))
    # 9: rebound stretch
    keyframe_bone(p_torso, 9, loc=(0, 0, 0.04), rot_deg=(2, 0, 0))
    keyframe_bone(p_head, 9, rot_deg=(-3, 0, 0))
    keyframe_bone(p_ant_l, 9, rot_deg=(-10, 0, 0))
    keyframe_bone(p_ant_r, 9, rot_deg=(-10, 0, 0))
    keyframe_bone(p_arm_l, 9, rot_deg=(15, 0, 10))
    keyframe_bone(p_arm_r, 9, rot_deg=(15, 0, -10))
    # 15: neutral
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
    keyframe_bone(p_torso, 5, rot_deg=(2, 18, 10))
    keyframe_bone(p_head, 5, rot_deg=(0, 28, 8))
    keyframe_bone(p_ant_l, 5, rot_deg=(0, 0, 18))
    keyframe_bone(p_ant_r, 5, rot_deg=(0, 0, 18))
    keyframe_bone(p_arm_l, 5, rot_deg=(-20, 0, 15))
    keyframe_bone(p_arm_r, 5, rot_deg=(25, 0, -15))
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
    keyframe_bone(p_torso, 5, rot_deg=(2, -18, -10))
    keyframe_bone(p_head, 5, rot_deg=(0, -28, -8))
    keyframe_bone(p_ant_l, 5, rot_deg=(0, 0, -18))
    keyframe_bone(p_ant_r, 5, rot_deg=(0, 0, -18))
    keyframe_bone(p_arm_l, 5, rot_deg=(25, 0, 15))
    keyframe_bone(p_arm_r, 5, rot_deg=(-20, 0, -15))
    keyframe_bone(p_torso, 12, rot_deg=(0, 0, 0))
    keyframe_bone(p_head, 12, rot_deg=(0, 0, 0))
    keyframe_bone(p_ant_l, 12, rot_deg=(0, 0, 0))
    keyframe_bone(p_ant_r, 12, rot_deg=(0, 0, 0))
    keyframe_bone(p_arm_l, 12, rot_deg=(0, 0, 0))
    keyframe_bone(p_arm_r, 12, rot_deg=(0, 0, 0))
    push_to_nla(act_turn_r)

    # --- 11. Collect (24 frames / 0.8s) ---
    act_collect = create_action("Collect")
    # 1: neutral
    keyframe_bone(p_torso, 1, loc=(0, 0, 0), rot_deg=(0, 0, 0))
    # 5: crouch
    keyframe_bone(p_torso, 5, loc=(0, 0, -0.06), rot_deg=(0, 0, 0))
    # 12: joyous double fist pump jump!
    keyframe_bone(p_torso, 12, loc=(0, 0, 0.16), rot_deg=(-8, 0, 0))
    keyframe_bone(p_head, 12, rot_deg=(-18, 0, 0))
    keyframe_bone(p_ant_l, 12, rot_deg=(15, 0, -12))
    keyframe_bone(p_ant_r, 12, rot_deg=(15, 0, 12))
    keyframe_bone(p_arm_l, 12, rot_deg=(95, 0, 30))
    keyframe_bone(p_arm_r, 12, rot_deg=(95, 0, -30))
    keyframe_bone(p_hand_l, 12, rot_deg=(25, 0, 0))
    keyframe_bone(p_hand_r, 12, rot_deg=(25, 0, 0))
    keyframe_bone(p_leg_l, 12, rot_deg=(15, 0, 0))
    keyframe_bone(p_leg_r, 12, rot_deg=(15, 0, 0))
    # 18: land
    keyframe_bone(p_torso, 18, loc=(0, 0, -0.04), rot_deg=(0, 0, 0))
    keyframe_bone(p_arm_l, 18, rot_deg=(30, 0, 10))
    keyframe_bone(p_arm_r, 18, rot_deg=(30, 0, -10))
    # 24: return
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
    # 1: neutral
    keyframe_bone(p_torso, 1, rot_deg=(0, 0, 0))
    # 6: step forward lean
    keyframe_bone(p_torso, 6, rot_deg=(-8, 0, 0))
    keyframe_bone(p_head, 6, rot_deg=(10, 0, 0))
    # 12: reach right hand forward to press switch
    keyframe_bone(p_torso, 12, rot_deg=(-12, 5, 0))
    keyframe_bone(p_head, 12, rot_deg=(14, 0, 0))
    keyframe_bone(p_arm_r, 12, rot_deg=(85, 0, -10))
    keyframe_bone(p_hand_r, 12, rot_deg=(25, 0, 0))
    # 16: tap press pulse
    keyframe_bone(p_arm_r, 16, rot_deg=(92, 0, -8))
    keyframe_bone(p_head, 16, rot_deg=(18, 0, 0))
    # 24: return
    keyframe_bone(p_torso, 24, rot_deg=(0, 0, 0))
    keyframe_bone(p_head, 24, rot_deg=(0, 0, 0))
    keyframe_bone(p_arm_r, 24, rot_deg=(0, 0, 0))
    keyframe_bone(p_hand_r, 24, rot_deg=(0, 0, 0))
    push_to_nla(act_interact)

    # --- 13. Victory (75 frames / 2.5s) ---
    act_victory = create_action("Victory")
    # 1: start
    keyframe_bone(p_torso, 1, loc=(0, 0, 0), rot_deg=(0, 0, 0))
    # 10: spin 180 deg
    keyframe_bone(p_torso, 10, loc=(0, 0, 0.10), rot_deg=(0, 180, 0))
    keyframe_bone(p_arm_l, 10, rot_deg=(45, 0, 45))
    keyframe_bone(p_arm_r, 10, rot_deg=(45, 0, -45))
    # 20: spin 360 deg
    keyframe_bone(p_torso, 20, loc=(0, 0, 0.0), rot_deg=(0, 360, 0))
    # 30: celebratory hop 1
    keyframe_bone(p_torso, 30, loc=(0, 0, 0.18), rot_deg=(-5, 360, 0))
    keyframe_bone(p_arm_l, 30, rot_deg=(85, 0, 35))
    keyframe_bone(p_arm_r, 30, rot_deg=(85, 0, -35))
    # 40: land
    keyframe_bone(p_torso, 40, loc=(0, 0, -0.04), rot_deg=(0, 360, 0))
    # 50: celebratory hop 2
    keyframe_bone(p_torso, 50, loc=(0, 0, 0.18), rot_deg=(-5, 360, 0))
    keyframe_bone(p_head, 50, rot_deg=(-15, 0, 10))
    keyframe_bone(p_arm_l, 50, rot_deg=(95, 0, 40))
    keyframe_bone(p_arm_r, 50, rot_deg=(95, 0, -40))
    # 60: side-to-side cute sway
    keyframe_bone(p_torso, 60, loc=(0, 0, 0), rot_deg=(0, 360, 12))
    keyframe_bone(p_head, 60, rot_deg=(0, 0, -10))
    # 75: final hero freeze pose waving to player!
    keyframe_bone(p_torso, 75, loc=(0, 0, 0), rot_deg=(0, 360, -8))
    keyframe_bone(p_head, 75, rot_deg=(-5, 0, 12))
    keyframe_bone(p_ant_l, 75, rot_deg=(0, 0, 15))
    keyframe_bone(p_ant_r, 75, rot_deg=(0, 0, 15))
    keyframe_bone(p_arm_r, 75, rot_deg=(-20, 0, -25)) # right hand on hip
    keyframe_bone(p_hand_r, 75, rot_deg=(40, 0, 0))
    keyframe_bone(p_arm_l, 75, rot_deg=(75, 0, 30))   # left hand waving
    keyframe_bone(p_hand_l, 75, rot_deg=(0, 0, 20))
    push_to_nla(act_victory)

    # --- 14. Respawn (30 frames / 1.0s) ---
    act_respawn = create_action("Respawn")
    # 1: compact crouch reboot
    keyframe_bone(p_torso, 1, loc=(0, 0, -0.12), rot_deg=(15, 0, 0))
    keyframe_bone(p_head, 1, rot_deg=(25, 0, 0))
    keyframe_bone(p_ant_l, 1, rot_deg=(-25, 0, -10))
    keyframe_bone(p_ant_r, 1, rot_deg=(-25, 0, 10))
    keyframe_bone(p_arm_l, 1, rot_deg=(-20, 0, 10))
    keyframe_bone(p_arm_r, 1, rot_deg=(-20, 0, -10))
    # 10: system boot head snaps up
    keyframe_bone(p_torso, 10, loc=(0, 0, -0.06), rot_deg=(-5, 0, 0))
    keyframe_bone(p_head, 10, rot_deg=(-15, 0, 0))
    keyframe_bone(p_ant_l, 10, rot_deg=(25, 0, 15))
    keyframe_bone(p_ant_r, 10, rot_deg=(25, 0, -15))
    # 18: shake off dust
    keyframe_bone(p_torso, 18, loc=(0, 0, 0), rot_deg=(0, 20, 5))
    keyframe_bone(p_head, 18, rot_deg=(0, -25, 0))
    # 24: shake opposite
    keyframe_bone(p_torso, 24, loc=(0, 0, 0), rot_deg=(0, -20, -5))
    keyframe_bone(p_head, 24, rot_deg=(0, 25, 0))
    # 30: fully alert & ready!
    keyframe_bone(p_torso, 30, loc=(0, 0, 0), rot_deg=(0, 0, 0))
    keyframe_bone(p_head, 30, rot_deg=(0, 0, 0))
    keyframe_bone(p_ant_l, 30, rot_deg=(0, 0, 0))
    keyframe_bone(p_ant_r, 30, rot_deg=(0, 0, 0))
    keyframe_bone(p_arm_l, 30, rot_deg=(0, 0, 0))
    keyframe_bone(p_arm_r, 30, rot_deg=(0, 0, 0))
    push_to_nla(act_respawn)

    bpy.ops.object.mode_set(mode='OBJECT')

    # 6. Save source .blend file
    blend_path = os.path.join(source_dir, "bot_character.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print(f"✓ Saved Blender source to: {blend_path}")

    # 7. Export GLB with Armature, Skins, and all 14 Actions
    glb_char_path = os.path.join(char_model_dir, "bot.glb")
    glb_root_path = os.path.join(root_model_dir, "bot.glb")
    
    # Export options ensuring single armature and all actions
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
    
    # Also copy to root models for backward compatibility
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
    print(f"✓ Exported GLB with 14 Actions to: {glb_char_path} and {glb_root_path}")

if __name__ == "__main__":
    build_bot_character()
    print("B.O.T character generation with skeletal rigging and 14 actions complete!")
