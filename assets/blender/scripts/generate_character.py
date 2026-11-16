"""
B.O.T Production 3D Character Builder (20 Articulated Component Objects)
Tiny Planet - Phase 6 Production Pipeline
Authoritative Visual Reference: Character Turnaround Sheet (~2.5 Heads Tall, Astro Bot Inspired)
Engine: Godot 4.7.1 Stable Standard | Blender 5.2.3 LTS
"""

import bpy
import bmesh
import math
from mathutils import Vector, Matrix

# Clear scene
bpy.ops.wm.read_factory_settings(use_empty=True)

# ---------------------------------------------------------
# 1. PBR Materials
# ---------------------------------------------------------
materials = {}

def get_mat(name, base_color, metallic=0.0, roughness=0.3, emission_color=(0,0,0,1), emission_strength=0.0):
    if name in materials:
        return materials[name]
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Base Color'].default_value = base_color
        bsdf.inputs['Metallic'].default_value = metallic
        bsdf.inputs['Roughness'].default_value = roughness
        if 'Emission Color' in bsdf.inputs:
            bsdf.inputs['Emission Color'].default_value = emission_color
            bsdf.inputs['Emission Strength'].default_value = emission_strength
        elif 'Emission' in bsdf.inputs:
            bsdf.inputs['Emission'].default_value = emission_color
    materials[name] = mat
    return mat

mat_white = get_mat("Mat_Pearl_White", (0.95, 0.96, 0.98, 1.0), metallic=0.06, roughness=0.18)
mat_blue = get_mat("Mat_Royal_Blue", (0.04, 0.26, 0.86, 1.0), metallic=0.15, roughness=0.22)
mat_yellow = get_mat("Mat_Golden_Yellow", (0.98, 0.72, 0.08, 1.0), metallic=0.0, roughness=0.30)
mat_visor = get_mat("Mat_Glossy_Visor", (0.010, 0.012, 0.018, 1.0), metallic=0.92, roughness=0.02)
mat_cyan = get_mat("Mat_Cyan_Emissive", (0.2, 0.88, 1.0, 1.0), metallic=0.0, roughness=0.1, emission_color=(0.25, 0.92, 1.0, 1.0), emission_strength=5.5)
mat_navy = get_mat("Mat_Graphite_Navy", (0.12, 0.14, 0.18, 1.0), metallic=0.45, roughness=0.38)

# ---------------------------------------------------------
# 2. Geometry Builders
# ---------------------------------------------------------
def create_beveled_box(name, dims, loc, mat, bevel_width=0.02, bevel_segs=4, taper_bottom=(1.0, 1.0)):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x *= dims[0]
        v.co.y *= dims[1]
        v.co.z *= dims[2]
        if v.co.z < 0:
            v.co.x *= taper_bottom[0]
            v.co.y *= taper_bottom[1]
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.location = loc
    if mat:
        obj.data.materials.append(mat)
    if bevel_width > 0:
        bev = obj.modifiers.new("Bevel", 'BEVEL')
        bev.width = bevel_width
        bev.segments = bevel_segs
        bev.limit_method = 'NONE'
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.modifier_apply(modifier="Bevel")
    for p in obj.data.polygons:
        p.use_smooth = True
    return obj

def create_smooth_cylinder(name, radius, depth, loc, mat, rot=(0,0,0), segs=28, bevel_width=0.008, radius2=None):
    r2 = radius if radius2 is None else radius2
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=segs, radius1=radius, radius2=r2, depth=depth)
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.location = loc
    obj.rotation_euler = rot
    if mat:
        obj.data.materials.append(mat)
    if bevel_width > 0:
        bev = obj.modifiers.new("Bevel", 'BEVEL')
        bev.width = bevel_width
        bev.segments = 2
        bev.limit_method = 'ANGLE'
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.modifier_apply(modifier="Bevel")
    for p in obj.data.polygons:
        p.use_smooth = True
    return obj

def create_smooth_sphere(name, radius, loc, mat, segs=28, rings=20, scale=(1,1,1)):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=segs, v_segments=rings, radius=radius)
    for v in bm.verts:
        v.co.x *= scale[0]
        v.co.y *= scale[1]
        v.co.z *= scale[2]
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.location = loc
    if mat:
        obj.data.materials.append(mat)
    for p in obj.data.polygons:
        p.use_smooth = True
    return obj

