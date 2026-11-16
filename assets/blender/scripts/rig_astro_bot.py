import bpy
import mathutils
from mathutils import Matrix, Quaternion, Vector
import math
import os
import shutil

print("=== Starting Rigging Pipeline for Astro Bot Model ===")

SOURCE_GLB = "/Users/it/Downloads/ef0c833b-978c-4029-a406-95e89e04ec94/base_basic_pbr.glb"
OUTPUT_BLEND = "/Users/it/Documents/TINY PLANET/assets/blender/source/bot_rigged_astro.blend"
CANONICAL_BLEND_1 = "/Users/it/Documents/TINY PLANET/assets/blender/source/bot.blend"
CANONICAL_BLEND_2 = "/Users/it/Documents/TINY PLANET/assets/blender/source/bot_character.blend"

EXPORT_GLB_TARGETS = [
    "/Users/it/Documents/TINY PLANET/assets/models/character/bot.glb",
    "/Users/it/Documents/TINY PLANET/assets/models/characters/bot.glb",
    "/Users/it/Documents/TINY PLANET/assets/models/bot.glb"
]

# 1. Reset Scene & Import Model
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=SOURCE_GLB)

model = bpy.data.objects.get("model")
assert model is not None, "Failed to load model from GLB"
bpy.context.view_layer.objects.active = model
model.name = "BOT_Mesh"

# 2. Decimate Mesh for WebGL Performance (from ~93k to ~26k polygons)
print(f"Original polygon count: {len(model.data.polygons)}")
dec_mod = model.modifiers.new("Decimate", "DECIMATE")
dec_mod.ratio = 0.28
bpy.ops.object.modifier_apply(modifier="Decimate")
print(f"Decimated polygon count: {len(model.data.polygons)} ({len(model.data.vertices)} vertices)")

# 3. Scale, Align to Ground (Z=0) & Center
# Model is height 1.9056m in T-pose. Target height is 0.92m to match Godot player capsule.
TARGET_HEIGHT = 0.92
orig_height = 1.9056
scale_fac = TARGET_HEIGHT / orig_height

bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
model.scale = (scale_fac, scale_fac, scale_fac)
bpy.ops.object.transform_apply(scale=True)

bbox = [mathutils.Vector(c) for c in model.bound_box]
min_z = min(v.z for v in bbox)
model.location.z = -min_z
bpy.ops.object.transform_apply(location=True)

print(f"Rescaled dimensions: {model.dimensions}")

# 4. Create 13-Bone Deformation Armature
arm_data = bpy.data.armatures.new("Armature")
arm_obj = bpy.data.objects.new("BOT_Armature", arm_data)
bpy.context.collection.objects.link(arm_obj)
bpy.context.view_layer.objects.active = arm_obj
bpy.ops.object.mode_set(mode='EDIT')

eb = arm_data.edit_bones

# 1. Root
b_root = eb.new("Root")
b_root.head = (0, 0, 0)
b_root.tail = (0, 0, 0.35)

# 2. Torso
b_torso = eb.new("Torso")
b_torso.head = (0, 0, 0.35)
b_torso.tail = (0, 0, 0.55)
b_torso.parent = b_root

# 3. Head
b_head = eb.new("Head")
b_head.head = (0, 0, 0.55)
b_head.tail = (0, 0, 0.85)
b_head.parent = b_torso

# 4 & 5. Antenna.L & Antenna.R
b_ant_l = eb.new("Antenna.L")
b_ant_l.head = (-0.03, 0.0, 0.85)
b_ant_l.tail = (-0.05, 0.02, 0.92)
b_ant_l.parent = b_head

b_ant_r = eb.new("Antenna.R")
b_ant_r.head = (0.03, 0.0, 0.85)
b_ant_r.tail = (0.05, 0.02, 0.92)
b_ant_r.parent = b_head

# 6 & 7. Arm.L & Hand.L (T-Pose along +X)
b_arm_l = eb.new("Arm.L")
b_arm_l.head = (0.13, 0.0, 0.52)
b_arm_l.tail = (0.26, 0.0, 0.52)
b_arm_l.parent = b_torso

b_hand_l = eb.new("Hand.L")
b_hand_l.head = (0.26, 0.0, 0.52)
b_hand_l.tail = (0.41, 0.0, 0.52)
b_hand_l.parent = b_arm_l

