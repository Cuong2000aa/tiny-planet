"""
B.O.T Production 3D Character Generator — Astro Bot Style Master Pass
Tiny Planet - High-Quality Stylized 3D Adventure Protagonist
Inspired by Astro Bot: Chibi proportions, glossy ceramic finish, cyan LED expressions,
yellow flying scarf/cape, ear speakers, sprout antenna, and glowing thruster boots.
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
# 1. Astro Bot PBR Materials (Glossy Ceramic & Vibrant Neon)
# ---------------------------------------------------------
materials = {}

def get_mat(name, base_color, metallic=0.0, roughness=0.20, emission_color=(0,0,0,1), emission_strength=0.0, clearcoat=0.0):
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

# Tactile premium palette matching Astro Bot
mat_white  = get_mat("Mat_Ceramic_White", (0.95, 0.95, 0.97, 1.0), metallic=0.02, roughness=0.12, clearcoat=0.55)
mat_blue   = get_mat("Mat_Royal_Blue",    (0.05, 0.28, 0.88, 1.0), metallic=0.10, roughness=0.16, clearcoat=0.35)
mat_yellow = get_mat("Mat_Sunny_Yellow",  (0.98, 0.72, 0.05, 1.0), metallic=0.0,  roughness=0.28)
mat_visor  = get_mat("Mat_Obsidian_Visor",(0.008, 0.010, 0.015, 1.0), metallic=0.95, roughness=0.02, clearcoat=1.0)
mat_cyan   = get_mat("Mat_Cyan_Neon",     (0.15, 0.90, 1.0, 1.0),  metallic=0.0,  roughness=0.05, emission_color=(0.15, 0.90, 1.0, 1.0), emission_strength=5.5)
mat_navy   = get_mat("Mat_Graphite_Joint",(0.12, 0.14, 0.18, 1.0), metallic=0.60, roughness=0.28)

# ---------------------------------------------------------
# 2. Geometry Helpers
# ---------------------------------------------------------
def create_subdiv_box(name, dims, loc, mat, subdiv=2, smooth=True, taper_z=None):
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
# 3. Build 20 Astro Bot Style Components (~2.5 Heads Tall)
# Total height: ~0.96m. Forward is -Y (Godot -Z)
# ---------------------------------------------------------

Z_HEAD     = 0.730
Z_COLLAR   = 0.565
Z_TORSO    = 0.460
Z_PELVIS   = 0.310
Z_SHOULDER = 0.485
Z_ELBOW    = 0.370
Z_HAND     = 0.245
Z_KNEE     = 0.190
Z_BOOT     = 0.065

# ==================== 1. BOT_Head (Astro Bot Round Helmet & Curved Visor) ====================
# Cute rounded dome helmet (slightly wider than tall, perfectly chibi)
head_shell = create_smooth_sphere("BOT_Head", 0.215, (0.0, 0.0, Z_HEAD), mat_white, segs=40, rings=32, scale=(1.06, 0.98, 0.92))

# Smooth convex panoramic black glass visor seamlessly recessed into front face (-Y)
visor = create_subdiv_box("Part_Visor", (0.32, 0.12, 0.22), (0.0, -0.115, Z_HEAD), mat_visor, subdiv=3)
for v in visor.data.vertices:
    if v.co.y < 0:
        v.co.y -= 0.028 * (1.0 - (v.co.x/0.18)**2 - (v.co.z/0.13)**2 if abs(v.co.x)<0.18 and abs(v.co.z)<0.13 else 0)

# Signature Astro Bot Cyan LED Eyes: expressive vertical capsules with rounded caps, tilted slightly inward
eye_l = create_smooth_sphere("Part_Eye_L", 0.035, (-0.072, -0.192, Z_HEAD + 0.005), mat_cyan, segs=24, rings=18, scale=(0.85, 0.14, 1.45))
eye_l.rotation_euler = (0, 0, math.radians(-2.5))
eye_r = create_smooth_sphere("Part_Eye_R", 0.035, (0.072, -0.192, Z_HEAD + 0.005), mat_cyan, segs=24, rings=18, scale=(0.85, 0.14, 1.45))
eye_r.rotation_euler = (0, 0, math.radians(2.5))

# Royal Blue Helmet Crown / Cap (sweeps smoothly over forehead and down the back)
bm_cr = bmesh.new()
verts_cr = []
for x_f in [-0.15, -0.075, 0.0, 0.075, 0.15]:
    z_f = (Z_HEAD + 0.09) - (x_f**2)*0.6
    verts_cr.append(bm_cr.verts.new((x_f, -0.11, z_f)))
for x_f in [-0.17, -0.085, 0.0, 0.085, 0.17]:
    z_f = (Z_HEAD + 0.19) - (x_f**2)*0.5
    verts_cr.append(bm_cr.verts.new((x_f, 0.0, z_f)))
for x_f in [-0.16, -0.08, 0.0, 0.08, 0.16]:
    z_f = (Z_HEAD + 0.13) - (x_f**2)*0.5
    verts_cr.append(bm_cr.verts.new((x_f, 0.13, z_f)))
for x_f in [-0.14, -0.07, 0.0, 0.07, 0.14]:
    z_f = (Z_HEAD + 0.01) - (x_f**2)*0.4
    verts_cr.append(bm_cr.verts.new((x_f, 0.18, z_f)))

bm_cr.verts.ensure_lookup_table()
for r in range(3):
    for c in range(4):
        bm_cr.faces.new((
            bm_cr.verts[r*5 + c],
            bm_cr.verts[r*5 + c + 1],
            bm_cr.verts[(r+1)*5 + c + 1],
            bm_cr.verts[(r+1)*5 + c]
        ))

mesh_cr = bpy.data.meshes.new("CrownMesh")
bm_cr.to_mesh(mesh_cr)
bm_cr.free()
crown = bpy.data.objects.new("Part_Crown", mesh_cr)
bpy.context.collection.objects.link(crown)
crown.data.materials.append(mat_blue)
sol_cr = crown.modifiers.new("Solidify", 'SOLIDIFY')
sol_cr.thickness = 0.015
sol_cr.offset = 1.0
bpy.context.view_layer.objects.active = crown
bpy.ops.object.modifier_apply(modifier="Solidify")
sub_cr = crown.modifiers.new("Subdiv", 'SUBSURF')
sub_cr.levels = 3
bpy.ops.object.modifier_apply(modifier="Subdiv")

bpy.ops.object.select_all(action='DESELECT')
for p in [crown, visor, eye_l, eye_r]:
    p.select_set(True)
head_shell.select_set(True)
bpy.context.view_layer.objects.active = head_shell
bpy.ops.object.join()
BOT_Head = head_shell
BOT_Head.name = "BOT_Head"
for p in BOT_Head.data.polygons:
    p.use_smooth = True

# ==================== 2. BOT_Antenna (Playful Sprout on Top) ====================
stem = create_smooth_cylinder("Part_AntStem", 0.011, 0.045, (0.0, 0.01, Z_HEAD + 0.195), mat_yellow, rot=(math.radians(14), 0, 0), segs=16)

bm_sp = bmesh.new()
v0 = bm_sp.verts.new((0.0, 0.00, Z_HEAD + 0.210))
v1 = bm_sp.verts.new((0.0, 0.035, Z_HEAD + 0.255))
v2 = bm_sp.verts.new((0.0, 0.070, Z_HEAD + 0.285))
v3 = bm_sp.verts.new((0.0, 0.095, Z_HEAD + 0.265))
v4 = bm_sp.verts.new((0.0, 0.080, Z_HEAD + 0.235))
v5 = bm_sp.verts.new((0.0, 0.035, Z_HEAD + 0.215))
bm_sp.faces.new((v0, v1, v2, v3, v4, v5))
mesh_sp = bpy.data.meshes.new("SproutMesh")
bm_sp.to_mesh(mesh_sp)
bm_sp.free()
sprout = bpy.data.objects.new("Part_Sprout", mesh_sp)
bpy.context.collection.objects.link(sprout)
sprout.data.materials.append(mat_yellow)
sol_sp = sprout.modifiers.new("Solidify", 'SOLIDIFY')
sol_sp.thickness = 0.022
sol_sp.offset = 0.0
bpy.context.view_layer.objects.active = sprout
bpy.ops.object.modifier_apply(modifier="Solidify")
sub_sp = sprout.modifiers.new("Subdiv", 'SUBSURF')
sub_sp.levels = 2
bpy.ops.object.modifier_apply(modifier="Subdiv")

bpy.ops.object.select_all(action='DESELECT')
stem.select_set(True)
sprout.select_set(True)
bpy.context.view_layer.objects.active = sprout
bpy.ops.object.join()
BOT_Antenna = sprout
BOT_Antenna.name = "BOT_Antenna"
for p in BOT_Antenna.data.polygons:
    p.use_smooth = True

# ==================== 3 & 4. BOT_Ear_L and BOT_Ear_R (Concentric Audio Speaker Discs) ====================
def build_ear(side, sign):
    # Outer yellow chamfer ring
    base = create_smooth_cylinder(f"BOT_Ear_{side}", 0.085, 0.026, (sign * 0.222, -0.01, Z_HEAD), mat_yellow, rot=(0, math.radians(90), 0), segs=32, bevel_width=0.005)
    # Royal blue inner bezel
    housing = create_smooth_cylinder(f"Part_EarHouse_{side}", 0.070, 0.020, (sign * 0.230, -0.01, Z_HEAD), mat_blue, rot=(0, math.radians(90), 0), segs=32, bevel_width=0.004)
    # Concentric glowing cyan ring
    ring = create_smooth_cylinder(f"Part_EarRing_{side}", 0.050, 0.012, (sign * 0.236, -0.01, Z_HEAD), mat_cyan, rot=(0, math.radians(90), 0), segs=32, bevel_width=0.002)
    # Dark graphite center hub
    hub = create_smooth_cylinder(f"Part_EarHub_{side}", 0.026, 0.014, (sign * 0.240, -0.01, Z_HEAD), mat_navy, rot=(0, math.radians(90), 0), segs=24)
    
    bpy.ops.object.select_all(action='DESELECT')
    for p in [housing, ring, hub]:
        p.select_set(True)
    base.select_set(True)
    bpy.context.view_layer.objects.active = base
    bpy.ops.object.join()
    base.name = f"BOT_Ear_{side}"
    for p in base.data.polygons:
        p.use_smooth = True
    return base

BOT_Ear_L = build_ear("L", 1.0)
BOT_Ear_R = build_ear("R", -1.0)

# ==================== 5. BOT_Scarf (Astro Bot Yellow Cape & Scarf with Emblem) ====================
bm_cowl = bmesh.new()
segments = 28
rings = 4
for ring_idx in range(rings):
    z = (Z_TORSO + 0.09) + ring_idx * 0.020
    r_outer = 0.170 + (0.012 if ring_idx in [1, 2] else 0.0)
    for seg in range(segments):
        angle = seg / segments * 2.0 * math.pi
        y_bias = -0.016 * math.cos(angle)
        fold = 0.008 * math.sin(angle * 4)
        x = (r_outer + fold) * math.sin(angle)
        y = (r_outer * 0.88 + y_bias + fold) * math.cos(angle)
        bm_cowl.verts.new((x, y, z))

bm_cowl.verts.ensure_lookup_table()
for ring_idx in range(rings - 1):
    for seg in range(segments):
        next_seg = (seg + 1) % segments
        bm_cowl.faces.new((
            bm_cowl.verts[ring_idx * segments + seg],
            bm_cowl.verts[ring_idx * segments + next_seg],
            bm_cowl.verts[(ring_idx + 1) * segments + next_seg],
            bm_cowl.verts[(ring_idx + 1) * segments + seg]
        ))
mesh_cowl = bpy.data.meshes.new("ScarfCowl")
bm_cowl.to_mesh(mesh_cowl)
bm_cowl.free()
cowl = bpy.data.objects.new("BOT_Scarf", mesh_cowl)
bpy.context.collection.objects.link(cowl)
cowl.data.materials.append(mat_yellow)
sol_cowl = cowl.modifiers.new("Solidify", 'SOLIDIFY')
sol_cowl.thickness = 0.015
sol_cowl.offset = 1.0
bpy.context.view_layer.objects.active = cowl
bpy.ops.object.modifier_apply(modifier="Solidify")
sub_cowl = cowl.modifiers.new("Subdiv", 'SUBSURF')
sub_cowl.levels = 2
bpy.ops.object.modifier_apply(modifier="Subdiv")

# Front folded kerchief bib pointing down (-Y)
bm_bib = bmesh.new()
v_top_l = bm_bib.verts.new((-0.072, -0.150, Z_TORSO + 0.13))
v_top_r = bm_bib.verts.new((0.072, -0.150, Z_TORSO + 0.13))
v_mid_l = bm_bib.verts.new((-0.062, -0.160, Z_TORSO + 0.08))
v_mid_r = bm_bib.verts.new((0.062, -0.160, Z_TORSO + 0.08))
v_tip   = bm_bib.verts.new((0.0, -0.155, Z_TORSO + 0.025))
bm_bib.faces.new((v_top_l, v_top_r, v_mid_r, v_mid_l))
bm_bib.faces.new((v_mid_l, v_mid_r, v_tip))
mesh_bib = bpy.data.meshes.new("BibMesh")
bm_bib.to_mesh(mesh_bib)
bm_bib.free()
obj_bib = bpy.data.objects.new("Part_Bib", mesh_bib)
bpy.context.collection.objects.link(obj_bib)
obj_bib.data.materials.append(mat_yellow)
sol_bib = obj_bib.modifiers.new("Solidify", 'SOLIDIFY')
sol_bib.thickness = 0.012
sol_bib.offset = 1.0
bpy.context.view_layer.objects.active = obj_bib
bpy.ops.object.modifier_apply(modifier="Solidify")
sub_bib = obj_bib.modifiers.new("Subdiv", 'SUBSURF')
sub_bib.levels = 2
bpy.ops.object.modifier_apply(modifier="Subdiv")

# Scarf Bib Emblem (Dark Blue Triangle + Glowing Cyan Chevron)
bm_em = bmesh.new()
b_v0 = bm_em.verts.new((-0.036, -0.168, Z_TORSO + 0.095))
b_v1 = bm_em.verts.new((0.036, -0.168, Z_TORSO + 0.095))
b_v2 = bm_em.verts.new((0.0, -0.164, Z_TORSO + 0.048))
bm_em.faces.new((b_v0, b_v1, b_v2))
mesh_em = bpy.data.meshes.new("ScarfEmblem")
bm_em.to_mesh(mesh_em)
bm_em.free()
obj_em = bpy.data.objects.new("Part_ScarfEmblem", mesh_em)
bpy.context.collection.objects.link(obj_em)
obj_em.data.materials.append(mat_blue)
sol_em = obj_em.modifiers.new("Solidify", 'SOLIDIFY')
sol_em.thickness = 0.007
bpy.context.view_layer.objects.active = obj_em
bpy.ops.object.modifier_apply(modifier="Solidify")

bm_ch = bmesh.new()
c_v0 = bm_ch.verts.new((-0.018, -0.174, Z_TORSO + 0.088))
c_v1 = bm_ch.verts.new((0.018, -0.174, Z_TORSO + 0.088))
c_v2 = bm_ch.verts.new((0.0, -0.170, Z_TORSO + 0.060))
bm_ch.faces.new((c_v0, c_v1, c_v2))
mesh_ch = bpy.data.meshes.new("ScarfChevron")
bm_ch.to_mesh(mesh_ch)
bm_ch.free()
obj_ch = bpy.data.objects.new("Part_ScarfChevron", mesh_ch)
bpy.context.collection.objects.link(obj_ch)
obj_ch.data.materials.append(mat_cyan)
sol_ch = obj_ch.modifiers.new("Solidify", 'SOLIDIFY')
sol_ch.thickness = 0.005
bpy.context.view_layer.objects.active = obj_ch
bpy.ops.object.modifier_apply(modifier="Solidify")

# Flowing Cape Tails behind shoulders
def create_scarf_tail(name, side_sign):
    bm = bmesh.new()
    t0 = bm.verts.new((side_sign * 0.06, 0.145, Z_TORSO + 0.11))
    t1 = bm.verts.new((side_sign * 0.11, 0.145, Z_TORSO + 0.11))
    t2 = bm.verts.new((side_sign * 0.15, 0.22, Z_TORSO + 0.05))
    t3 = bm.verts.new((side_sign * 0.08, 0.21, Z_TORSO + 0.05))
    t4 = bm.verts.new((side_sign * 0.17, 0.27, Z_TORSO - 0.01))
    bm.faces.new((t0, t1, t2, t3))
    bm.faces.new((t3, t2, t4))
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(mat_yellow)
    sol = obj.modifiers.new("Solidify", 'SOLIDIFY')
    sol.thickness = 0.012
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_apply(modifier="Solidify")
    sub = obj.modifiers.new("Subdiv", 'SUBSURF')
    sub.levels = 2
    bpy.ops.object.modifier_apply(modifier="Subdiv")
    return obj

tail_l = create_scarf_tail("Part_Tail_L", 1.0)
tail_r = create_scarf_tail("Part_Tail_R", -1.0)

bpy.ops.object.select_all(action='DESELECT')
for p in [obj_bib, obj_em, obj_ch, tail_l, tail_r]:
    p.select_set(True)
cowl.select_set(True)
bpy.context.view_layer.objects.active = cowl
bpy.ops.object.join()
BOT_Scarf = cowl
BOT_Scarf.name = "BOT_Scarf"
for p in BOT_Scarf.data.polygons:
    p.use_smooth = True

# ==================== 6. BOT_Chest_Armor (Cute Rounded White Torso with Inverted Triangle Reactor) ====================
torso_body = create_smooth_sphere("BOT_Chest_Armor", 0.180, (0.0, 0.0, Z_TORSO), mat_white, segs=36, rings=28, scale=(0.96, 0.88, 1.00))

# Chest Reactor: Recessed inverted glowing cyan triangle with blue bezel
bm_cr = bmesh.new()
cr_0 = bm_cr.verts.new((-0.042, -0.155, Z_TORSO + 0.020))
cr_1 = bm_cr.verts.new((0.042, -0.155, Z_TORSO + 0.020))
cr_2 = bm_cr.verts.new((0.0, -0.150, Z_TORSO - 0.038))
bm_cr.faces.new((cr_0, cr_1, cr_2))
mesh_cr = bpy.data.meshes.new("ChestCoreBezel")
bm_cr.to_mesh(mesh_cr)
bm_cr.free()
obj_cr_bezel = bpy.data.objects.new("Part_ChestBezel", mesh_cr)
bpy.context.collection.objects.link(obj_cr_bezel)
obj_cr_bezel.data.materials.append(mat_blue)
sol_b = obj_cr_bezel.modifiers.new("Solidify", 'SOLIDIFY')
sol_b.thickness = 0.012
bpy.context.view_layer.objects.active = obj_cr_bezel
bpy.ops.object.modifier_apply(modifier="Solidify")

bm_core = bmesh.new()
co_0 = bm_core.verts.new((-0.030, -0.160, Z_TORSO + 0.014))
co_1 = bm_core.verts.new((0.030, -0.160, Z_TORSO + 0.014))
co_2 = bm_core.verts.new((0.0, -0.155, Z_TORSO - 0.028))
bm_core.faces.new((co_0, co_1, co_2))
mesh_core = bpy.data.meshes.new("ChestCoreGlow")
bm_core.to_mesh(mesh_core)
bm_core.free()
obj_core = bpy.data.objects.new("Part_ChestCore", mesh_core)
bpy.context.collection.objects.link(obj_core)
obj_core.data.materials.append(mat_cyan)
sol_c = obj_core.modifiers.new("Solidify", 'SOLIDIFY')
sol_c.thickness = 0.009
bpy.context.view_layer.objects.active = obj_core
bpy.ops.object.modifier_apply(modifier="Solidify")

waist = create_smooth_cylinder("Part_Waist", 0.120, 0.045, (0.0, 0.0, Z_TORSO - 0.100), mat_navy, segs=32, bevel_width=0.006)

bpy.ops.object.select_all(action='DESELECT')
for p in [obj_cr_bezel, obj_core, waist]:
    p.select_set(True)
torso_body.select_set(True)
bpy.context.view_layer.objects.active = torso_body
bpy.ops.object.join()
BOT_Chest_Armor = torso_body
BOT_Chest_Armor.name = "BOT_Chest_Armor"
for p in BOT_Chest_Armor.data.polygons:
    p.use_smooth = True

# ==================== 7. BOT_Backpack (Astro Jetpack with Glowing Inverted Triangle) ====================
pack = create_subdiv_box("BOT_Backpack", (0.185, 0.085, 0.165), (0.0, 0.130, Z_TORSO + 0.010), mat_blue, subdiv=3)

# Inverted glowing cyan triangle
bm_bp = bmesh.new()
bp_0 = bm_bp.verts.new((-0.035, 0.178, Z_TORSO + 0.040))
bp_1 = bm_bp.verts.new((0.035, 0.178, Z_TORSO + 0.040))
bp_2 = bm_bp.verts.new((0.0, 0.178, Z_TORSO - 0.015))
bm_bp.faces.new((bp_0, bp_1, bp_2))
mesh_bp = bpy.data.meshes.new("PackGlow")
bm_bp.to_mesh(mesh_bp)
bm_bp.free()
obj_bp_glow = bpy.data.objects.new("Part_PackGlow", mesh_bp)
bpy.context.collection.objects.link(obj_bp_glow)
obj_bp_glow.data.materials.append(mat_cyan)
sol_bp = obj_bp_glow.modifiers.new("Solidify", 'SOLIDIFY')
sol_bp.thickness = 0.008
bpy.context.view_layer.objects.active = obj_bp_glow
bpy.ops.object.modifier_apply(modifier="Solidify")

bpy.ops.object.select_all(action='DESELECT')
obj_bp_glow.select_set(True)
pack.select_set(True)
bpy.context.view_layer.objects.active = pack
bpy.ops.object.join()
BOT_Backpack = pack
BOT_Backpack.name = "BOT_Backpack"
for p in BOT_Backpack.data.polygons:
    p.use_smooth = True

# ==================== 8. BOT_Pelvis (Smooth White Hip Saddle) ====================
pelvis = create_subdiv_box("BOT_Pelvis", (0.21, 0.15, 0.070), (0.0, 0.0, Z_PELVIS), mat_white, subdiv=3)
hip_socket_l = create_smooth_sphere("Part_Hip_L", 0.042, (0.095, 0.0, Z_PELVIS - 0.010), mat_navy, segs=24, rings=18)
hip_socket_r = create_smooth_sphere("Part_Hip_R", 0.042, (-0.095, 0.0, Z_PELVIS - 0.010), mat_navy, segs=24, rings=18)

bpy.ops.object.select_all(action='DESELECT')
for p in [hip_socket_l, hip_socket_r]:
    p.select_set(True)
pelvis.select_set(True)
bpy.context.view_layer.objects.active = pelvis
bpy.ops.object.join()
BOT_Pelvis = pelvis
BOT_Pelvis.name = "BOT_Pelvis"
for p in BOT_Pelvis.data.polygons:
    p.use_smooth = True

# ==================== 9 & 10. BOT_Arm_L and BOT_Arm_R (Shoulder Caps & Biceps) ====================
def build_upper_arm(side, sign):
    pivot = create_smooth_sphere(f"BOT_Arm_{side}", 0.042, (sign * 0.176, 0.0, Z_SHOULDER), mat_navy, segs=24, rings=18)
    # Royal blue dome shoulder pauldron with smooth bevel
    pauldron = create_smooth_sphere(f"Part_Shoulder_{side}", 0.054, (sign * 0.178, 0.0, Z_SHOULDER + 0.010), mat_blue, segs=28, rings=20, scale=(1.0, 0.95, 0.90))
    bicep = create_smooth_cylinder(f"Part_Bicep_{side}", 0.036, 0.076, (sign * 0.180, 0.0, Z_SHOULDER - 0.060), mat_white, segs=28, bevel_width=0.005)
    
    bpy.ops.object.select_all(action='DESELECT')
    for p in [pauldron, bicep]:
        p.select_set(True)
    pivot.select_set(True)
    bpy.context.view_layer.objects.active = pivot
    bpy.ops.object.join()
    pivot.name = f"BOT_Arm_{side}"
    for p in pivot.data.polygons:
        p.use_smooth = True
    return pivot

BOT_Arm_L = build_upper_arm("L", 1.0)
BOT_Arm_R = build_upper_arm("R", -1.0)

# ==================== 11 & 12. BOT_Forearm_L and BOT_Forearm_R ====================
def build_forearm(side, sign):
    elbow = create_smooth_cylinder(f"BOT_Forearm_{side}", 0.032, 0.038, (sign * 0.184, 0.0, Z_ELBOW), mat_navy, rot=(math.radians(90), 0, 0), segs=24)
    gauntlet = create_smooth_cylinder(f"Part_Gaunt_{side}", 0.044, 0.088, (sign * 0.186, 0.0, Z_ELBOW - 0.055), mat_white, segs=28, bevel_width=0.006, radius2=0.038)
    cuff = create_smooth_cylinder(f"Part_Cuff_{side}", 0.040, 0.015, (sign * 0.186, 0.0, Z_ELBOW - 0.102), mat_blue, segs=28, bevel_width=0.003)
    # Glowing cyan cross/tech icon on outer forearm
    glyph = create_subdiv_box(f"Part_Glyph_{side}", (0.006, 0.016, 0.016), (sign * 0.228, 0.0, Z_ELBOW - 0.055), mat_cyan, subdiv=1)
    
    bpy.ops.object.select_all(action='DESELECT')
    for p in [gauntlet, cuff, glyph]:
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

# ==================== 13 & 14. BOT_Hand_L and BOT_Hand_R (Articulated Robotic Gloves) ====================
def build_hand(side, sign):
    palm = create_subdiv_box(f"BOT_Hand_{side}", (0.052, 0.048, 0.042), (sign * 0.186, 0.0, Z_HAND), mat_navy, subdiv=2)
    digits = []
    for f_idx in range(3):
        y_pos = -0.016 + f_idx * 0.016
        f_obj = create_subdiv_box(f"Part_Fing_{side}_{f_idx}", (0.016, 0.015, 0.035), (sign * 0.186, y_pos, Z_HAND - 0.034), mat_navy, subdiv=1)
        digits.append(f_obj)
    thumb = create_subdiv_box(f"Part_Thumb_{side}", (0.016, 0.022, 0.028), (sign * 0.162, -0.020, Z_HAND - 0.014), mat_navy, subdiv=1)
    thumb.rotation_euler = (math.radians(-25), 0, math.radians(sign * 25))
    digits.append(thumb)
    
    bpy.ops.object.select_all(action='DESELECT')
    for d in digits:
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

# ==================== 15 & 16. BOT_Thigh_L and BOT_Thigh_R (Chubby Cute Legs) ====================
def build_thigh(side, sign):
    hip = create_smooth_sphere(f"BOT_Thigh_{side}", 0.042, (sign * 0.095, 0.0, Z_PELVIS - 0.010), mat_navy, segs=24, rings=18)
    thigh_armor = create_smooth_cylinder(f"Part_ThighArmor_{side}", 0.052, 0.088, (sign * 0.095, 0.0, Z_PELVIS - 0.055), mat_white, segs=28, bevel_width=0.007, radius2=0.046)
    
    bpy.ops.object.select_all(action='DESELECT')
    thigh_armor.select_set(True)
    hip.select_set(True)
    bpy.context.view_layer.objects.active = hip
    bpy.ops.object.join()
    hip.name = f"BOT_Thigh_{side}"
    for p in hip.data.polygons:
        p.use_smooth = True
    return hip

BOT_Thigh_L = build_thigh("L", 1.0)
BOT_Thigh_R = build_thigh("R", -1.0)

# ==================== 17 & 18. BOT_Shin_L and BOT_Shin_R ====================
def build_shin(side, sign):
    knee = create_smooth_cylinder(f"BOT_Shin_{side}", 0.036, 0.036, (sign * 0.095, -0.002, Z_KNEE), mat_navy, rot=(0, math.radians(90), 0), segs=24)
    shin_armor = create_smooth_cylinder(f"Part_ShinArmor_{side}", 0.054, 0.096, (sign * 0.095, -0.005, Z_KNEE - 0.050), mat_white, segs=28, bevel_width=0.007, radius2=0.046)
    shin_glyph = create_subdiv_box(f"Part_ShinGlyph_{side}", (0.006, 0.014, 0.022), (sign * 0.146, -0.005, Z_KNEE - 0.050), mat_cyan, subdiv=1)
    
    bpy.ops.object.select_all(action='DESELECT')
    for p in [shin_armor, shin_glyph]:
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

# ==================== 19 & 20. BOT_Boot_L and BOT_Boot_R (Astro Boots: Yellow Toes + Blue Soles + Laser Slits) ====================
def build_boot(side, sign):
    body = create_subdiv_box(f"BOT_Boot_{side}", (0.105, 0.135, 0.075), (sign * 0.095, 0.015, Z_BOOT + 0.010), mat_white, subdiv=3)
    # Bulbous golden yellow rounded front toe cap
    toe = create_smooth_sphere(f"Part_Toe_{side}", 0.054, (sign * 0.095, -0.060, Z_BOOT), mat_yellow, segs=28, rings=20, scale=(1.0, 0.95, 0.78))
    # Royal blue sole
    sole = create_subdiv_box(f"Part_Sole_{side}", (0.110, 0.160, 0.022), (sign * 0.095, -0.012, Z_BOOT - 0.038), mat_blue, subdiv=2)
    # Glowing cyan side/heel laser thruster slit
    slit = create_subdiv_box(f"Part_Slit_{side}", (0.006, 0.036, 0.014), (sign * 0.150, 0.005, Z_BOOT - 0.010), mat_cyan, subdiv=1)
    
    bpy.ops.object.select_all(action='DESELECT')
    for p in [toe, sole, slit]:
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
print(f"Created {len(components)} Astro Bot style components.")

# ---------------------------------------------------------
# 4. Rigging: Standard 13-Bone Deformation Armature
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
b_root.tail = (0, 0, Z_PELVIS)

# 2. Torso
b_torso = edit_bones.new("Torso")
b_torso.head = (0, 0, Z_PELVIS)
b_torso.tail = (0, 0, Z_TORSO + 0.14)
b_torso.parent = b_root

# 3. Head
b_head = edit_bones.new("Head")
b_head.head = (0, 0, Z_TORSO + 0.14)
b_head.tail = (0, 0, Z_HEAD + 0.18)
b_head.parent = b_torso

# 4 & 5. Antenna.L & Antenna.R
b_ant_l = edit_bones.new("Antenna.L")
b_ant_l.head = (-0.05, 0.0, Z_HEAD + 0.05)
b_ant_l.tail = (-0.08, 0.04, Z_HEAD + 0.14)
b_ant_l.parent = b_head

b_ant_r = edit_bones.new("Antenna.R")
b_ant_r.head = (0.05, 0.0, Z_HEAD + 0.05)
b_ant_r.tail = (0.08, 0.04, Z_HEAD + 0.14)
b_ant_r.parent = b_head

# 6 & 7. Arm.L & Hand.L
b_arm_l = edit_bones.new("Arm.L")
b_arm_l.head = (0.178, 0.0, Z_SHOULDER)
b_arm_l.tail = (0.184, 0.0, Z_ELBOW)
b_arm_l.parent = b_torso

b_hand_l = edit_bones.new("Hand.L")
b_hand_l.head = (0.184, 0.0, Z_ELBOW)
b_hand_l.tail = (0.186, 0.0, Z_HAND - 0.035)
b_hand_l.parent = b_arm_l

# 8 & 9. Arm.R & Hand.R
b_arm_r = edit_bones.new("Arm.R")
b_arm_r.head = (-0.178, 0.0, Z_SHOULDER)
b_arm_r.tail = (-0.184, 0.0, Z_ELBOW)
b_arm_r.parent = b_torso

b_hand_r = edit_bones.new("Hand.R")
b_hand_r.head = (-0.184, 0.0, Z_ELBOW)
b_hand_r.tail = (-0.186, 0.0, Z_HAND - 0.035)
b_hand_r.parent = b_arm_r

# 10 & 11. Leg.L & Foot.L
b_leg_l = edit_bones.new("Leg.L")
b_leg_l.head = (0.095, 0.0, Z_PELVIS - 0.01)
b_leg_l.tail = (0.095, 0.0, Z_KNEE)
b_leg_l.parent = b_root

b_foot_l = edit_bones.new("Foot.L")
b_foot_l.head = (0.095, 0.0, Z_KNEE)
b_foot_l.tail = (0.095, -0.06, 0.015)
b_foot_l.parent = b_leg_l

# 12 & 13. Leg.R & Foot.R
b_leg_r = edit_bones.new("Leg.R")
b_leg_r.head = (-0.095, 0.0, Z_PELVIS - 0.01)
b_leg_r.tail = (-0.095, 0.0, Z_KNEE)
b_leg_r.parent = b_root

b_foot_r = edit_bones.new("Foot.R")
b_foot_r.head = (-0.095, 0.0, Z_KNEE)
b_foot_r.tail = (-0.095, -0.06, 0.015)
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

# ---------------------------------------------------------
# 6. Complete 14 Animation Actions
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

# 1. Idle (Looping confident breathing & gentle sway)
act_idle = set_active_action("Idle")
for f, z_off, p_torso, p_head in [(0, 0, 0, 0), (30, -0.015, 2, -1.5), (60, 0, 0, 0)]:
    insert_loc("Root", f, (0, 0, z_off))
    insert_rot("Torso", f, (p_torso, 0, 0))
    insert_rot("Head", f, (p_head, 0, 0))
    insert_rot("Arm.L", f, (10, 0, 8))
    insert_rot("Arm.R", f, (10, 0, -8))

# 2. Idle_Secondary (Playful look around)
act_idle_sec = set_active_action("Idle_Secondary")
for f in [0, 60]:
    insert_loc("Root", f, (0, 0, 0))
    insert_rot("Head", f, (0, 0, 0))
insert_loc("Root", 20, (0, 0, 0.03))
insert_rot("Head", 20, (0, 0, 16))
insert_rot("Head", 40, (0, 0, -16))

# 3. Walk (Bouncy rhythmic Chibi walk)
act_walk = set_active_action("Walk")
for idx, f in enumerate([0, 6, 12, 18, 24]):
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

# 4. Run (Energetic joyful Astro sprint)
act_run = set_active_action("Run")
for idx, f in enumerate([0, 4, 8, 12, 15]):
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

# 5. Jump_Start (Squash & takeoff)
act_jump_start = set_active_action("Jump_Start")
insert_loc("Root", 0, (0, 0, 0))
insert_loc("Root", 4, (0, 0, -0.05))
insert_rot("Torso", 4, (12, 0, 0))
insert_rot("Leg.L", 4, (-15, 0, 0))
insert_rot("Leg.R", 4, (-15, 0, 0))
insert_loc("Root", 8, (0, 0, 0.08))
insert_rot("Torso", 8, (-8, 0, 0))
insert_rot("Arm.L", 8, (-40, 0, 20))
insert_rot("Arm.R", 8, (-40, 0, -20))

# 6. Jump_Loop (Airborne float / hover)
act_jump_loop = set_active_action("Jump_Loop")
for f in [0, 30]:
    insert_loc("Root", f, (0, 0, 0.05))
    insert_rot("Torso", f, (-5, 0, 0))
    insert_rot("Leg.L", f, (18, 0, 0))
    insert_rot("Leg.R", f, (-10, 0, 0))
    insert_rot("Arm.L", f, (-45, 0, 25))
    insert_rot("Arm.R", f, (-45, 0, -25))

# 7. Fall (Descent wind flare)
act_fall = set_active_action("Fall")
for f in [0, 20]:
    insert_loc("Root", f, (0, 0, 0))
    insert_rot("Torso", f, (8, 0, 0))
    insert_rot("Head", f, (-12, 0, 0))
    insert_rot("Arm.L", f, (-60, 0, 35))
    insert_rot("Arm.R", f, (-60, 0, -35))
    insert_rot("Leg.L", f, (-15, 0, 5))
    insert_rot("Leg.R", f, (-15, 0, -5))

# 8. Landing (Impact squash & recovery)
act_landing = set_active_action("Landing")
insert_loc("Root", 0, (0, 0, -0.06))
insert_rot("Torso", 0, (18, 0, 0))
insert_rot("Leg.L", 0, (-22, 0, 0))
insert_rot("Leg.R", 0, (-22, 0, 0))
insert_rot("Arm.L", 0, (20, 0, 20))
insert_rot("Arm.R", 0, (20, 0, -20))
insert_loc("Root", 4, (0, 0, 0.01))
insert_rot("Torso", 4, (-4, 0, 0))
insert_loc("Root", 8, (0, 0, 0))
insert_rot("Torso", 8, (0, 0, 0))

# 9. Turn_Left
act_turn_l = set_active_action("Turn_Left")
for f in [0, 15]:
    insert_loc("Root", f, (0, 0, 0))
    insert_rot("Torso", f, (0, 0, 0))
insert_rot("Torso", 7, (0, 0, 25))
insert_rot("Head", 7, (0, 0, 35))

# 10. Turn_Right
act_turn_r = set_active_action("Turn_Right")
for f in [0, 15]:
    insert_loc("Root", f, (0, 0, 0))
    insert_rot("Torso", f, (0, 0, 0))
insert_rot("Torso", 7, (0, 0, -25))
insert_rot("Head", 7, (0, 0, -35))

# 11. Collect (Reach out & star pickup celebration)
act_collect = set_active_action("Collect")
for f in [0, 30]:
    insert_loc("Root", f, (0, 0, 0))
    insert_rot("Arm.R", f, (0, 0, 0))
    insert_rot("Head", f, (0, 0, 0))
insert_loc("Root", 12, (0, 0, 0.02))
insert_rot("Arm.R", 12, (-65, 0, -20))
insert_rot("Head", 12, (15, 0, -10))

# 12. Interact (Button press)
act_interact = set_active_action("Interact")
for f in [0, 25]:
    insert_rot("Arm.L", f, (0, 0, 0))
insert_rot("Arm.L", 10, (-80, 0, 15))
insert_rot("Torso", 10, (10, 0, 10))

# 13. Victory (Joyous Astro victory dance)
act_victory = set_active_action("Victory")
for f in [0, 45]:
    insert_loc("Root", f, (0, 0, 0))
    insert_rot("Arm.L", f, (0, 0, 0))
    insert_rot("Arm.R", f, (0, 0, 0))
insert_loc("Root", 20, (0, 0, 0.12))
insert_rot("Arm.L", 20, (-135, 0, 35))
insert_rot("Arm.R", 20, (-135, 0, -35))
insert_rot("Torso", 20, (-10, 0, 0))
insert_rot("Head", 20, (-15, 0, 0))

# 14. Respawn (Materialization jump)
act_respawn = set_active_action("Respawn")
insert_loc("Root", 0, (0, 0, -0.08))
insert_rot("Torso", 0, (28, 0, 0))
insert_rot("Head", 0, (30, 0, 0))
insert_rot("Arm.L", 0, (35, 0, 15))
insert_rot("Arm.R", 0, (35, 0, -15))
insert_loc("Root", 25, (0, 0, 0))
insert_rot("Torso", 25, (0, 0, 0))
insert_rot("Head", 25, (0, 0, 0))

# Default to Idle
armature_obj.animation_data.action = act_idle
print("All 14 animation actions generated.")

# ---------------------------------------------------------
# 7. Save Blend & Export GLB
# ---------------------------------------------------------
blend_paths = [
    "/Users/it/Documents/TINY PLANET/assets/blender/source/bot_astro.blend",
    "/Users/it/Documents/TINY PLANET/assets/blender/source/bot.blend",
    "/Users/it/Documents/TINY PLANET/assets/blender/source/bot_character.blend"
]
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
    print(f"✓ Exported production Astro Bot GLB to: {gp}")

# ---------------------------------------------------------
# 8. Studio Floor, Lighting & Renders
# ---------------------------------------------------------
ground = create_smooth_cylinder("StudioFloor", 4.0, 0.02, (0, 0, -0.01), get_mat("StudioMat", (0.94, 0.95, 0.97, 1.0), roughness=0.35), segs=40)

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

cam_data = bpy.data.cameras.new("RenderCam")
cam_data.lens = 75.0
cam_obj = bpy.data.objects.new("RenderCam", cam_data)
bpy.context.collection.objects.link(cam_obj)
bpy.context.scene.camera = cam_obj

bpy.context.scene.render.resolution_x = 1200
bpy.context.scene.render.resolution_y = 1000
bpy.context.scene.render.engine = 'BLENDER_EEVEE_NEXT' if hasattr(bpy.types, 'RenderEngineEEVEE_NEXT') else 'BLENDER_EEVEE'

out_dir = "/Users/it/.gemini/antigravity/brain/0e7dd031-e455-469e-95de-196677cac497"

views = [
    ("astro_front.png", (0.0, -2.4, 0.55), (math.radians(88), 0, 0), 75.0),
    ("astro_34.png", (-1.7, -1.7, 0.65), (math.radians(80), 0, math.radians(-45)), 75.0),
    ("astro_side.png", (-2.4, 0.0, 0.55), (math.radians(88), 0, math.radians(-90)), 75.0),
    ("astro_back.png", (0.0, 2.4, 0.55), (math.radians(92), 0, math.radians(180)), 75.0),
    ("astro_hero.png", (-1.2, -1.4, 0.72), (math.radians(78), 0, math.radians(-40)), 85.0),
]

for filename, pos, rot, lens in views:
    cam_obj.location = pos
    cam_obj.rotation_euler = rot
    cam_data.lens = lens
    filepath = os.path.join(out_dir, filename)
    bpy.context.scene.render.filepath = filepath
    bpy.ops.render.render(write_still=True)
    print(f"Rendered: {filepath}")

print("Astro Bot Master Generation and Rendering Completed Successfully!")
