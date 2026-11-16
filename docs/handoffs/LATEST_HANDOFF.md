# Latest Session Handoff — Tiny Planet

## 1. Project Overview
Tiny Planet is an autonomous 3D adventure platformer developed for the web using Godot 4.7.1 Stable Standard with Compatibility renderer, WebGL 2.0, single-threaded export, hosted live on GitHub Pages. Inspired by Astro Bot's tactile charm, players control B.O.T exploring vibrant floating sky islands.

## 2. Current State
- **Phase:** Phase 4: Official Model Sheet Character Production ("B.O.T Explorer with Golden Scarf & Sprout Antenna") — Completed & Verified!
- **Public URL:** https://cuong2000aa.github.io/tiny-planet/
- **GitHub Repository:** https://github.com/Cuong2000aa/tiny-planet
- **Milestone Tag:** `v4.0-official-bot`

## 3. Completed Work in Phase 4
1. **Model Sheet Fidelity:**
   - Authored in Blender 5.2.3 LTS (`assets/blender/scripts/generate_character.py` -> `assets/blender/source/bot_character.blend`).
   - Replaced temporary geometries with the exact design from the official Game Character Model Sheet:
     - Rounded ivory ceramic helmet with royal blue crown cap.
     - Yellow sprout leaf antenna on the crown with flared teardrop fin.
     - Circular ear modules with yellow outer rim, blue housing, and luminous cyan donut ring.
     - Glossy dark visor with large expressive cyan LED capsule eyes.
     - Bright golden yellow neck scarf with front triangular fold and dual dynamic flying tails.
     - Compact white chassis with glowing cyan chest energy triangle.
     - Royal blue backpack with glowing cyan downward-pointing energy triangle.
     - Deep navy ball joints, white sleeve shells, blue forearm cuffs, and navy mech mitten hands.
     - Boots with bright yellow rounded toe caps, royal blue heels/soles, and cyan ankle dots.
2. **Armature & Rigging:**
   - 13 deformation bones: `Root`, `Torso`, `Head`, `Antenna.L`, `Antenna.R`, `Arm.L`, `Hand.L`, `Arm.R`, `Hand.R`, `Leg.L`, `Foot.L`, `Leg.R`, `Foot.R`.
   - Single unified mesh `BOT_Character` with vertex groups for clean robotic deformation without joint tearing.
3. **14 Tailored Animation Actions:**
   - `Idle`, `Idle_Secondary`, `Walk`, `Run`, `Jump_Start`, `Jump_Loop`, `Fall`, `Landing`, `Turn_Left`, `Turn_Right`, `Collect`, `Interact`, `Victory`, `Respawn`.
4. **Godot Integration & Collision:**
   - Integrated cleanly into `scenes/player/player.tscn`.
   - `PlayerController` automatically drives locomotion blending, proportional stride scaling, Astro-Bot banking tilt, and action hooks.
5. **Testing & Verification:**
   - `scripts/tests/test_character_animation.gd`: 100% assertions passed.
   - `scripts/tests/test_gameplay.gd`: 100% assertions passed.
6. **Web Export & Deployment:**
   - Exported release Web build to `web-build/` and deployed live to GitHub Pages.

## 4. How to Run & Verify
```bash
# Run automated character & animation verification test:
/Users/it/bin/godot_app/Godot.app/Contents/MacOS/Godot --path . --headless -s scripts/tests/test_character_animation.gd

# Run automated gameplay tests:
/Users/it/bin/godot_app/Godot.app/Contents/MacOS/Godot --path . --headless -s scripts/tests/test_gameplay.gd

# Run game in Godot:
/Users/it/bin/godot_app/Godot.app/Contents/MacOS/Godot --path .

# Regenerate B.O.T character and animations in Blender:
/Applications/Blender.app/Contents/MacOS/Blender --background --python assets/blender/scripts/generate_character.py

# Export web build:
/Users/it/bin/godot_app/Godot.app/Contents/MacOS/Godot --path . --headless --export-release "Web" web-build/index.html
```

## 5. Next Recommended Task
- Level 2: Sky Archipelago Ruins (vertical platforming with moving stone platforms and interactive laser mirrors).
- Audio options in pause menu (master, SFX, and music volume sliders).
