# Changelog — Tiny Planet

All notable changes to this project will be documented in this file.

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
