"""
B.O.T Redesign — Phase 2: Complete Visual Identity Overhaul
Authoritative Candidate Generation Script
Target: Modern, Compact, Agile Futuristic Exploration Robot
Engine: Godot 4.7.1 Stable Standard | Blender 5.2.3 LTS
"""

import bpy
import bmesh
import math
from mathutils import Vector, Matrix
import os

# Clear scene
bpy.ops.wm.read_factory_settings(use_empty=True)

# ---------------------------------------------------------
# 1. PBR Materials for Modern Explorer Identity
# ---------------------------------------------------------
materials = {}

def get_mat(name, base_color, metallic=0.0, roughness=0.25, emission_color=(0,0,0,1), emission_strength=0.0, clearcoat=0.0):
    if name in materials:
        return materials[name]
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Base Color'].default_value = base_color
        bsdf.inputs['Metallic'].default_value = metallic
        bsdf.inputs['Roughness'].default_value = roughness
        if 'Coat Weight' in bsdf.inputs:
            bsdf.inputs['Coat Weight'].default_value = clearcoat
        elif 'Clearcoat' in bsdf.inputs:
            bsdf.inputs['Clearcoat'].default_value = clearcoat
        if emission_strength > 0:
            if 'Emission Color' in bsdf.inputs:
                bsdf.inputs['Emission Color'].default_value = emission_color
                bsdf.inputs['Emission Strength'].default_value = emission_strength
            elif 'Emission' in bsdf.inputs:
                bsdf.inputs['Emission'].default_value = emission_color
    materials[name] = mat
    return mat

mat_white = get_mat("Mat_Satin_White", (0.92, 0.93, 0.96, 1.0), metallic=0.04, roughness=0.28, clearcoat=0.20)
mat_blue = get_mat("Mat_Cobalt_Blue", (0.05, 0.24, 0.78, 1.0), metallic=0.35, roughness=0.22, clearcoat=0.25)
mat_gold = get_mat("Mat_Warm_Gold", (0.88, 0.68, 0.22, 1.0), metallic=0.88, roughness=0.26)
mat_visor = get_mat("Mat_Glossy_Visor", (0.008, 0.010, 0.014, 1.0), metallic=0.94, roughness=0.025, clearcoat=1.0)
mat_cyan = get_mat("Mat_Cyan_Core", (0.10, 0.85, 1.0, 1.0), metallic=0.0, roughness=0.08, emission_color=(0.10, 0.85, 1.0, 1.0), emission_strength=4.0)
mat_navy = get_mat("Mat_Graphite_Chassis", (0.10, 0.12, 0.16, 1.0), metallic=0.65, roughness=0.32)

# ---------------------------------------------------------
# 2. Geometry Modeling Helpers
# ---------------------------------------------------------
def create_subdiv_box(name, dims, loc, mat, subdiv=2, smooth=True, bevel_width=0.0, taper_z=None):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x *= dims[0]
        v.co.y *= dims[1]
        v.co.z *= dims[2]
        if taper_z:
            factor = 1.0 + (v.co.z / (dims[2]*0.5)) * taper_z
            v.co.x *= factor
            v.co.y *= factor
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
        bev.segments = 2
        bev.limit_method = 'ANGLE'
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.modifier_apply(modifier="Bevel")
    if subdiv > 0:
        sub = obj.modifiers.new("Subdiv", 'SUBSURF')
        sub.levels = subdiv
        sub.render_levels = subdiv
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.modifier_apply(modifier="Subdiv")
    if smooth:
        for p in obj.data.polygons:
            p.use_smooth = True
    return obj

def create_smooth_sphere(name, radius, loc, mat, segs=36, rings=28, scale=(1,1,1)):
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

def create_smooth_cylinder(name, radius, depth, loc, mat, rot=(0,0,0), segs=32, bevel_width=0.008, radius2=None):
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

# ---------------------------------------------------------
# 3. Build Deliberate Modern Explorer Components
# Total height: ~1.02m (Forward is -Y, converting to Godot -Z)
# ---------------------------------------------------------

# ==================== 1. BOT_Head (Futuristic Aerodynamic Helmet) ====================
# Custom quad helmet cage: tapered rear aerodynamic curve, chamfered brow
bm_helm = bmesh.new()
bmesh.ops.create_cube(bm_helm, size=1.0)
for v in bm_helm.verts:
    v.co.x *= 0.36
    v.co.y *= 0.34
    v.co.z *= 0.28
    # Aerodynamic rear taper: top vertices shifted slightly backward (+Y)
    if v.co.z > 0:
        v.co.y += 0.04
        v.co.x *= 0.90
    # Front visor recess sculpting
    if v.co.y < 0:
        v.co.x *= 0.96
mesh_helm = bpy.data.meshes.new("HelmetMesh")
bm_helm.to_mesh(mesh_helm)
bm_helm.free()
helmet = bpy.data.objects.new("BOT_Head", mesh_helm)
bpy.context.collection.objects.link(helmet)
helmet.location = (0.0, 0.0, 0.775)
helmet.data.materials.append(mat_white)

