# Changelog — Tiny Planet

All notable changes to this project will be documented in this file.

## [6.5.0-premium-bot] - 2026-11-16
### Changed
- **B.O.T Character Refinement — Premium Game Character Pass:**
  - **Draped Adventure Scarf:** Completely replaced the rigid neck ring with a draped yellow fabric cloth cowl featuring natural thickness and folds, a front triangular bandana fold with an inverted royal blue badge and glowing cyan core, and dual dynamic fluttering ribbon tails.
  - **Layered Engineered Torso:** Redesigned the torso with a sculpted white ceramic pectoral breastplate tapering to the waist, an integrated blue bezel framing the glowing cyan triangular reactor rune, and a dark graphite navy inner mechanical chassis and spine.
  - **Broad Athletic Shoulders & Arms:** Replaced floating spherical shoulders with angular yet smoothly beveled white pauldrons with protective outer flanges; added visible mechanical elbow hinges with royal blue pivot pins; sculpted flared ceramic gauntlets with royal blue wrist cuffs and cyan status glyphs; articulated robotic gloves with palm chassis, opposable thumb, fingers, and backplates.
  - **Sculpted Legs & Robotic Adventure Boots:** Added muscular white thigh armor over dark ball joints, mechanical knee caps, flared shin gaiters with cyan LED strips, and athletic robotic adventure sneakers with rounded bulbous yellow toe bumper caps, white heel counters, and multi-tiered royal blue tread soles.
  - **Premium PBR Materials:** Tuned pearl white ceramic with specular clearcoat (`Clearcoat 0.35`, `Roughness 0.18`), deep royal cobalt blue (`Metallic 0.12`), warm rich yellow fabric (`Roughness 0.35`), deep obsidian visor glass (`Roughness 0.02`, `Clearcoat 1.0`), and intense cyan LED emission (`Strength 5.5`).
  - **Verification & Deployment:** 100% assertions passed in `test_character_animation.gd` and `test_gameplay.gd`. Re-exported Web release build and deployed live to GitHub Pages.

## [6.0.0-production-bot] - 2026-11-16
### Added
- **Production-Quality Rebuild with 20 Discrete Articulated Meshes:**
  - Resolved the core technical blocker where primitive geometries were previously merged into a single joined mesh with `bpy.ops.object.join()`.
  - Rebuilt B.O.T from scratch in Blender 5.2.3 LTS as 20 separate, logically named, beveled, and articulated `MeshInstance3D` components under Godot's `Skeleton3D`:
    1. `BOT_Head`: Beveled squircle helmet with recessed front visor pocket and royal blue crown armor.
    2. `BOT_Antenna`: Curved golden yellow sprout with teardrop leaf fin.
    3-4. `BOT_Ear_L` & `BOT_Ear_R`: Yellow outer bezel, royal blue housing, glowing concentric cyan LED ring, and dark navy hub.
    5. `BOT_Scarf`: Yellow neck cowl with front triangular bib, inverted triangle badge, cyan power core, and dual fluttering ribbon tails.
    6. `BOT_Chest_Armor`: Tapered ceramic breastplate with integrated cyan triangular reactor core.
    7. `BOT_Backpack`: Royal blue utility pack with recessed cyan inverted triangle rune and yellow mounting straps.
    8. `BOT_Pelvis`: Graphite navy mechanical waist chassis.
    9-10. `BOT_Arm_L` & `BOT_Arm_R`: Shoulder pauldron cap, bicep sleeve, and elbow pivot.
    11-12. `BOT_Forearm_L` & `BOT_Forearm_R`: Chunky flared gauntlet with royal blue cuff ring and cyan status glyph.
    13-14. `BOT_Hand_L` & `BOT_Hand_R`: Articulated robotic glove with palm chassis, thumb, fingers, and pearl white backplate guard.
    15-16. `BOT_Thigh_L` & `BOT_Thigh_R`: Ball hip joint and chunky white thigh armor sleeve.
    17-18. `BOT_Shin_L` & `BOT_Shin_R`: Flared white shin gaiter with cyan outer ankle indicator.
    19-20. `BOT_Boot_L` & `BOT_Boot_R`: Chunky rounded hero sneakers with golden yellow toe bumpers, royal blue tread soles, and cyan LED pills.
  - **Recessed Visor Cavity:** Modeled using a precise boolean difference pocket cut into the helmet face, eliminating any planar protrusion or z-fighting.
  - **Armature Rigging & Animations:** 13 deformation bones, vertex group weight assignment for each component, and 14 keyframed actions.
  - **Verification:** 100% assertions passed in `test_character_animation.gd` and `test_gameplay.gd`. All 20 components confirmed distinct in `inspect_bot_hierarchy.gd`.
  - **Deployment:** Re-exported Web release build to `web-build/` and deployed live to GitHub Pages.