# ---------------------------------------------------------
# 3. Build 20 Discrete Production Articulated Components
# Note: Forward is -Y (converts cleanly to Godot -Z forward)
# Total height: ~1.02m, fits 1.15m CapsuleShape3D
# ---------------------------------------------------------

# --- 1. BOT_Head ---
helmet = create_beveled_box("BOT_Head", (0.44, 0.40, 0.36), (0.0, 0.0, 0.79), mat_white, bevel_width=0.08, bevel_segs=5)

# Cut recessed cavity into front of helmet
pocket_cutter = create_beveled_box("PocketCutter", (0.34, 0.12, 0.23), (0.0, -0.165, 0.79), None, bevel_width=0.035, bevel_segs=4)
bool_mod = helmet.modifiers.new("VisorPocket", 'BOOLEAN')
bool_mod.operation = 'DIFFERENCE'
bool_mod.object = pocket_cutter
bpy.context.view_layer.objects.active = helmet
bpy.ops.object.modifier_apply(modifier="VisorPocket")
bpy.data.objects.remove(pocket_cutter, do_unlink=True)

# Inset glossy black visor screen inside the recessed cavity
visor = create_beveled_box("Part_Visor", (0.33, 0.06, 0.22), (0.0, -0.165, 0.79), mat_visor, bevel_width=0.032, bevel_segs=4)

# Glowing cyan capsule eyes flush with the visor
eye_l = create_smooth_sphere("Part_Eye_L", 0.035, (-0.082, -0.192, 0.795), mat_cyan, segs=20, rings=16, scale=(0.85, 0.12, 1.45))
eye_r = create_smooth_sphere("Part_Eye_R", 0.035, (0.082, -0.192, 0.795), mat_cyan, segs=20, rings=16, scale=(0.85, 0.12, 1.45))

# Royal blue curved crown armor cap covering top of helmet
crown = create_smooth_sphere("Part_Crown", 0.235, (0.0, 0.015, 0.88), mat_blue, segs=32, rings=24, scale=(0.95, 0.88, 0.45))

bpy.ops.object.select_all(action='DESELECT')
for p in [crown, visor, eye_l, eye_r]:
    p.select_set(True)
helmet.select_set(True)
bpy.context.view_layer.objects.active = helmet
bpy.ops.object.join()
BOT_Head = helmet
BOT_Head.name = "BOT_Head"

# --- 2. BOT_Antenna ---
stem = create_smooth_cylinder("Part_AntStem", 0.014, 0.08, (0.0, 0.02, 1.005), mat_yellow, rot=(math.radians(22), 0, 0), segs=16)
fin = create_beveled_box("Part_AntFin", (0.022, 0.09, 0.06), (0.0, 0.055, 1.065), mat_yellow, bevel_width=0.015, bevel_segs=3)
fin.rotation_euler = (math.radians(38), 0, 0)
bpy.ops.object.select_all(action='DESELECT')
stem.select_set(True)
fin.select_set(True)
bpy.context.view_layer.objects.active = fin
bpy.ops.object.join()
BOT_Antenna = fin
BOT_Antenna.name = "BOT_Antenna"

# --- 3 & 4. BOT_Ear_L and BOT_Ear_R ---
def build_ear(side, sign):
    base = create_smooth_cylinder(f"BOT_Ear_{side}", 0.092, 0.032, (sign * 0.228, -0.01, 0.79), mat_yellow, rot=(0, math.radians(90), 0), segs=28, bevel_width=0.008)
    housing = create_smooth_cylinder(f"Part_EarHouse_{side}", 0.076, 0.024, (sign * 0.238, -0.01, 0.79), mat_blue, rot=(0, math.radians(90), 0), segs=28, bevel_width=0.005)
    ring = create_smooth_cylinder(f"Part_EarRing_{side}", 0.055, 0.014, (sign * 0.245, -0.01, 0.79), mat_cyan, rot=(0, math.radians(90), 0), segs=28, bevel_width=0.002)
    hub = create_smooth_cylinder(f"Part_EarHub_{side}", 0.032, 0.016, (sign * 0.252, -0.01, 0.79), mat_navy, rot=(0, math.radians(90), 0), segs=20)
    
    bpy.ops.object.select_all(action='DESELECT')
    for p in [housing, ring, hub]:
        p.select_set(True)
    base.select_set(True)
    bpy.context.view_layer.objects.active = base
    bpy.ops.object.join()
    base.name = f"BOT_Ear_{side}"
    return base

BOT_Ear_L = build_ear("L", 1.0)
BOT_Ear_R = build_ear("R", -1.0)