# 8 & 9. Arm.R & Hand.R (T-Pose along -X)
b_arm_r = eb.new("Arm.R")
b_arm_r.head = (-0.13, 0.0, 0.52)
b_arm_r.tail = (-0.26, 0.0, 0.52)
b_arm_r.parent = b_torso

b_hand_r = eb.new("Hand.R")
b_hand_r.head = (-0.26, 0.0, 0.52)
b_hand_r.tail = (-0.41, 0.0, 0.52)
b_hand_r.parent = b_arm_r

# 10 & 11. Leg.L & Foot.L
b_leg_l = eb.new("Leg.L")
b_leg_l.head = (0.095, 0.0, 0.32)
b_leg_l.tail = (0.095, 0.0, 0.15)
b_leg_l.parent = b_root

b_foot_l = eb.new("Foot.L")
b_foot_l.head = (0.095, 0.0, 0.15)
b_foot_l.tail = (0.095, -0.06, 0.02)
b_foot_l.parent = b_leg_l

# 12 & 13. Leg.R & Foot.R
b_leg_r = eb.new("Leg.R")
b_leg_r.head = (-0.095, 0.0, 0.32)
b_leg_r.tail = (-0.095, 0.0, 0.15)
b_leg_r.parent = b_root

b_foot_r = eb.new("Foot.R")
b_foot_r.head = (-0.095, 0.0, 0.15)
b_foot_r.tail = (-0.095, -0.06, 0.02)
b_foot_r.parent = b_leg_r

bpy.ops.object.mode_set(mode='OBJECT')

# 5. Skin Weight Assignment
bone_names = [b.name for b in arm_data.bones]
vgroups = {name: model.vertex_groups.new(name=name) for name in bone_names}

num_verts = len(model.data.vertices)
vert_weights = [{} for _ in range(num_verts)]

for idx, v in enumerate(model.data.vertices):
    x, y, z = v.co
    w = {}
    
    if z >= 0.55 and abs(x) <= 0.25:
        if z >= 0.84:
            w['Head'] = 0.60
            w['Antenna.L'] = 0.20
            w['Antenna.R'] = 0.20
        else:
            if z < 0.60:
                t = (z - 0.55) / 0.05
                w['Head'] = t
                w['Torso'] = 1.0 - t
            else:
                w['Head'] = 1.0
    elif x >= 0.13 and 0.36 <= z <= 0.64:
        if x >= 0.26:
            w['Hand.L'] = 0.90
            w['Arm.L'] = 0.10
        else:
            t = (x - 0.13) / 0.13
            w['Arm.L'] = 0.20 + 0.80 * t
            w['Torso'] = 0.80 * (1.0 - t)
    elif x <= -0.13 and 0.36 <= z <= 0.64:
        if x <= -0.26:
            w['Hand.R'] = 0.90
            w['Arm.R'] = 0.10
        else:
            t = (-x - 0.13) / 0.13
            w['Arm.R'] = 0.20 + 0.80 * t
            w['Torso'] = 0.80 * (1.0 - t)
    elif 0.32 <= z < 0.55 and abs(x) < 0.16:
        t = (z - 0.32) / 0.23
        w['Torso'] = 0.20 + 0.80 * t
        w['Root'] = 0.80 * (1.0 - t)
    elif z < 0.32 and x >= 0.0:
        if z <= 0.14:
            w['Foot.L'] = 0.95
            w['Leg.L'] = 0.05
        else:
            t = (z - 0.14) / 0.18
            w['Leg.L'] = 0.90 - 0.40 * t
            w['Root'] = 0.10 + 0.40 * t
    elif z < 0.32 and x < 0.0:
        if z <= 0.14:
            w['Foot.R'] = 0.95
            w['Leg.R'] = 0.05
        else:
            t = (z - 0.14) / 0.18
            w['Leg.R'] = 0.90 - 0.40 * t
            w['Root'] = 0.10 + 0.40 * t
    else:
        w['Root'] = 1.0

    tot = sum(w.values())
    vert_weights[idx] = {k: v_val / tot for k, v_val in w.items()}

# Laplacian smoothing of vertex weights across edge neighbors (2 passes)
adj = [[] for _ in range(num_verts)]
for edge in model.data.edges:
    adj[edge.vertices[0]].append(edge.vertices[1])
    adj[edge.vertices[1]].append(edge.vertices[0])