bev_h = helmet.modifiers.new("Bevel", 'BEVEL')
bev_h.width = 0.055
bev_h.segments = 3
bpy.context.view_layer.objects.active = helmet
bpy.ops.object.modifier_apply(modifier="Bevel")
sub_h = helmet.modifiers.new("Subdiv", 'SUBSURF')
sub_h.levels = 2
bpy.ops.object.modifier_apply(modifier="Subdiv")
for p in helmet.data.polygons:
    p.use_smooth = True

# Wrap-around panoramic curved obsidian visor seamlessly recessed into the face
visor = create_subdiv_box("Part_Visor", (0.30, 0.10, 0.19), (0.0, -0.125, 0.775), mat_visor, subdiv=3)
# Bulge visor outward smoothly along front curvature
for v in visor.data.vertices:
    if v.co.y < 0:
        v.co.y -= 0.025 * (1.0 - (v.co.x/0.18)**2 - (v.co.z/0.12)**2 if abs(v.co.x)<0.18 and abs(v.co.z)<0.12 else 0)

# Expressive Modern Cyan LED Eyes displayed inside the visor (digital rounded capsules)
eye_l = create_subdiv_box("Part_Eye_L", (0.038, 0.010, 0.070), (-0.068, -0.192, 0.775), mat_cyan, subdiv=2)
eye_l.rotation_euler = (0, 0, math.radians(-2.0))
eye_r = create_subdiv_box("Part_Eye_R", (0.038, 0.010, 0.070), (0.068, -0.192, 0.775), mat_cyan, subdiv=2)
eye_r.rotation_euler = (0, 0, math.radians(2.0))

# Cobalt Blue Upper Canopy Plate (Sleek aerodynamic crest wrapping over top and down rear)
bm_can = bmesh.new()
c_v0 = bm_can.verts.new((-0.13, -0.10, 0.88))
c_v1 = bm_can.verts.new((0.13, -0.10, 0.88))
c_v2 = bm_can.verts.new((0.14, 0.08, 0.94))
c_v3 = bm_can.verts.new((-0.14, 0.08, 0.94))
c_v4 = bm_can.verts.new((0.10, 0.18, 0.86))
c_v5 = bm_can.verts.new((-0.10, 0.18, 0.86))
bm_can.faces.new((c_v0, c_v1, c_v2, c_v3))
bm_can.faces.new((c_v3, c_v2, c_v4, c_v5))
mesh_can = bpy.data.meshes.new("CanopyMesh")
bm_can.to_mesh(mesh_can)
bm_can.free()
canopy = bpy.data.objects.new("Part_Canopy", mesh_can)
bpy.context.collection.objects.link(canopy)
canopy.data.materials.append(mat_blue)
sol_can = canopy.modifiers.new("Solidify", 'SOLIDIFY')
sol_can.thickness = 0.015
sol_can.offset = 1.0
bpy.context.view_layer.objects.active = canopy
bpy.ops.object.modifier_apply(modifier="Solidify")
sub_can = canopy.modifiers.new("Subdiv", 'SUBSURF')
sub_can.levels = 2
bpy.ops.object.modifier_apply(modifier="Subdiv")

# Asymmetric Telemetry Fin / Comm Sensor on Left Temple (Sleek, futuristic, warm gold tipped)
bm_fin = bmesh.new()
f0 = bm_fin.verts.new((-0.190, -0.02, 0.81))
f1 = bm_fin.verts.new((-0.205, -0.05, 0.82))
f2 = bm_fin.verts.new((-0.210, 0.06, 0.86))
f3 = bm_fin.verts.new((-0.195, 0.04, 0.84))
bm_fin.faces.new((f0, f1, f2, f3))
mesh_fin = bpy.data.meshes.new("FinMesh")
bm_fin.to_mesh(mesh_fin)
bm_fin.free()
comm_fin = bpy.data.objects.new("Part_CommFin", mesh_fin)
bpy.context.collection.objects.link(comm_fin)
comm_fin.data.materials.append(mat_gold)
sol_f = comm_fin.modifiers.new("Solidify", 'SOLIDIFY')
sol_f.thickness = 0.012
bpy.context.view_layer.objects.active = comm_fin
bpy.ops.object.modifier_apply(modifier="Solidify")

# Low-profile telemetry ports on sides (flush hexagonal sensors, NO big round discs)
sensor_port_l = create_smooth_cylinder("Part_SensL", 0.040, 0.012, (-0.192, 0.01, 0.775), mat_navy, rot=(0, math.radians(90), 0), segs=6)
sensor_port_r = create_smooth_cylinder("Part_SensR", 0.040, 0.012, (0.192, 0.01, 0.775), mat_navy, rot=(0, math.radians(90), 0), segs=6)
gold_rim_r = create_smooth_cylinder("Part_GoldRimR", 0.044, 0.005, (0.195, 0.01, 0.775), mat_gold, rot=(0, math.radians(90), 0), segs=6)