# --- 5. BOT_Scarf ---
cowl = create_smooth_cylinder("BOT_Scarf", 0.175, 0.075, (0.0, 0.0, 0.615), mat_yellow, segs=28, bevel_width=0.028)
bib = create_beveled_box("Part_ScarfBib", (0.13, 0.035, 0.10), (0.0, -0.145, 0.56), mat_yellow, bevel_width=0.016, bevel_segs=3, taper_bottom=(0.4, 0.8))
badge_bg = create_beveled_box("Part_ScarfBadgeB", (0.055, 0.015, 0.045), (0.0, -0.165, 0.565), mat_blue, bevel_width=0.006, bevel_segs=2, taper_bottom=(0.3, 0.8))
badge_cyan = create_beveled_box("Part_ScarfBadgeC", (0.032, 0.01, 0.028), (0.0, -0.172, 0.565), mat_cyan, bevel_width=0.004, bevel_segs=2, taper_bottom=(0.3, 0.8))
tail1 = create_beveled_box("Part_ScarfTail1", (0.045, 0.15, 0.022), (0.12, 0.14, 0.59), mat_yellow, bevel_width=0.008)
tail1.rotation_euler = (math.radians(-24), math.radians(12), math.radians(26))
tail2 = create_beveled_box("Part_ScarfTail2", (0.038, 0.18, 0.018), (0.15, 0.17, 0.53), mat_yellow, bevel_width=0.008)
tail2.rotation_euler = (math.radians(-34), math.radians(18), math.radians(34))

bpy.ops.object.select_all(action='DESELECT')
for p in [bib, badge_bg, badge_cyan, tail1, tail2]:
    p.select_set(True)
cowl.select_set(True)
bpy.context.view_layer.objects.active = cowl
bpy.ops.object.join()
BOT_Scarf = cowl
BOT_Scarf.name = "BOT_Scarf"

# --- 6. BOT_Chest_Armor ---
chest = create_beveled_box("BOT_Chest_Armor", (0.28, 0.21, 0.20), (0.0, -0.01, 0.495), mat_white, bevel_width=0.045, bevel_segs=4, taper_bottom=(0.82, 0.88))
core_rim = create_beveled_box("Part_CoreRim", (0.085, 0.02, 0.075), (0.0, -0.122, 0.465), mat_blue, bevel_width=0.008, bevel_segs=2, taper_bottom=(1.6, 0.8))
core_tri = create_beveled_box("Part_CoreTri", (0.055, 0.015, 0.05), (0.0, -0.130, 0.465), mat_cyan, bevel_width=0.006, bevel_segs=2, taper_bottom=(1.6, 0.8))

bpy.ops.object.select_all(action='DESELECT')
for p in [core_rim, core_tri]:
    p.select_set(True)
chest.select_set(True)
bpy.context.view_layer.objects.active = chest
bpy.ops.object.join()
BOT_Chest_Armor = chest
BOT_Chest_Armor.name = "BOT_Chest_Armor"

# --- 7. BOT_Backpack ---
pack = create_beveled_box("BOT_Backpack", (0.18, 0.08, 0.16), (0.0, 0.125, 0.50), mat_blue, bevel_width=0.03, bevel_segs=3)
pack_core = create_beveled_box("Part_PackCore", (0.065, 0.02, 0.06), (0.0, 0.168, 0.50), mat_cyan, bevel_width=0.008, taper_bottom=(0.3, 0.8))
pack_strap_l = create_beveled_box("Part_PackStrapL", (0.025, 0.06, 0.05), (0.075, 0.10, 0.56), mat_yellow, bevel_width=0.006)
pack_strap_l.rotation_euler = (math.radians(-30), 0, math.radians(-15))
pack_strap_r = create_beveled_box("Part_PackStrapR", (0.025, 0.06, 0.05), (-0.075, 0.10, 0.56), mat_yellow, bevel_width=0.006)
pack_strap_r.rotation_euler = (math.radians(-30), 0, math.radians(15))

bpy.ops.object.select_all(action='DESELECT')
for p in [pack_core, pack_strap_l, pack_strap_r]:
    p.select_set(True)
pack.select_set(True)
bpy.context.view_layer.objects.active = pack
bpy.ops.object.join()
BOT_Backpack = pack
BOT_Backpack.name = "BOT_Backpack"

# --- 8. BOT_Pelvis ---
BOT_Pelvis = create_beveled_box("BOT_Pelvis", (0.22, 0.17, 0.08), (0.0, 0.0, 0.375), mat_navy, bevel_width=0.025, bevel_segs=3, taper_bottom=(0.85, 0.85))