for _ in range(2):
    smoothed_weights = [{} for _ in range(num_verts)]
    for i in range(num_verts):
        cur_w = vert_weights[i]
        neighbors = adj[i]
        if not neighbors:
            smoothed_weights[i] = cur_w
            continue
        
        # Accumulate neighbor weights
        all_keys = set(cur_w.keys())
        for n in neighbors:
            all_keys.update(vert_weights[n].keys())
        
        n_count = len(neighbors)
        new_w = {}
        for k in all_keys:
            c_val = cur_w.get(k, 0.0)
            avg_neigh = sum(vert_weights[n].get(k, 0.0) for n in neighbors) / n_count
            new_w[k] = 0.65 * c_val + 0.35 * avg_neigh
            
        tot = sum(new_w.values())
        if tot > 0:
            smoothed_weights[i] = {k: v_val / tot for k, v_val in new_w.items() if (v_val / tot) >= 0.02}
        else:
            smoothed_weights[i] = {'Root': 1.0}
    vert_weights = smoothed_weights

# Populate vertex groups
for i in range(num_verts):
    tot = sum(vert_weights[i].values())
    for bname, weight in vert_weights[i].items():
        vgroups[bname].add([i], weight / tot, 'REPLACE')

model.parent = arm_obj
arm_mod = model.modifiers.new("Armature", "ARMATURE")
arm_mod.object = arm_obj
print(f"Vertex weighting complete across all {num_verts} vertices.")

# 6. Animation System (All 14 Required Actions)
fps = 30
scene = bpy.context.scene
scene.render.fps = fps

arm_obj.animation_data_create()
for pb in arm_obj.pose.bones:
    pb.rotation_mode = 'XYZ'

# Base resting arm rotation for T-pose character (swings arms down naturally by -68 degrees)
REST_ARM_L = (-68.0, 4.0, -10.0)
REST_ARM_R = (-68.0, -4.0, 10.0)

def set_active_action(name):
    act = bpy.data.actions.new(name=name)
    act.use_fake_user = True
    arm_obj.animation_data.action = act
    for pb in arm_obj.pose.bones:
        pb.location = (0, 0, 0)
        pb.rotation_euler = (0, 0, 0)
    return act

def insert_rot(bone_name, frame, euler_deg):
    pb = arm_obj.pose.bones[bone_name]
    pb.rotation_euler = (
        math.radians(euler_deg[0]),
        math.radians(euler_deg[1]),
        math.radians(euler_deg[2])
    )
    pb.keyframe_insert(data_path="rotation_euler", frame=frame)

def insert_loc(bone_name, frame, loc):
    pb = arm_obj.pose.bones[bone_name]
    pb.location = loc
    pb.keyframe_insert(data_path="location", frame=frame)

# 1. Idle (Bouncy breathing idle with arms resting down at hips)
act_idle = set_active_action("Idle")
for f, z_off, p_torso, p_head in [(0, 0, 0, 0), (30, -0.012, 2.5, -2.0), (60, 0, 0, 0)]:
    insert_loc("Root", f, (0, 0, z_off))
    insert_rot("Torso", f, (p_torso, 0, 0))
    insert_rot("Head", f, (p_head, 0, 0))
    insert_rot("Arm.L", f, (REST_ARM_L[0] + (2.0 if f == 30 else 0.0), REST_ARM_L[1], REST_ARM_L[2]))
    insert_rot("Arm.R", f, (REST_ARM_R[0] + (2.0 if f == 30 else 0.0), REST_ARM_R[1], REST_ARM_R[2]))

# 2. Idle_Secondary (Look around tilt)
act_idle_sec = set_active_action("Idle_Secondary")
for f in [0, 60]:
    insert_loc("Root", f, (0, 0, 0))
    insert_rot("Head", f, (0, 0, 0))
    insert_rot("Arm.L", f, REST_ARM_L)
    insert_rot("Arm.R", f, REST_ARM_R)
insert_loc("Root", 20, (0, 0, 0.02))
insert_rot("Head", 20, (0, 0, 18))
insert_rot("Head", 40, (0, 0, -18))

# 3. Walk (Playful toddler waddle walk)
act_walk = set_active_action("Walk")
for idx, f in enumerate([0, 6, 12, 18, 24]):
    phase = idx / 4.0 * 2.0 * math.pi
    l_rot = math.sin(phase) * 18.0
    r_rot = -math.sin(phase) * 18.0
    bob = abs(math.sin(phase * 2.0)) * 0.016
    insert_loc("Root", f, (0, 0, bob))
    insert_rot("Leg.L", f, (l_rot, 0, 0))
    insert_rot("Leg.R", f, (r_rot, 0, 0))
    # Arm swing forward/back via local Z rotation around resting baseline
    insert_rot("Arm.L", f, (REST_ARM_L[0], REST_ARM_L[1], REST_ARM_L[2] - l_rot * 0.8))
    insert_rot("Arm.R", f, (REST_ARM_R[0], REST_ARM_R[1], REST_ARM_R[2] + r_rot * 0.8))
    insert_rot("Head", f, (math.sin(phase) * 3.0, 0, 0))