## [5.1.0-character-refinement] - 2026-11-16
### Changed
- **Substantial 3D Character Model & Material Refinement:**
  - **Eliminated Clipping & Primitive Visuals:** Completely overhauled head and face assembly with smooth beveled squircle geometry, a recessed curved obsidian face visor with zero z-fighting/clipping, and flush-mounted vibrant cyan LED capsule eyes.
  - **Premium PBR Materials:**
    - White Armor: Warm glossy pearl ceramic (`Roughness 0.12`, `Clearcoat 0.45`).
    - Royal Blue Armor: Rich saturated deep royal blue (`Roughness 0.18`, `Metallic 0.08`).
    - Golden Yellow Details: Bright sunny golden yellow (`Roughness 0.25`, `Metallic 0.0`) for scarf, toe caps, ear rims, and antenna.
    - Mechanical Joints: Deep graphite navy (`Roughness 0.32`, `Metallic 0.18`) with compact recessed ball sockets.
    - Visor Display: Ultra-glossy deep obsidian black (`Roughness 0.03`, `Clearcoat 1.0`).
    - Energy Cores: Luminous neon electric cyan with high emissive intensity.
  - **Sculpted Scarf & Chassis:** Upgraded yellow neck scarf into soft fleece cowl with natural folds, front triangular bib with blue inlay & glowing cyan core, and dual S-curve fluttering tails.
  - **Articulated Limbs & Hands:** Refined shoulder pauldrons, upper arm sleeves, elbow pivots, wrist cuff rings with cyan cross decals, and chibi robotic hands with palm, thumb, and sculpted fingers.
  - **Stable Platformer Boots:** Bulbous golden yellow toe caps, blue heel/sole wraps, and cyan ankle LED dots sitting perfectly flat on ground.
  - **Saved Deliverables:**
    - `assets/models/character/bot.blend` & `assets/models/character/bot.glb`.
    - `assets/models/source/bot.blend` & `assets/models/characters/bot.glb`.
    - Godot `import/blender/enabled=false` configured to ensure pure GLB runtime loading without headless editor warnings.
  - **Verification:** Both test suites (`test_character_animation.gd` and `test_gameplay.gd`) passing 100%. Re-exported Web build deployed live.

## [5.0.0-turnaround-bot] - 2026-11-16
### Added
- **Complete 3D Character Rebuild Matching Authoritative Character Turnaround Sheet:**
  - Built from scratch in Blender 5.2.3 LTS matching `media_1794801712994_79a8c181.jpg` from all angles (FRONT, RIGHT, BACK, LEFT, and 3/4 VIEW).
  - Saved editable `.blend` source to `assets/models/source/bot.blend` and `assets/blender/source/bot.blend`.
  - Added `.gdignore` in `assets/models/source/` to prevent raw `.blend` import errors while maintaining direct GLB pipeline.
  - Exported optimized game-ready GLBs to `assets/models/bot.glb` and `assets/models/characters/bot.glb`.
  - Added forearm outer cyan decal glyphs, articulated chibi hands with fingers and thumbs, flush-curved visor lens with cyan capsule LED eyes, and dynamic fluttering scarf tails.
  - Generated composite 5-view turnaround verification sheet at `/tmp/bot_turnaround_sheet.png`.
- **Full Humanoid Robot Armature & 14 Actions:**
  - Complete bone hierarchy: `Root`, `Hips`, `Torso`, `Chest`, `Neck`, `Head`, `Antenna.L/R`, `Shoulder.L/R`, `Arm.L/R`, `Hand.L/R`, `Thumb.L/R`, `Fingers.L/R`, `Leg.L/R`, `Foot.L/R`.
  - 14 animation actions tailored to the new anatomy.
