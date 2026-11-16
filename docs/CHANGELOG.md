# Changelog — Tiny Planet

All notable changes to this project will be documented in this file.

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
