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

def build_bot_character():
    clean_scene()
    script_dir = os.path.dirname(os.path.abspath(__file__))
    source_dir = os.path.join(script_dir, "..", "source")
    char_model_dir = os.path.join(script_dir, "..", "..", "models", "characters")
    root_model_dir = os.path.join(script_dir, "..", "..", "models")
    os.makedirs(source_dir, exist_ok=True)
    os.makedirs(char_model_dir, exist_ok=True)

    # Materials
    # Warm cream porcelain body
    mat_white = create_pbr_material("Mat_Bot_Porcelain", (0.96, 0.95, 0.98, 1.0), metallic=0.1, roughness=0.2)
    # Glossy dark reflective visor glass
    mat_visor = create_pbr_material("Mat_Bot_Visor", (0.04, 0.05, 0.08, 1.0), metallic=0.9, roughness=0.1)
    # Bright emissive cyan for eyes and energy circuits
    mat_cyan_glow = create_pbr_material("Mat_Bot_CyanGlow", (0.0, 0.95, 1.0, 1.0), metallic=0.0, roughness=0.2, emission=(0.0, 1.0, 0.95, 1.0), emission_strength=4.0)
    # Warm gold metallic accents
    mat_gold = create_pbr_material("Mat_Bot_Gold", (1.0, 0.82, 0.22, 1.0), metallic=0.85, roughness=0.25)
    # Dark titanium joints and soles
    mat_dark = create_pbr_material("Mat_Bot_Titanium", (0.18, 0.20, 0.24, 1.0), metallic=0.8, roughness=0.35)
    # Sky blue trim
    mat_blue_trim = create_pbr_material("Mat_Bot_Trim", (0.15, 0.55, 0.95, 1.0), metallic=0.3, roughness=0.3)

    # Root
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
    root = bpy.context.active_object
    root.name = "BOT_Root"

    # 1. Main Egg Body: cute capsule-egg silhouette
    bpy.ops.mesh.primitive_uv_sphere_add(segments=28, ring_count=20, radius=0.46, location=(0, 0, 0.58))
    body = bpy.context.active_object
    body.name = "Body"
    body.scale = (0.92, 0.88, 1.05)
    body.data.materials.append(mat_white)
    bpy.ops.object.shade_smooth()
    body.parent = root

    # 2. Chest Insignia / Planet Logo: embossed gold circle on chest
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.10, depth=0.04, location=(0, 0.38, 0.45))
    badge = bpy.context.active_object
    badge.name = "ChestBadge"
    badge.rotation_euler = (math.radians(72), 0, 0)
    badge.data.materials.append(mat_gold)
    bpy.ops.object.shade_smooth()
    badge.parent = root

    # Cyan glowing inner star core in the chest badge
    bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=8, radius=0.045, location=(0, 0.40, 0.45))
    badge_core = bpy.context.active_object
    badge_core.name = "ChestCore"
    badge_core.data.materials.append(mat_cyan_glow)
    badge_core.parent = root

    # 3. Visor Screen: sleek dark curved screen wrapping the face
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=16, radius=0.26, location=(0, 0.27, 0.65))
    visor = bpy.context.active_object
    visor.name = "Visor"
    visor.scale = (1.12, 0.52, 0.68)
    visor.data.materials.append(mat_visor)
    bpy.ops.object.shade_smooth()
    visor.parent = root

    # 4. Expressive Cyan Glowing Eyes (Tilted slightly for cute expressive look)
    # Left Eye
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=12, radius=0.055, location=(-0.115, 0.38, 0.66))
    eye_l = bpy.context.active_object
    eye_l.name = "Eye_Left"
    eye_l.scale = (1.0, 0.45, 1.25)
    eye_l.rotation_euler = (0, 0, math.radians(-5))
    eye_l.data.materials.append(mat_cyan_glow)
    bpy.ops.object.shade_smooth()
    eye_l.parent = root

    # Right Eye
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=12, radius=0.055, location=(0.115, 0.38, 0.66))
    eye_r = bpy.context.active_object
    eye_r.name = "Eye_Right"
    eye_r.scale = (1.0, 0.45, 1.25)
    eye_r.rotation_euler = (0, 0, math.radians(5))
    eye_r.data.materials.append(mat_cyan_glow)
    bpy.ops.object.shade_smooth()
    eye_r.parent = root

    # 5. Dual Stylized Antenna: springy look with chrome bands and glowing cyan tips
    # Left Antenna Stem
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.018, depth=0.18, location=(-0.08, 0, 1.10))
    stem_l = bpy.context.active_object
    stem_l.name = "Antenna_Stem_L"
    stem_l.rotation_euler = (0, math.radians(-12), 0)
    stem_l.data.materials.append(mat_dark)
    bpy.ops.object.shade_smooth()
    stem_l.parent = root

    # Left Glowing Tip
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=12, radius=0.06, location=(-0.11, 0, 1.21))
    orb_l = bpy.context.active_object
    orb_l.name = "Antenna_Orb_L"
    orb_l.data.materials.append(mat_cyan_glow)
    bpy.ops.object.shade_smooth()
    orb_l.parent = root

    # Right Antenna Stem
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.018, depth=0.18, location=(0.08, 0, 1.10))
    stem_r = bpy.context.active_object
    stem_r.name = "Antenna_Stem_R"
    stem_r.rotation_euler = (0, math.radians(12), 0)
    stem_r.data.materials.append(mat_dark)
    bpy.ops.object.shade_smooth()
    stem_r.parent = root

    # Right Glowing Tip
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=12, radius=0.06, location=(0.11, 0, 1.21))
    orb_r = bpy.context.active_object
    orb_r.name = "Antenna_Orb_R"
    orb_r.data.materials.append(mat_cyan_glow)
    bpy.ops.object.shade_smooth()
    orb_r.parent = root

    # 6. Jetpack Backpack on the back (explains propulsion/jump effects!)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -0.36, 0.58))
    jetpack = bpy.context.active_object
    jetpack.name = "JetpackBody"
    jetpack.scale = (0.36, 0.16, 0.38)
    jetpack.data.materials.append(mat_white)
    bpy.ops.object.shade_smooth()
    jetpack.parent = root

    # Jetpack Glowing Energy Core Cell
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.07, depth=0.22, location=(0, -0.44, 0.58))
    jet_core = bpy.context.active_object
    jet_core.name = "JetpackCore"
    jet_core.rotation_euler = (math.radians(90), 0, 0)
    jet_core.data.materials.append(mat_cyan_glow)
    bpy.ops.object.shade_smooth()
    jet_core.parent = root

    # Left & Right Thruster Nozzles
    for side, x in [("L", -0.12), ("R", 0.12)]:
        bpy.ops.mesh.primitive_cone_add(vertices=16, radius1=0.06, radius2=0.035, depth=0.10, location=(x, -0.38, 0.34))
        nozzle = bpy.context.active_object
        nozzle.name = f"Thruster_{side}"
        nozzle.rotation_euler = (math.radians(180), 0, 0)
        nozzle.data.materials.append(mat_gold)
        bpy.ops.object.shade_smooth()
        nozzle.parent = root

    # 7. Ear Dials / Audio Sensors
    for side, x, rot in [("L", -0.42, 90), ("R", 0.42, -90)]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.09, depth=0.05, location=(x, 0, 0.62))
        ear = bpy.context.active_object
        ear.name = f"EarDial_{side}"
        ear.rotation_euler = (0, math.radians(rot), 0)
        ear.data.materials.append(mat_gold)
        bpy.ops.object.shade_smooth()
        ear.parent = root

        # Cyan inner sensor dot
        bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=8, radius=0.035, location=(x * 1.05, 0, 0.62))
        ear_dot = bpy.context.active_object
        ear_dot.name = f"EarDot_{side}"
        ear_dot.data.materials.append(mat_cyan_glow)
        ear_dot.parent = root

    # 8. Cute Stubby Arms with Mitten Hands
    for side, x, s_mult in [("L", -0.42, 1), ("R", 0.42, -1)]:
        # Shoulder ball joint
        bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=8, radius=0.07, location=(x, 0.02, 0.52))
        shoulder = bpy.context.active_object
        shoulder.name = f"Shoulder_{side}"
        shoulder.data.materials.append(mat_dark)
        shoulder.parent = root

        # Arm capsule
        bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.045, depth=0.18, location=(x * 1.12, 0.05, 0.40))
        arm = bpy.context.active_object
        arm.name = f"Arm_{side}"
        arm.rotation_euler = (math.radians(15), math.radians(s_mult * 18), 0)
        arm.data.materials.append(mat_white)
        bpy.ops.object.shade_smooth()
        arm.parent = root

        # Cute rounded mitten hand
        bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=12, radius=0.075, location=(x * 1.20, 0.10, 0.28))
        hand = bpy.context.active_object
        hand.name = f"Hand_{side}"
        hand.scale = (0.85, 1.0, 1.1)
        hand.data.materials.append(mat_white)
        bpy.ops.object.shade_smooth()
        hand.parent = root

    # 9. Chunky Magnetic Boots
    for side, x in [("L", -0.19), ("R", 0.19)]:
        # Hip joint
        bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=8, radius=0.065, location=(x, 0, 0.22))
        hip = bpy.context.active_object
        hip.name = f"Hip_{side}"
        hip.data.materials.append(mat_dark)
        hip.parent = root

        # Foot main body (white porcelain cap)
        bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=12, radius=0.13, location=(x, 0.03, 0.13))
        foot = bpy.context.active_object
        foot.name = f"Foot_{side}"
        foot.scale = (0.88, 1.28, 0.65)
        foot.data.materials.append(mat_white)
        bpy.ops.object.shade_smooth()
        foot.parent = root

        # Magnetic Sole (dark titanium grip pad)
        bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.12, depth=0.03, location=(x, 0.03, 0.035))
        sole = bpy.context.active_object
        sole.name = f"Sole_{side}"
        sole.scale = (0.85, 1.25, 1.0)
        sole.data.materials.append(mat_dark)
        sole.parent = root

        # Cyan glow strip on heel
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(x, -0.09, 0.07))
        glow_strip = bpy.context.active_object
        glow_strip.name = f"HeelGlow_{side}"
        glow_strip.scale = (0.08, 0.025, 0.03)
        glow_strip.data.materials.append(mat_cyan_glow)
        glow_strip.parent = root

    # Save source .blend file
    blend_path = os.path.join(source_dir, "bot_character.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print(f"✓ Saved Blender source to: {blend_path}")

    # Export optimized GLB
    glb_char_path = os.path.join(char_model_dir, "bot.glb")
    glb_root_path = os.path.join(root_model_dir, "bot.glb")
    bpy.ops.export_scene.gltf(filepath=glb_char_path, export_format='GLB', use_selection=False)
    # Also update root bot.glb for seamless Godot scene reference
    bpy.ops.export_scene.gltf(filepath=glb_root_path, export_format='GLB', use_selection=False)
    print(f"✓ Exported GLB to: {glb_char_path} & {glb_root_path}")

if __name__ == "__main__":
    build_bot_character()
    print("B.O.T character generation complete!")