bpy.ops.object.select_all(action='DESELECT')
for p in [visor, eye_l, eye_r, canopy, comm_fin, sensor_port_l, sensor_port_r, gold_rim_r]:
    p.select_set(True)
helmet.select_set(True)
bpy.context.view_layer.objects.active = helmet
bpy.ops.object.join()
BOT_Head = helmet
BOT_Head.name = "BOT_Head"
for p in BOT_Head.data.polygons:
    p.use_smooth = True

# ==================== 2 & 3. BOT_Antenna (Mapped to Comm Fin / Sensors for 13-Bone Rig) ====================
# We maintain the bone handles cleanly in the armature
bm_ant = bmesh.new()
bmesh.ops.create_cube(bm_ant, size=0.01)
mesh_ant = bpy.data.meshes.new("AntennaMesh")
bm_ant.to_mesh(mesh_ant)
bm_ant.free()
BOT_Antenna = bpy.data.objects.new("BOT_Antenna", mesh_ant)
bpy.context.collection.objects.link(BOT_Antenna)
BOT_Antenna.location = (-0.20, 0.0, 0.84)
BOT_Antenna.data.materials.append(mat_gold)

# Dummy Ear handles for strict 20-component hierarchy
def make_dummy_sensor(name, side_sign):
    obj = create_subdiv_box(name, (0.015, 0.015, 0.015), (side_sign * 0.195, 0.01, 0.775), mat_navy, subdiv=1)
    return obj

BOT_Ear_L = make_dummy_sensor("BOT_Ear_L", -1.0)
BOT_Ear_R = make_dummy_sensor("BOT_Ear_R", 1.0)

# ==================== 4. BOT_Scarf -> Replaced by BOT_Collar_Armor (Engineered Cowl) ====================
# An engineered mechanical neck collar in cobalt blue with warm gold articulation rim (NO cloth scarf!)
bm_col = bmesh.new()
col_segs = 24
for i in range(col_segs):
    ang = i / col_segs * 2.0 * math.pi
    r_in = 0.110
    r_out = 0.145 + (0.015 if math.cos(ang) > 0.3 else 0.0) # slightly forward flared
    z_bot = 0.585
    z_top = 0.630 + 0.010 * math.cos(ang)
    x_in = r_in * math.sin(ang)
    y_in = r_in * math.cos(ang) * 0.90
    x_out = r_out * math.sin(ang)
    y_out = r_out * math.cos(ang) * 0.90
    v0 = bm_col.verts.new((x_in, y_in, z_bot))
    v1 = bm_col.verts.new((x_out, y_out, z_bot))
    v2 = bm_col.verts.new((x_out, y_out, z_top))
    v3 = bm_col.verts.new((x_in, y_in, z_top))

bm_col.verts.ensure_lookup_table()
for i in range(col_segs):
    nxt = (i + 1) % col_segs
    idx_curr = i * 4
    idx_nxt = nxt * 4
    # outer face
    bm_col.faces.new((bm_col.verts[idx_curr+1], bm_col.verts[idx_nxt+1], bm_col.verts[idx_nxt+2], bm_col.verts[idx_curr+2]))
    # top rim
    bm_col.faces.new((bm_col.verts[idx_curr+2], bm_col.verts[idx_nxt+2], bm_col.verts[idx_nxt+3], bm_col.verts[idx_curr+3]))
    # inner wall
    bm_col.faces.new((bm_col.verts[idx_curr+3], bm_col.verts[idx_nxt+3], bm_col.verts[idx_nxt+0], bm_col.verts[idx_curr+0]))
    # bottom rim
    bm_col.faces.new((bm_col.verts[idx_curr+0], bm_col.verts[idx_nxt+0], bm_col.verts[idx_nxt+1], bm_col.verts[idx_curr+1]))

mesh_col = bpy.data.meshes.new("CollarMesh")
bm_col.to_mesh(mesh_col)
bm_col.free()
collar = bpy.data.objects.new("BOT_Scarf", mesh_col)
bpy.context.collection.objects.link(collar)
collar.data.materials.append(mat_blue)
sub_c = collar.modifiers.new("Subdiv", 'SUBSURF')
sub_c.levels = 2
bpy.context.view_layer.objects.active = collar
bpy.ops.object.modifier_apply(modifier="Subdiv")

# Front gold status pin on collar
collar_pin = create_subdiv_box("Part_ColPin", (0.024, 0.008, 0.028), (0.0, -0.155, 0.610), mat_gold, subdiv=1)

bpy.ops.object.select_all(action='DESELECT')
collar_pin.select_set(True)
collar.select_set(True)
bpy.context.view_layer.objects.active = collar
bpy.ops.object.join()
BOT_Scarf = collar
BOT_Scarf.name = "BOT_Scarf"
for p in BOT_Scarf.data.polygons:
    p.use_smooth = True