# --- 9 & 10. BOT_Arm_L and BOT_Arm_R ---
def build_upper_arm(side, sign):
    joint = create_smooth_sphere(f"BOT_Arm_{side}", 0.046, (sign * 0.175, 0.0, 0.50), mat_navy, segs=20, rings=16)
    paul = create_smooth_sphere(f"Part_Paul_{side}", 0.056, (sign * 0.180, 0.0, 0.525), mat_white, segs=20, rings=16, scale=(1.08, 1.08, 0.8))
    bicep = create_smooth_cylinder(f"Part_Bicep_{side}", 0.038, 0.07, (sign * 0.182, 0.0, 0.445), mat_white, segs=20, bevel_width=0.006)
    elbow = create_smooth_sphere(f"Part_Elbow_{side}", 0.036, (sign * 0.185, 0.0, 0.40), mat_navy, segs=16, rings=12)
    
    bpy.ops.object.select_all(action='DESELECT')
    for p in [paul, bicep, elbow]:
        p.select_set(True)
    joint.select_set(True)
    bpy.context.view_layer.objects.active = joint
    bpy.ops.object.join()
    joint.name = f"BOT_Arm_{side}"
    return joint

BOT_Arm_L = build_upper_arm("L", 1.0)
BOT_Arm_R = build_upper_arm("R", -1.0)

# --- 11 & 12. BOT_Forearm_L and BOT_Forearm_R ---
def build_forearm(side, sign):
    gauntlet = create_smooth_cylinder(f"BOT_Forearm_{side}", 0.048, 0.10, (sign * 0.190, 0.0, 0.335), mat_white, segs=24, bevel_width=0.008, radius2=0.042)
    cuff = create_smooth_cylinder(f"Part_Cuff_{side}", 0.049, 0.022, (sign * 0.190, 0.0, 0.29), mat_blue, segs=24, bevel_width=0.004)
    glyph = create_beveled_box(f"Part_Glyph_{side}", (0.008, 0.025, 0.025), (sign * 0.237, 0.0, 0.335), mat_cyan, bevel_width=0.003)
    
    bpy.ops.object.select_all(action='DESELECT')
    for p in [cuff, glyph]:
        p.select_set(True)
    gauntlet.select_set(True)
    bpy.context.view_layer.objects.active = gauntlet
    bpy.ops.object.join()
    gauntlet.name = f"BOT_Forearm_{side}"
    return gauntlet

BOT_Forearm_L = build_forearm("L", 1.0)
BOT_Forearm_R = build_forearm("R", -1.0)

# --- 13 & 14. BOT_Hand_L and BOT_Hand_R ---
def build_hand(side, sign):
    palm = create_beveled_box(f"BOT_Hand_{side}", (0.065, 0.06, 0.065), (sign * 0.190, 0.0, 0.24), mat_navy, bevel_width=0.016, bevel_segs=3)
    thumb = create_beveled_box(f"Part_Thumb_{side}", (0.026, 0.035, 0.038), (sign * (0.190 - sign * 0.028), -0.022, 0.235), mat_navy, bevel_width=0.008)
    thumb.rotation_euler = (math.radians(-25), 0, math.radians(-sign * 30))
    fingers = create_beveled_box(f"Part_Fingers_{side}", (0.05, 0.045, 0.035), (sign * 0.190, -0.015, 0.20), mat_navy, bevel_width=0.01)
    backplate = create_beveled_box(f"Part_Backplate_{side}", (0.055, 0.015, 0.055), (sign * 0.190, 0.032, 0.24), mat_white, bevel_width=0.006)
    
    bpy.ops.object.select_all(action='DESELECT')
    for p in [thumb, fingers, backplate]:
        p.select_set(True)
    palm.select_set(True)
    bpy.context.view_layer.objects.active = palm
    bpy.ops.object.join()
    palm.name = f"BOT_Hand_{side}"
    return palm

BOT_Hand_L = build_hand("L", 1.0)
BOT_Hand_R = build_hand("R", -1.0)