- **Verification & Deployment:**
  - All automated test suites (`test_character_animation.gd`, `test_gameplay.gd`) passing 100%.
  - Web release build re-exported to `web-build/` and deployed live to GitHub Pages.

## [4.1.0-model-sheet-fidelity] - 2026-11-16
### Changed
- **High-Fidelity Official Model Sheet Character Refinement:**
  - **Recessed Curved Visor & Capsule LED Eyes:** Refined the obsidian faceplate into a curved squircle seamlessly integrated into the helmet opening; elongated the cyan LED eyes into authentic vertical capsule pill shapes with subtle 4.5° inward tilt matching the official sheet.
  - **Smooth Puffy Scarf & Bib with Cyan Core:** Upgraded the yellow adventure scarf collar with smooth subsurf curvature, front bib with blue border inlay and glowing cyan triangle core, and dual flutter tails.
  - **Refined Proportions & Silhouettes:** Optimized ivory helmet dome, royal blue crown cap arching over the brow, yellow sprout antenna fin, and boots with rounded bulbous golden yellow toe caps, white collars, and royal blue soles.
  - **Studio 3-Point Lighting & Floor Backdrop:** Added automated studio render pipeline producing high-resolution renders of the new hero character.
- **Export & Verification:**
  - Automated test suites (`test_character_animation.gd` and `test_gameplay.gd`) passing 100%.
  - Web release build re-exported to `web-build/` and ready for live GitHub Pages deployment.

## [4.0.0-official-bot] - 2026-11-16
### Added
- **Official Character Model Sheet B.O.T Production in Blender 5.2.3 LTS:**
  - **Head & Helmet:** Large rounded ivory-white ceramic helmet with royal blue top crown cap wrapping over the brow.
  - **Yellow Sprout Antenna:** Iconic yellow leaf sprout antenna on head crown with curved stem and flared teardrop fin.
  - **Concentric Cyan Ear Canisters:** Yellow outer disc rim, royal blue housing, glowing cyan concentric donut ring, and navy center hub.
  - **Visor & LED Eyes:** Deep gloss obsidian visor screen with large expressive cyan LED capsule pill eyes.
  - **Yellow Adventure Scarf:** 3D yellow neckerchief wrap around the neck, front triangular bib with blue emblem inlay, and dual dynamic scarf tails fluttering over shoulders.
  - **Torso & Backpack:** Compact ivory chassis, glowing cyan triangular chest energy core in blue bezel, and royal blue backpack unit with glowing cyan downward-pointing energy triangle.
  - **Limbs & Mitten Hands:** Deep navy shoulder/elbow/hip ball joints, white sleeve armor shells, royal blue forearm trim, and deep navy chibi mech mitten hands with white back-of-hand plates.
  - **Boots & Soles:** Golden yellow rounded front toe caps, royal blue heels and soles, and glowing cyan circular ankle dots.
- **Armature & Rigging:**
  - 13 deformation bones tailored to the exact model sheet proportions.
- **14 Rebuilt Animation Actions in Blender 5.2.3:**
  - `Idle`, `Idle_Secondary`, `Walk`, `Run`, `Jump_Start`, `Jump_Loop`, `Fall`, `Landing`, `Turn_Left`, `Turn_Right`, `Collect`, `Interact`, `Victory`, `Respawn`.
- **Godot Integration:**
  - Integrated into `scenes/player/player.tscn`.
  - Both automated test suites pass 100%: `scripts/tests/test_character_animation.gd` and `scripts/tests/test_gameplay.gd`.
- **Web Export:**
  - Updated release Web build in `web-build/` deployed to GitHub Pages.

## [3.5.0-bot-redesign] - 2026-11-16
### Changed
- Initial modular silhouette exploration and chassis testing.

## [3.0.0-character-animation] - 2026-11-16
### Added
- Initial 13-bone skeletal deformation armature and 14 animation actions.

## [2.0.0-visual-overhaul] - 2026-11-16
### Added
- Complete Blender 3D environment asset pipeline and ACES tone mapping.