# ==================== 5. BOT_Chest_Armor (Athletic Engineered Explorer Torso) ====================
# Upper chest plate: Sculpted pearl white armor plate with beveled panel lines
chest_main = create_subdiv_box("BOT_Chest_Armor", (0.31, 0.25, 0.22), (0.0, -0.015, 0.495), mat_white, subdiv=3, taper_z=-0.12)

# Deep Cobalt Blue Sub-Chassis Side Insets
blue_flank_l = create_subdiv_box("Part_Flank_L", (0.05, 0.18, 0.16), (0.150, -0.010, 0.490), mat_blue, subdiv=2)
blue_flank_r = create_subdiv_box("Part_Flank_R", (0.05, 0.18, 0.16), (-0.150, -0.010, 0.490), mat_blue, subdiv=2)

# Single Distinctive Energy Core: Horizontal Hexagonal Capsule with Warm Gold Bezel & Cyan Glow
core_bezel = create_subdiv_box("Part_CoreBezel", (0.095, 0.020, 0.055), (0.0, -0.142, 0.510), mat_gold, subdiv=2)
core_glow = create_subdiv_box("Part_CoreGlow", (0.075, 0.014, 0.038), (0.0, -0.147, 0.510), mat_cyan, subdiv=2)

# Dark Graphite Navy Flexible Midriff Chassis (Articulated ribbing between torso and pelvis)
midriff = create_subdiv_box("Part_Midriff", (0.24, 0.19, 0.065), (0.0, 0.0, 0.385), mat_navy, subdiv=2)

bpy.ops.object.select_all(action='DESELECT')
for p in [blue_flank_l, blue_flank_r, core_bezel, core_glow, midriff]:
    p.select_set(True)
chest_main.select_set(True)
bpy.context.view_layer.objects.active = chest_main
bpy.ops.object.join()
BOT_Chest_Armor = chest_main
BOT_Chest_Armor.name = "BOT_Chest_Armor"
for p in BOT_Chest_Armor.data.polygons:
    p.use_smooth = True

# ==================== 6. BOT_Backpack (Integrated Micro-Thruster Module) ====================
# Sleek, low-profile twin-thruster exploration module integrated into the spine
pack_body = create_subdiv_box("BOT_Backpack", (0.20, 0.09, 0.18), (0.0, 0.120, 0.495), mat_blue, subdiv=2)
# Twin microthruster exhaust vents in graphite navy
thruster_l = create_smooth_cylinder("Part_ThrustL", 0.032, 0.035, (0.055, 0.170, 0.465), mat_navy, rot=(math.radians(75), 0, 0), segs=20)
thruster_r = create_smooth_cylinder("Part_ThrustR", 0.032, 0.035, (-0.055, 0.170, 0.465), mat_navy, rot=(math.radians(75), 0, 0), segs=20)
# Horizontal telemetry cyan indicator strip
telemetry = create_subdiv_box("Part_PackTelem", (0.12, 0.008, 0.016), (0.0, 0.170, 0.540), mat_cyan, subdiv=1)

bpy.ops.object.select_all(action='DESELECT')
for p in [thruster_l, thruster_r, telemetry]:
    p.select_set(True)
pack_body.select_set(True)
bpy.context.view_layer.objects.active = pack_body
bpy.ops.object.join()
BOT_Backpack = pack_body
BOT_Backpack.name = "BOT_Backpack"
for p in BOT_Backpack.data.polygons:
    p.use_smooth = True

# ==================== 7. BOT_Pelvis (Articulated Hip Saddle) ====================
pelvis = create_subdiv_box("BOT_Pelvis", (0.22, 0.16, 0.075), (0.0, 0.0, 0.345), mat_white, subdiv=2, taper_z=-0.15)
hip_socket_l = create_smooth_sphere("Part_HipSocL", 0.042, (0.095, 0.0, 0.335), mat_navy, segs=20, rings=16)
hip_socket_r = create_smooth_sphere("Part_HipSocR", 0.042, (-0.095, 0.0, 0.335), mat_navy, segs=20, rings=16)
pelvis_blue_l = create_subdiv_box("Part_PelvBlueL", (0.02, 0.12, 0.06), (0.115, 0.0, 0.345), mat_blue, subdiv=1)
pelvis_blue_r = create_subdiv_box("Part_PelvBlueR", (0.02, 0.12, 0.06), (-0.115, 0.0, 0.345), mat_blue, subdiv=1)

bpy.ops.object.select_all(action='DESELECT')
for p in [hip_socket_l, hip_socket_r, pelvis_blue_l, pelvis_blue_r]:
    p.select_set(True)
pelvis.select_set(True)
bpy.context.view_layer.objects.active = pelvis
bpy.ops.object.join()
BOT_Pelvis = pelvis
BOT_Pelvis.name = "BOT_Pelvis"
for p in BOT_Pelvis.data.polygons:
    p.use_smooth = True