# --- 15 & 16. BOT_Thigh_L and BOT_Thigh_R ---
def build_thigh(side, sign):
    hip = create_smooth_sphere(f"BOT_Thigh_{side}", 0.046, (sign * 0.095, 0.0, 0.345), mat_navy, segs=20, rings=16)
    armor = create_smooth_cylinder(f"Part_ThighArmor_{side}", 0.052, 0.08, (sign * 0.095, 0.0, 0.295), mat_white, segs=24, bevel_width=0.008)
    knee = create_smooth_sphere(f"Part_Knee_{side}", 0.042, (sign * 0.095, 0.0, 0.240), mat_navy, segs=20, rings=16)
    
    bpy.ops.object.select_all(action='DESELECT')
    for p in [armor, knee]:
        p.select_set(True)
    hip.select_set(True)
    bpy.context.view_layer.objects.active = hip
    bpy.ops.object.join()
    hip.name = f"BOT_Thigh_{side}"
    return hip

BOT_Thigh_L = build_thigh("L", 1.0)
BOT_Thigh_R = build_thigh("R", -1.0)

# --- 17 & 18. BOT_Shin_L and BOT_Shin_R ---
def build_shin(side, sign):
    shin = create_smooth_cylinder(f"BOT_Shin_{side}", 0.058, 0.10, (sign * 0.095, -0.005, 0.175), mat_white, segs=24, bevel_width=0.010, radius2=0.048)
    led = create_beveled_box(f"Part_ShinLED_{side}", (0.008, 0.022, 0.035), (sign * (0.095 + sign * 0.058), 0.0, 0.16), mat_cyan, bevel_width=0.003)
    
    bpy.ops.object.select_all(action='DESELECT')
    led.select_set(True)
    shin.select_set(True)
    bpy.context.view_layer.objects.active = shin
    bpy.ops.object.join()
    shin.name = f"BOT_Shin_{side}"
    return shin

BOT_Shin_L = build_shin("L", 1.0)
BOT_Shin_R = build_shin("R", -1.0)

# --- 19 & 20. BOT_Boot_L and BOT_Boot_R ---
def build_boot(side, sign):
    heel = create_beveled_box(f"BOT_Boot_{side}", (0.12, 0.13, 0.095), (sign * 0.095, 0.02, 0.075), mat_white, bevel_width=0.025, bevel_segs=4)
    toe = create_beveled_box(f"Part_Toe_{side}", (0.13, 0.12, 0.08), (sign * 0.095, -0.072, 0.065), mat_yellow, bevel_width=0.038, bevel_segs=4)
    sole = create_beveled_box(f"Part_Sole_{side}", (0.14, 0.23, 0.032), (sign * 0.095, -0.025, 0.018), mat_blue, bevel_width=0.012, bevel_segs=3)
    led = create_beveled_box(f"Part_BootLED_{side}", (0.01, 0.032, 0.02), (sign * (0.095 + sign * 0.072), 0.02, 0.05), mat_cyan, bevel_width=0.003)
    
    bpy.ops.object.select_all(action='DESELECT')
    for p in [toe, sole, led]:
        p.select_set(True)
    heel.select_set(True)
    bpy.context.view_layer.objects.active = heel
    bpy.ops.object.join()
    heel.name = f"BOT_Boot_{side}"
    return heel

BOT_Boot_L = build_boot("L", 1.0)
BOT_Boot_R = build_boot("R", -1.0)

# List of all 20 component objects
components = [
    BOT_Head, BOT_Antenna, BOT_Ear_L, BOT_Ear_R, BOT_Scarf,
    BOT_Chest_Armor, BOT_Backpack, BOT_Pelvis,
    BOT_Arm_L, BOT_Arm_R, BOT_Forearm_L, BOT_Forearm_R,
    BOT_Hand_L, BOT_Hand_R, BOT_Thigh_L, BOT_Thigh_R,
    BOT_Shin_L, BOT_Shin_R, BOT_Boot_L, BOT_Boot_R
]

# Ensure UV smart project on each component
for c in components:
    bpy.context.view_layer.objects.active = c
    c.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=math.radians(66), island_margin=0.02)
    bpy.ops.object.mode_set(mode='OBJECT')
    c.select_set(False)

# ---------------------------------------------------------
# 4. Rigging: Armature with 13 Deformation Bones
# ---------------------------------------------------------
armature_data = bpy.data.armatures.new("ArmatureData")
armature_obj = bpy.data.objects.new("BOT_Armature", armature_data)
bpy.context.collection.objects.link(armature_obj)
bpy.context.view_layer.objects.active = armature_obj

bpy.ops.object.mode_set(mode='EDIT')
edit_bones = armature_data.edit_bones

# Root bone
b_root = edit_bones.new("Root")
b_root.head = (0.0, 0.0, 0.38)
b_root.tail = (0.0, 0.0, 0.44)