# 4. Run (Energetic joyful sprint)
act_run = set_active_action("Run")
for idx, f in enumerate([0, 4, 8, 12, 15]):
    phase = idx / 4.0 * 2.0 * math.pi
    l_rot = math.sin(phase) * 32.0
    r_rot = -math.sin(phase) * 32.0
    bob = abs(math.sin(phase * 2.0)) * 0.028
    insert_loc("Root", f, (0, 0, bob))
    insert_rot("Torso", f, (12.0, 0, 0))
    insert_rot("Head", f, (-6.0, 0, 0))
    insert_rot("Leg.L", f, (l_rot, 0, 0))
    insert_rot("Leg.R", f, (r_rot, 0, 0))
    insert_rot("Arm.L", f, (REST_ARM_L[0] + 10.0, REST_ARM_L[1], REST_ARM_L[2] - l_rot * 1.2))
    insert_rot("Arm.R", f, (REST_ARM_R[0] + 10.0, REST_ARM_R[1], REST_ARM_R[2] + r_rot * 1.2))

# 5. Jump_Start (Squash anticipation)
act_jump_start = set_active_action("Jump_Start")
insert_loc("Root", 0, (0, 0, 0))
insert_rot("Arm.L", 0, REST_ARM_L)
insert_rot("Arm.R", 0, REST_ARM_R)

insert_loc("Root", 4, (0, 0, -0.040))
insert_rot("Torso", 4, (12.0, 0, 0))
insert_rot("Leg.L", 4, (-15.0, 0, 0))
insert_rot("Leg.R", 4, (-15.0, 0, 0))
insert_rot("Arm.L", 4, (REST_ARM_L[0] - 10.0, REST_ARM_L[1], REST_ARM_L[2] - 15.0))
insert_rot("Arm.R", 4, (REST_ARM_R[0] - 10.0, REST_ARM_R[1], REST_ARM_R[2] + 15.0))

insert_loc("Root", 8, (0, 0, 0.060))
insert_rot("Torso", 8, (-8.0, 0, 0))
insert_rot("Arm.L", 8, (-15.0, REST_ARM_L[1], REST_ARM_L[2] + 25.0))
insert_rot("Arm.R", 8, (-15.0, REST_ARM_R[1], REST_ARM_R[2] - 25.0))

# 6. Jump_Loop (Airborne float)
act_jump_loop = set_active_action("Jump_Loop")
for f in [0, 30]:
    insert_loc("Root", f, (0, 0, 0.040))
    insert_rot("Torso", f, (-4.0, 0, 0))
    insert_rot("Leg.L", f, (14.0, 0, 0))
    insert_rot("Leg.R", f, (-10.0, 0, 0))
    insert_rot("Arm.L", f, (-20.0, 0, 30.0))
    insert_rot("Arm.R", f, (-20.0, 0, -30.0))

# 7. Fall (Falling pose)
act_fall = set_active_action("Fall")
for f in [0, 20]:
    insert_loc("Root", f, (0, 0, 0))
    insert_rot("Torso", f, (8.0, 0, 0))
    insert_rot("Head", f, (-8.0, 0, 0))
    insert_rot("Arm.L", f, (0.0, 0, 45.0))
    insert_rot("Arm.R", f, (0.0, 0, -45.0))
    insert_rot("Leg.L", f, (-10.0, 0, 4.0))
    insert_rot("Leg.R", f, (-10.0, 0, -4.0))

# 8. Landing (Impact absorption)
act_landing = set_active_action("Landing")
insert_loc("Root", 0, (0, 0, -0.050))
insert_rot("Torso", 0, (15.0, 0, 0))
insert_rot("Leg.L", 0, (-18.0, 0, 0))
insert_rot("Leg.R", 0, (-18.0, 0, 0))
insert_rot("Arm.L", 0, (REST_ARM_L[0] - 10.0, REST_ARM_L[1], REST_ARM_L[2]))
insert_rot("Arm.R", 0, (REST_ARM_R[0] - 10.0, REST_ARM_R[1], REST_ARM_R[2]))