# ==================== 8 & 9. BOT_Arm_L and BOT_Arm_R (Integrated Shoulders & Biceps) ====================
def build_upper_arm(side, sign):
    # Integrated aerodynamic shoulder pauldron: flows smoothly over upper chest
    pauldron = create_subdiv_box(f"BOT_Arm_{side}", (0.070, 0.090, 0.065), (sign * 0.185, 0.0, 0.515), mat_blue, subdiv=2)
    # Tapered white bicep armor
    bicep = create_subdiv_box(f"Part_Bicep_{side}", (0.055, 0.065, 0.085), (sign * 0.188, 0.0, 0.440), mat_white, subdiv=2)
    # Warm gold accent stripe on pauldron
    gold_stripe = create_subdiv_box(f"Part_ArmGold_{side}", (0.008, 0.080, 0.012), (sign * 0.222, 0.0, 0.515), mat_gold, subdiv=1)
    
    bpy.ops.object.select_all(action='DESELECT')
    for p in [bicep, gold_stripe]:
        p.select_set(True)
    pauldron.select_set(True)
    bpy.context.view_layer.objects.active = pauldron
    bpy.ops.object.join()
    pauldron.name = f"BOT_Arm_{side}"
    for p in pauldron.data.polygons:
        p.use_smooth = True
    return pauldron

BOT_Arm_L = build_upper_arm("L", 1.0)
BOT_Arm_R = build_upper_arm("R", -1.0)

# ==================== 10 & 11. BOT_Forearm_L and BOT_Forearm_R ====================
def build_forearm(side, sign):
    # Mechanical elbow hinge joint in graphite navy with warm gold pivot cap
    elbow = create_smooth_cylinder(f"BOT_Forearm_{side}", 0.028, 0.045, (sign * 0.190, 0.0, 0.395), mat_navy, rot=(math.radians(90), 0, 0), segs=20)
    gold_cap = create_smooth_cylinder(f"Part_ElbowCap_{side}", 0.018, 0.050, (sign * 0.190, 0.0, 0.395), mat_gold, rot=(math.radians(90), 0, 0), segs=16)
    # Tapered white forearm gauntlet with faceted silhouette
    gauntlet = create_subdiv_box(f"Part_Gaunt_{side}", (0.065, 0.075, 0.100), (sign * 0.192, 0.0, 0.335), mat_white, subdiv=2, taper_z=-0.15)
    # Recessed cobalt blue lateral conduit
    conduit = create_subdiv_box(f"Part_Conduit_{side}", (0.008, 0.055, 0.060), (sign * 0.228, 0.0, 0.335), mat_blue, subdiv=1)
    
    bpy.ops.object.select_all(action='DESELECT')
    for p in [gold_cap, gauntlet, conduit]:
        p.select_set(True)
    elbow.select_set(True)
    bpy.context.view_layer.objects.active = elbow
    bpy.ops.object.join()
    elbow.name = f"BOT_Forearm_{side}"
    for p in elbow.data.polygons:
        p.use_smooth = True
    return elbow

BOT_Forearm_L = build_forearm("L", 1.0)
BOT_Forearm_R = build_forearm("R", -1.0)

# ==================== 12 & 13. BOT_Hand_L and BOT_Hand_R ====================
def build_hand(side, sign):
    # Compact mechanical explorer hand with palm chassis and 3 articulated digits
    palm = create_subdiv_box(f"BOT_Hand_{side}", (0.052, 0.048, 0.042), (sign * 0.192, 0.0, 0.245), mat_navy, subdiv=2)
    # 2 articulated fingers + 1 opposable thumb
    f0 = create_subdiv_box(f"Part_Fing0_{side}", (0.016, 0.016, 0.036), (sign * 0.192, -0.014, 0.210), mat_navy, subdiv=1)
    f1 = create_subdiv_box(f"Part_Fing1_{side}", (0.016, 0.016, 0.036), (sign * 0.192, 0.014, 0.210), mat_navy, subdiv=1)
    thumb = create_subdiv_box(f"Part_Thumb_{side}", (0.016, 0.022, 0.030), (sign * 0.168, -0.020, 0.230), mat_navy, subdiv=1)
    thumb.rotation_euler = (math.radians(-25), 0, math.radians(sign * 25))
    
    bpy.ops.object.select_all(action='DESELECT')
    for d in [f0, f1, thumb]:
        d.select_set(True)
    palm.select_set(True)
    bpy.context.view_layer.objects.active = palm
    bpy.ops.object.join()
    palm.name = f"BOT_Hand_{side}"
    for p in palm.data.polygons:
        p.use_smooth = True
    return palm

BOT_Hand_L = build_hand("L", 1.0)
BOT_Hand_R = build_hand("R", -1.0)