# Torso bone
b_torso = edit_bones.new("Torso")
b_torso.parent = b_root
b_torso.head = (0.0, 0.0, 0.38)
b_torso.tail = (0.0, 0.0, 0.62)

# Head bone
b_head = edit_bones.new("Head")
b_head.parent = b_torso
b_head.head = (0.0, 0.0, 0.62)
b_head.tail = (0.0, 0.0, 0.98)

# Antenna bones
b_ant_l = edit_bones.new("Antenna.L")
b_ant_l.parent = b_head
b_ant_l.head = (-0.015, 0.02, 1.00)
b_ant_l.tail = (-0.025, 0.05, 1.08)

b_ant_r = edit_bones.new("Antenna.R")
b_ant_r.parent = b_head
b_ant_r.head = (0.015, 0.02, 1.00)
b_ant_r.tail = (0.025, 0.05, 1.08)

# Left Arm & Hand
b_arm_l = edit_bones.new("Arm.L")
b_arm_l.parent = b_torso
b_arm_l.head = (0.175, 0.0, 0.50)
b_arm_l.tail = (0.190, 0.0, 0.38)

b_hand_l = edit_bones.new("Hand.L")
b_hand_l.parent = b_arm_l
b_hand_l.head = (0.190, 0.0, 0.38)
b_hand_l.tail = (0.190, 0.0, 0.22)

# Right Arm & Hand
b_arm_r = edit_bones.new("Arm.R")
b_arm_r.parent = b_torso
b_arm_r.head = (-0.175, 0.0, 0.50)
b_arm_r.tail = (-0.190, 0.0, 0.38)

b_hand_r = edit_bones.new("Hand.R")
b_hand_r.parent = b_arm_r
b_hand_r.head = (-0.190, 0.0, 0.38)
b_hand_r.tail = (-0.190, 0.0, 0.22)

# Left Leg & Foot
b_leg_l = edit_bones.new("Leg.L")
b_leg_l.parent = b_root
b_leg_l.head = (0.095, 0.0, 0.345)
b_leg_l.tail = (0.095, 0.0, 0.20)

b_foot_l = edit_bones.new("Foot.L")
b_foot_l.parent = b_leg_l
b_foot_l.head = (0.095, 0.0, 0.20)
b_foot_l.tail = (0.095, -0.06, 0.02)

# Right Leg & Foot
b_leg_r = edit_bones.new("Leg.R")
b_leg_r.parent = b_root
b_leg_r.head = (-0.095, 0.0, 0.345)
b_leg_r.tail = (-0.095, 0.0, 0.20)

b_foot_r = edit_bones.new("Foot.R")
b_foot_r.parent = b_leg_r
b_foot_r.head = (-0.095, 0.0, 0.20)
b_foot_r.tail = (-0.095, -0.06, 0.02)

bpy.ops.object.mode_set(mode='OBJECT')

# ---------------------------------------------------------
# 5. Component Binding to Bones (Discrete Mesh Parenting)
# ---------------------------------------------------------
bone_mapping = {
    "BOT_Head": "Head",
    "BOT_Antenna": "Head",
    "BOT_Ear_L": "Head",
    "BOT_Ear_R": "Head",
    "BOT_Scarf": "Torso",
    "BOT_Chest_Armor": "Torso",
    "BOT_Backpack": "Torso",
    "BOT_Pelvis": "Root",
    "BOT_Arm_L": "Arm.L",
    "BOT_Arm_R": "Arm.R",
    "BOT_Forearm_L": "Arm.L",
    "BOT_Forearm_R": "Arm.R",
    "BOT_Hand_L": "Hand.L",
    "BOT_Hand_R": "Hand.R",
    "BOT_Thigh_L": "Leg.L",
    "BOT_Thigh_R": "Leg.R",
    "BOT_Shin_L": "Leg.L",
    "BOT_Shin_R": "Leg.R",
    "BOT_Boot_L": "Foot.L",
    "BOT_Boot_R": "Foot.R"
}

all_bone_names = [b.name for b in armature_data.bones]

for comp in components:
    target_bone = bone_mapping[comp.name]
    comp.parent = armature_obj
    
    # Create vertex groups for all bones
    for b_name in all_bone_names:
        vg = comp.vertex_groups.new(name=b_name)
        if b_name == target_bone:
            v_indices = [v.index for v in comp.data.vertices]
            vg.add(v_indices, 1.0, 'REPLACE')
            
    # Add Armature Modifier
    mod = comp.modifiers.new("Armature", 'ARMATURE')
    mod.object = armature_obj