insert_loc("Root", 4, (0, 0, 0.010))
insert_rot("Torso", 4, (-4.0, 0, 0))
insert_loc("Root", 8, (0, 0, 0))
insert_rot("Torso", 8, (0, 0, 0))
insert_rot("Arm.L", 8, REST_ARM_L)
insert_rot("Arm.R", 8, REST_ARM_R)

# 9. Turn_Left
act_turn_l = set_active_action("Turn_Left")
for f in [0, 15]:
    insert_loc("Root", f, (0, 0, 0))
    insert_rot("Torso", f, (0, 0, 0))
    insert_rot("Arm.L", f, REST_ARM_L)
    insert_rot("Arm.R", f, REST_ARM_R)
insert_rot("Torso", 7, (0, 0, 20.0))
insert_rot("Head", 7, (0, 0, 28.0))

# 10. Turn_Right
act_turn_r = set_active_action("Turn_Right")
for f in [0, 15]:
    insert_loc("Root", f, (0, 0, 0))
    insert_rot("Torso", f, (0, 0, 0))
    insert_rot("Arm.L", f, REST_ARM_L)
    insert_rot("Arm.R", f, REST_ARM_R)
insert_rot("Torso", 7, (0, 0, -20.0))
insert_rot("Head", 7, (0, 0, -28.0))

# 11. Collect (Reach & celebrate)
act_collect = set_active_action("Collect")
for f in [0, 30]:
    insert_loc("Root", f, (0, 0, 0))
    insert_rot("Arm.R", f, REST_ARM_R)
    insert_rot("Arm.L", f, REST_ARM_L)
    insert_rot("Head", f, (0, 0, 0))
insert_loc("Root", 12, (0, 0, 0.020))
insert_rot("Arm.R", 12, (-25.0, 0.0, 50.0))
insert_rot("Head", 12, (10.0, 0, -8.0))

# 12. Interact
act_interact = set_active_action("Interact")
for f in [0, 25]:
    insert_rot("Arm.L", f, REST_ARM_L)
    insert_rot("Arm.R", f, REST_ARM_R)
insert_rot("Arm.L", 10, (-20.0, 0.0, 55.0))
insert_rot("Torso", 10, (10.0, 0, 10.0))

# 13. Victory (Astro Victory Dance with arms raised in V shape)
act_victory = set_active_action("Victory")
for f in [0, 45]:
    insert_loc("Root", f, (0, 0, 0))
    insert_rot("Arm.L", f, REST_ARM_L)
    insert_rot("Arm.R", f, REST_ARM_R)
    insert_rot("Torso", f, (0, 0, 0))
    insert_rot("Head", f, (0, 0, 0))
insert_loc("Root", 20, (0, 0, 0.080))
insert_rot("Arm.L", 20, (35.0, 0.0, 25.0))
insert_rot("Arm.R", 20, (35.0, 0.0, -25.0))
insert_rot("Torso", 20, (-6.0, 0, 0))
insert_rot("Head", 20, (-10.0, 0, 0))

# 14. Respawn
act_respawn = set_active_action("Respawn")
insert_loc("Root", 0, (0, 0, -0.070))
insert_rot("Arm.L", 0, REST_ARM_L)
insert_rot("Arm.R", 0, REST_ARM_R)
insert_loc("Root", 15, (0, 0, 0.050))
insert_loc("Root", 25, (0, 0, 0))

print("Created all 14 animation actions.")

# Set Idle as active action
arm_obj.animation_data.action = act_idle

# 7. Save .blend files
os.makedirs(os.path.dirname(OUTPUT_BLEND), exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=OUTPUT_BLEND)
print(f"Saved: {OUTPUT_BLEND}")
shutil.copyfile(OUTPUT_BLEND, CANONICAL_BLEND_1)
shutil.copyfile(OUTPUT_BLEND, CANONICAL_BLEND_2)
print("Updated canonical .blend files.")

# 8. Export GLB
for target in EXPORT_GLB_TARGETS:
    os.makedirs(os.path.dirname(target), exist_ok=True)
    bpy.ops.export_scene.gltf(
        filepath=target,
        export_format='GLB',
        use_selection=False,
        export_apply=False,
        export_skins=True,
        export_animations=True,
        export_animation_mode='ACTIONS',
        export_optimize_animation_size=False
    )
    print(f"Exported: {target}")

print("=== Astro Bot Rigging Pipeline Completed Successfully! ===")