# ==================== 14 & 15. BOT_Thigh_L and BOT_Thigh_R ====================
def build_thigh(side, sign):
    # Graphite hip gimbal pivot
    hip = create_smooth_sphere(f"BOT_Thigh_{side}", 0.042, (sign * 0.095, 0.0, 0.335), mat_navy, segs=20, rings=16)
    # Sculpted athletic white thigh armor
    thigh_armor = create_subdiv_box(f"Part_ThighArm_{side}", (0.075, 0.085, 0.100), (sign * 0.095, 0.0, 0.270), mat_white, subdiv=2, taper_z=-0.15)
    # Lateral cobalt blue trim insert
    blue_trim = create_subdiv_box(f"Part_ThighTrim_{side}", (0.008, 0.060, 0.070), (sign * 0.135, 0.0, 0.270), mat_blue, subdiv=1)
    
    bpy.ops.object.select_all(action='DESELECT')
    for p in [thigh_armor, blue_trim]:
        p.select_set(True)
    hip.select_set(True)
    bpy.context.view_layer.objects.active = hip
    bpy.ops.object.join()
    hip.name = f"BOT_Thigh_{side}"
    for p in hip.data.polygons:
        p.use_smooth = True
    return hip

BOT_Thigh_L = build_thigh("L", 1.0)
BOT_Thigh_R = build_thigh("R", -1.0)

# ==================== 16 & 17. BOT_Shin_L and BOT_Shin_R ====================
def build_shin(side, sign):
    # Clean mechanical knee joint in graphite navy
    knee = create_smooth_cylinder(f"BOT_Shin_{side}", 0.034, 0.040, (sign * 0.095, -0.002, 0.220), mat_navy, rot=(0, math.radians(90), 0), segs=20)
    # Protective knee cap armor plate in cobalt blue
    knee_cap = create_subdiv_box(f"Part_KneeCap_{side}", (0.055, 0.025, 0.045), (sign * 0.095, -0.025, 0.220), mat_blue, subdiv=2)
    # Tapered forward-angled white shin armor
    shin_armor = create_subdiv_box(f"Part_ShinArm_{side}", (0.080, 0.090, 0.110), (sign * 0.095, -0.005, 0.165), mat_white, subdiv=2)
    # Gold telemetry bolt
    gold_bolt = create_smooth_sphere(f"Part_ShinBolt_{side}", 0.008, (sign * 0.140, -0.005, 0.165), mat_gold, segs=12, rings=8)
    
    bpy.ops.object.select_all(action='DESELECT')
    for p in [knee_cap, shin_armor, gold_bolt]:
        p.select_set(True)
    knee.select_set(True)
    bpy.context.view_layer.objects.active = knee
    bpy.ops.object.join()
    knee.name = f"BOT_Shin_{side}"
    for p in knee.data.polygons:
        p.use_smooth = True
    return knee

BOT_Shin_L = build_shin("L", 1.0)
BOT_Shin_R = build_shin("R", -1.0)

# ==================== 18 & 19. BOT_Boot_L and BOT_Boot_R ====================
def build_boot(side, sign):
    # Futuristic all-terrain explorer boot: integrated aerodynamic silhouette
    # Main white upper shell with forward taper
    body = create_subdiv_box(f"BOT_Boot_{side}", (0.095, 0.155, 0.075), (sign * 0.095, 0.010, 0.072), mat_white, subdiv=2)
    # Integrated front bumper in cobalt blue (cleanly contoured into shoe lines, NOT a separate yellow clown ball)
    bumper = create_subdiv_box(f"Part_Bumper_{side}", (0.092, 0.055, 0.055), (sign * 0.095, -0.065, 0.055), mat_blue, subdiv=2)
    # Contoured runner sole in dark graphite navy with tread profile
    sole = create_subdiv_box(f"Part_Sole_{side}", (0.100, 0.170, 0.024), (sign * 0.095, -0.010, 0.024), mat_navy, subdiv=1)
    # Warm gold side stabilizer accent
    gold_acc = create_subdiv_box(f"Part_BootGold_{side}", (0.008, 0.045, 0.016), (sign * 0.148, 0.005, 0.055), mat_gold, subdiv=1)
    # Subtle rear cyan telemetry slit
    heel_light = create_subdiv_box(f"Part_BootGlow_{side}", (0.045, 0.006, 0.012), (sign * 0.095, 0.088, 0.055), mat_cyan, subdiv=1)
    
    bpy.ops.object.select_all(action='DESELECT')
    for p in [bumper, sole, gold_acc, heel_light]:
        p.select_set(True)
    body.select_set(True)
    bpy.context.view_layer.objects.active = body
    bpy.ops.object.join()
    body.name = f"BOT_Boot_{side}"
    for p in body.data.polygons:
        p.use_smooth = True
    return body

BOT_Boot_L = build_boot("L", 1.0)
BOT_Boot_R = build_boot("R", -1.0)

components = [
    BOT_Head, BOT_Antenna, BOT_Ear_L, BOT_Ear_R, BOT_Scarf,
    BOT_Chest_Armor, BOT_Backpack, BOT_Pelvis,
    BOT_Arm_L, BOT_Arm_R, BOT_Forearm_L, BOT_Forearm_R,
    BOT_Hand_L, BOT_Hand_R, BOT_Thigh_L, BOT_Thigh_R,
    BOT_Shin_L, BOT_Shin_R, BOT_Boot_L, BOT_Boot_R
]
print(f"Constructed {len(components)} deliberate modern explorer components.")