print("All 20 component meshes bound to Armature successfully.")

# ---------------------------------------------------------
# 6. Complete 14 Production Animation Actions
# ---------------------------------------------------------
fps = 30
scene = bpy.context.scene
scene.render.fps = fps

armature_obj.animation_data_create()
for pb in armature_obj.pose.bones:
    pb.rotation_mode = 'QUATERNION'

def set_active_action(name):
    act = bpy.data.actions.new(name=name)
    act.use_fake_user = True
    armature_obj.animation_data.action = act
    for pb in armature_obj.pose.bones:
        pb.location = (0, 0, 0)
        pb.rotation_quaternion = (1, 0, 0, 0)
    return act

def insert_rot(bone_name, frame, euler_deg):
    pb = armature_obj.pose.bones[bone_name]
    q = Matrix.Rotation(math.radians(euler_deg[0]), 4, 'X') @ \
        Matrix.Rotation(math.radians(euler_deg[1]), 4, 'Y') @ \
        Matrix.Rotation(math.radians(euler_deg[2]), 4, 'Z')
    pb.rotation_quaternion = q.to_quaternion()
    pb.keyframe_insert(data_path="rotation_quaternion", frame=frame)

def insert_loc(bone_name, frame, loc):
    pb = armature_obj.pose.bones[bone_name]
    pb.location = loc
    pb.keyframe_insert(data_path="location", frame=frame)

# 1. Idle (2.0s looping breathing & sway)
act_idle = set_active_action("Idle")
for f, z_off, p_torso, p_head in [(0, 0, 0, 0), (30, -0.015, 2, -1.5), (60, 0, 0, 0)]:
    insert_loc("Root", f, (0, 0, z_off))
    insert_rot("Torso", f, (p_torso, 0, 0))
    insert_rot("Head", f, (p_head, 0, 0))
    insert_rot("Arm.L", f, (10, 0, 8))
    insert_rot("Arm.R", f, (10, 0, -8))

# 2. Idle_Secondary (Fidget: ear wiggle & happy bounce)
act_idle_sec = set_active_action("Idle_Secondary")
for f in [0, 60]:
    insert_loc("Root", f, (0, 0, 0))
    insert_rot("Head", f, (0, 0, 0))
insert_loc("Root", 20, (0, 0, 0.03))
insert_rot("Head", 20, (0, 0, 15))
insert_rot("Head", 40, (0, 0, -15))

# 3. Walk (0.8s looping chibi march)
act_walk = set_active_action("Walk")
walk_frames = [0, 6, 12, 18, 24]
for idx, f in enumerate(walk_frames):
    phase = idx / 4.0 * 2.0 * math.pi
    l_rot = math.sin(phase) * 22
    r_rot = -math.sin(phase) * 22
    bob = abs(math.sin(phase * 2)) * 0.02
    insert_loc("Root", f, (0, 0, bob))
    insert_rot("Leg.L", f, (l_rot, 0, 0))
    insert_rot("Leg.R", f, (r_rot, 0, 0))
    insert_rot("Arm.L", f, (-l_rot * 0.8, 0, 6))
    insert_rot("Arm.R", f, (-r_rot * 0.8, 0, -6))
    insert_rot("Head", f, (math.sin(phase) * 3, 0, 0))

# 4. Run (0.5s brisk energetic dash)
act_run = set_active_action("Run")
run_frames = [0, 4, 8, 12, 15]
for idx, f in enumerate(run_frames):
    phase = idx / 4.0 * 2.0 * math.pi
    l_rot = math.sin(phase) * 38
    r_rot = -math.sin(phase) * 38
    bob = abs(math.sin(phase * 2)) * 0.035
    insert_loc("Root", f, (0, 0, bob))
    insert_rot("Torso", f, (14, 0, 0))
    insert_rot("Head", f, (-8, 0, 0))
    insert_rot("Leg.L", f, (l_rot, 0, 0))
    insert_rot("Leg.R", f, (r_rot, 0, 0))
    insert_rot("Arm.L", f, (-l_rot * 1.1, 0, 10))
    insert_rot("Arm.R", f, (-r_rot * 1.1, 0, -10))

# 5. Jump_Start (Squat and takeoff)
act_jump_start = set_active_action("Jump_Start")
insert_loc("Root", 0, (0, 0, 0))
insert_loc("Root", 4, (0, 0, -0.04))
insert_loc("Root", 8, (0, 0, 0.05))
insert_rot("Torso", 4, (15, 0, 0))
insert_rot("Leg.L", 4, (-25, 0, 0))
insert_rot("Leg.R", 4, (-25, 0, 0))

# 6. Jump_Loop (Airborne pose)
act_jump_loop = set_active_action("Jump_Loop")
for f in [0, 9, 18]:
    insert_loc("Root", f, (0, 0, 0.02))
    insert_rot("Leg.L", f, (-15, 0, -5))
    insert_rot("Leg.R", f, (10, 0, 5))
    insert_rot("Arm.L", f, (-35, 0, 25))
    insert_rot("Arm.R", f, (-35, 0, -25))

# 7. Fall (Falling pose)
act_fall = set_active_action("Fall")
for f in [0, 9, 18]:
    insert_loc("Root", f, (0, 0, 0))
    insert_rot("Leg.L", f, (15, 0, 0))
    insert_rot("Leg.R", f, (15, 0, 0))
    insert_rot("Arm.L", f, (-55, 0, 35))
    insert_rot("Arm.R", f, (-55, 0, -35))

# 8. Landing (Impact squash and recover)
act_land = set_active_action("Landing")
insert_loc("Root", 0, (0, 0, -0.06))
insert_loc("Root", 5, (0, 0, -0.03))
insert_loc("Root", 9, (0, 0, 0))
insert_rot("Torso", 0, (18, 0, 0))
insert_rot("Torso", 9, (0, 0, 0))

# 9. Turn_Left
act_turn_l = set_active_action("Turn_Left")
insert_rot("Root", 0, (0, 0, 0))
insert_rot("Root", 9, (0, 25, 0))

# 10. Turn_Right
act_turn_r = set_active_action("Turn_Right")
insert_rot("Root", 0, (0, 0, 0))
insert_rot("Root", 9, (0, -25, 0))

# 11. Collect (Reach out and grasp)
act_collect = set_active_action("Collect")
insert_rot("Arm.R", 0, (0, 0, 0))
insert_rot("Arm.R", 8, (-65, 0, -10))
insert_rot("Arm.R", 18, (0, 0, 0))

# 12. Interact (Press mechanism button)
act_interact = set_active_action("Interact")
insert_rot("Arm.R", 0, (0, 0, 0))
insert_rot("Arm.R", 9, (-80, 0, 0))
insert_rot("Arm.R", 18, (0, 0, 0))

# 13. Victory (Joyful cheer & arms up!)
act_victory = set_active_action("Victory")
for f in [0, 36]:
    insert_loc("Root", f, (0, 0, 0))
    insert_rot("Arm.L", f, (-110, 0, 35))
    insert_rot("Arm.R", f, (-110, 0, -35))
insert_loc("Root", 18, (0, 0, 0.08))

# 14. Respawn (Rise from ground)
act_respawn = set_active_action("Respawn")
insert_loc("Root", 0, (0, 0, -0.3))
insert_loc("Root", 24, (0, 0, 0))

# Default back to Idle
armature_obj.animation_data.action = act_idle

# ---------------------------------------------------------
# 7. Save .blend and Export glTF 2.0
# ---------------------------------------------------------
blend_paths = [
    "/Users/it/Documents/TINY PLANET/assets/models/character/bot.blend",
    "/Users/it/Documents/TINY PLANET/assets/models/source/bot.blend",
    "/Users/it/Documents/TINY PLANET/assets/blender/source/bot.blend",
    "/Users/it/Documents/TINY PLANET/assets/blender/source/bot_character.blend"
]

import os
for bp in blend_paths:
    os.makedirs(os.path.dirname(bp), exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=bp)
    print(f"✓ Saved Blender source to: {bp}")

glb_paths = [
    "/Users/it/Documents/TINY PLANET/assets/models/character/bot.glb",
    "/Users/it/Documents/TINY PLANET/assets/models/characters/bot.glb",
    "/Users/it/Documents/TINY PLANET/assets/models/bot.glb"
]

for gp in glb_paths:
    os.makedirs(os.path.dirname(gp), exist_ok=True)
    bpy.ops.export_scene.gltf(
        filepath=gp,
        export_format='GLB',
        use_selection=False,
        export_apply=False,
        export_skins=True,
        export_animations=True,
        export_animation_mode='ACTIONS',
        export_optimize_animation_size=False
    )
    print(f"✓ Exported production B.O.T GLB to: {gp}")

print("B.O.T Production 3D Character construction complete!")