# ---------------------------------------------------------
# 4. Rigging: 13-Bone Deformation Armature
# ---------------------------------------------------------
armature_data = bpy.data.armatures.new("Armature")
armature_obj = bpy.data.objects.new("BOT_Armature", armature_data)
bpy.context.collection.objects.link(armature_obj)
bpy.context.view_layer.objects.active = armature_obj
bpy.ops.object.mode_set(mode='EDIT')

edit_bones = armature_data.edit_bones

# 1. Root
b_root = edit_bones.new("Root")
b_root.head = (0, 0, 0)
b_root.tail = (0, 0, 0.38)

# 2. Torso
b_torso = edit_bones.new("Torso")
b_torso.head = (0, 0, 0.38)
b_torso.tail = (0, 0, 0.65)
b_torso.parent = b_root

# 3. Head
b_head = edit_bones.new("Head")
b_head.head = (0, 0, 0.65)
b_head.tail = (0, 0, 0.98)
b_head.parent = b_torso

# 4 & 5. Antenna.L and Antenna.R (retained for 100% bone compatibility)
b_ant_l = edit_bones.new("Antenna.L")
b_ant_l.head = (-0.05, 0.0, 0.80)
b_ant_l.tail = (-0.08, 0.04, 0.88)
b_ant_l.parent = b_head

b_ant_r = edit_bones.new("Antenna.R")
b_ant_r.head = (0.05, 0.0, 0.80)
b_ant_r.tail = (0.08, 0.04, 0.88)
b_ant_r.parent = b_head

# 6 & 7. Arm.L & Hand.L
b_arm_l = edit_bones.new("Arm.L")
b_arm_l.head = (0.18, 0.0, 0.52)
b_arm_l.tail = (0.19, 0.0, 0.35)
b_arm_l.parent = b_torso

b_hand_l = edit_bones.new("Hand.L")
b_hand_l.head = (0.19, 0.0, 0.35)
b_hand_l.tail = (0.19, 0.0, 0.20)
b_hand_l.parent = b_arm_l

# 8 & 9. Arm.R & Hand.R
b_arm_r = edit_bones.new("Arm.R")
b_arm_r.head = (-0.18, 0.0, 0.52)
b_arm_r.tail = (-0.19, 0.0, 0.35)
b_arm_r.parent = b_torso

b_hand_r = edit_bones.new("Hand.R")
b_hand_r.head = (-0.19, 0.0, 0.35)
b_hand_r.tail = (-0.19, 0.0, 0.20)
b_hand_r.parent = b_arm_r

# 10 & 11. Leg.L & Foot.L
b_leg_l = edit_bones.new("Leg.L")
b_leg_l.head = (0.095, 0.0, 0.35)
b_leg_l.tail = (0.095, 0.0, 0.17)
b_leg_l.parent = b_root

b_foot_l = edit_bones.new("Foot.L")
b_foot_l.head = (0.095, 0.0, 0.17)
b_foot_l.tail = (0.095, -0.06, 0.02)
b_foot_l.parent = b_leg_l

# 12 & 13. Leg.R & Foot.R
b_leg_r = edit_bones.new("Leg.R")
b_leg_r.head = (-0.095, 0.0, 0.35)
b_leg_r.tail = (-0.095, 0.0, 0.17)
b_leg_r.parent = b_root

b_foot_r = edit_bones.new("Foot.R")
b_foot_r.head = (-0.095, 0.0, 0.17)
b_foot_r.tail = (-0.095, -0.06, 0.02)
b_foot_r.parent = b_leg_r

bpy.ops.object.mode_set(mode='OBJECT')

# ---------------------------------------------------------
# 5. Skinning & Vertex Groups Binding
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
    
    for b_name in all_bone_names:
        vg = comp.vertex_groups.new(name=b_name)
        if b_name == target_bone:
            v_indices = [v.index for v in comp.data.vertices]
            vg.add(v_indices, 1.0, 'REPLACE')
            
    mod = comp.modifiers.new("Armature", 'ARMATURE')
    mod.object = armature_obj

print("Armature binding and vertex groups mapped.")

# ---------------------------------------------------------
# 6. Save Separate Candidate Blender File (DO NOT overwrite active model)
# ---------------------------------------------------------
candidate_blend_path = "/Users/it/Documents/TINY PLANET/assets/blender/source/candidates/bot_modern_explorer_candidate.blend"
bpy.ops.wm.save_as_mainfile(filepath=candidate_blend_path)
print(f"Saved Candidate Blend File to: {candidate_blend_path}")

# ---------------------------------------------------------
# 7. Professional Studio Lighting & Render Setup
# ---------------------------------------------------------
# Studio Floor
ground = create_smooth_cylinder("StudioFloor", 4.0, 0.02, (0, 0, -0.01), get_mat("Mat_StudioFloor", (0.92, 0.93, 0.96, 1.0), roughness=0.35), segs=40)

# Studio 3-Point Lighting
light_key = bpy.data.lights.new("KeyLight", 'AREA')
light_key.energy = 340.0
light_key.size = 2.4
light_key.color = (1.0, 0.98, 0.95)
obj_key = bpy.data.objects.new("KeyLight", light_key)
bpy.context.collection.objects.link(obj_key)
obj_key.location = (-1.8, -2.6, 2.2)
obj_key.rotation_euler = (math.radians(52), 0, math.radians(-35))

light_fill = bpy.data.lights.new("FillLight", 'AREA')
light_fill.energy = 160.0
light_fill.size = 3.0
light_fill.color = (0.86, 0.93, 1.0)
obj_fill = bpy.data.objects.new("FillLight", light_fill)
bpy.context.collection.objects.link(obj_fill)
obj_fill.location = (2.4, -1.8, 1.5)
obj_fill.rotation_euler = (math.radians(48), 0, math.radians(52))

light_rim = bpy.data.lights.new("RimLight", 'SPOT')
light_rim.energy = 420.0
light_rim.spot_size = math.radians(70)
light_rim.color = (0.40, 0.85, 1.0)
obj_rim = bpy.data.objects.new("RimLight", light_rim)
bpy.context.collection.objects.link(obj_rim)
obj_rim.location = (0.0, 2.4, 2.2)
obj_rim.rotation_euler = (math.radians(-50), 0, math.radians(180))

# Camera setup
cam_data = bpy.data.cameras.new("RenderCam")
cam_data.lens = 75.0
cam_obj = bpy.data.objects.new("RenderCam", cam_data)
bpy.context.collection.objects.link(cam_obj)
bpy.context.scene.camera = cam_obj

bpy.context.scene.render.resolution_x = 1200
bpy.context.scene.render.resolution_y = 1000
bpy.context.scene.render.engine = 'BLENDER_EEVEE_NEXT' if hasattr(bpy.types, 'RenderEngineEEVEE_NEXT') else 'BLENDER_EEVEE'

out_dir = "/Users/it/.gemini/antigravity/brain/0e7dd031-e455-469e-95de-196677cac497"

# Required full-body and close-up views:
# 1. Front view
# 2. Back view
# 3. Left view
# 4. Right view
# 5. Three-quarter view
# 6. Face close-up
# 7. Torso close-up
views = [
    ("candidate_front.png", (0.0, -2.4, 0.58), (math.radians(87), 0, 0), 75.0),
    ("candidate_back.png", (0.0, 2.4, 0.58), (math.radians(93), 0, math.radians(180)), 75.0),
    ("candidate_left.png", (2.4, 0.0, 0.58), (math.radians(87), 0, math.radians(90)), 75.0),
    ("candidate_right.png", (-2.4, 0.0, 0.58), (math.radians(87), 0, math.radians(-90)), 75.0),
    ("candidate_34.png", (-1.7, -1.7, 0.68), (math.radians(80), 0, math.radians(-45)), 75.0),
    ("candidate_face.png", (0.0, -1.2, 0.775), (math.radians(88), 0, 0), 105.0),
    ("candidate_torso.png", (0.0, -1.3, 0.490), (math.radians(88), 0, 0), 95.0),
]

for filename, pos, rot, lens in views:
    cam_obj.location = pos
    cam_obj.rotation_euler = rot
    cam_data.lens = lens
    filepath = os.path.join(out_dir, filename)
    bpy.context.scene.render.filepath = filepath
    bpy.ops.render.render(write_still=True)
    print(f"Rendered view: {filepath}")

# ---------------------------------------------------------
# 8. Black Silhouette Render (Pure Black Shader on White Background)
# ---------------------------------------------------------
mat_pure_black = get_mat("Mat_PureBlack", (0.0, 0.0, 0.0, 1.0), roughness=1.0)
# Temporarily override floor to pure white emissive
mat_pure_white = get_mat("Mat_PureWhite", (1.0, 1.0, 1.0, 1.0), emission_color=(1,1,1,1), emission_strength=1.0)
ground.data.materials[0] = mat_pure_white

orig_mats = {}
for comp in components:
    orig_mats[comp.name] = [m for m in comp.data.materials]
    comp.data.materials.clear()
    comp.data.materials.append(mat_pure_black)

# Disable lights for pure silhouette
obj_key.data.energy = 0
obj_fill.data.energy = 0
obj_rim.data.energy = 0

cam_obj.location = (-1.7, -1.7, 0.68)
cam_obj.rotation_euler = (math.radians(80), 0, math.radians(-45))
cam_data.lens = 75.0
sil_path = os.path.join(out_dir, "candidate_silhouette.png")
bpy.context.scene.render.filepath = sil_path
bpy.ops.render.render(write_still=True)
print(f"Rendered silhouette: {sil_path}")

print("Candidate generation, rendering, and silhouette completed successfully!")
