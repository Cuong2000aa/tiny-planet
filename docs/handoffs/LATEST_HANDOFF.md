# Latest Session Handoff — Tiny Planet

## 1. Project Overview
Tiny Planet is an autonomous 3D adventure platformer developed for the web using Godot 4.7.1 Stable Standard with Compatibility renderer, WebGL 2.0, single-threaded export, hosted live on GitHub Pages. Inspired by Astro Bot's tactile charm, players control B.O.T exploring vibrant floating sky islands.

## 2. Current State
- **Phase:** Phase 2: Visual Overhaul & 3D Asset Production (Completed & Verified).
- **Public URL:** https://cuong2000aa.github.io/tiny-planet/
- **GitHub Repository:** https://github.com/Cuong2000aa/tiny-planet
- **Latest Commit Checkpoint:** Ready to stage Phase 2 commit & push.

## 3. Completed Work in Phase 2
1. **Asset Pipeline:**
   - Established `assets/blender/source/` with source `.blend` files (`bot_character.blend`, `environment_islands.blend`, `environment_props.blend`, `interactive_props.blend`).
   - Automated Blender 5.2.3 scripts in `assets/blender/scripts/`.
   - Categorized GLB exports under `assets/models/` (`characters/`, `environment/`, `props/`, `architecture/`, `collectibles/`).
2. **Character Overhaul (B.O.T):**
   - High-appeal cute robot model with porcelain-white ceramic material, reflective visor, tilted cyan eyes, jetpack battery with dual gold thrusters, articulated shoulder ball joints and mitten hands, and magnetic boots with heel glow.
3. **Island & Level Overhaul:**
   - Sculpted multi-layered floating islands (`island_awakening.glb`, `island_sanctuary.glb`, `island_portal.glb`, `stepping_stone.glb`).
   - Organic terrain with cobblestone spawn pathway, overhanging grass rim, stratified sandstone cliff undersides, and floating rock shards.
   - Modular stepping stones with moss caps and glowing levitation crystals.
4. **Vegetation & Props:**
   - Low-poly canopy trees, rounded leafy bushes, colorful flower patches, glowing mushrooms, chiseled boulders, crystal clusters, ancient ruin pillars, and celestial lanterns.
   - Distant sky vista islands and floating 3D clouds.
5. **Lighting, Color Grading & VFX:**
   - ACES tone mapping (`tonemap_mode = 3`) eliminating washed-out whites and producing rich greens and warm stone.
   - Jump and landing dust puffs (`CPUParticles3D`).
   - Energy Fragment collection sparkle burst (`CPUParticles3D`).
   - Exit portal cosmic swirl and particle aura.
6. **Camera Tuning:**
   - Shortened spring arm from 4.8m to 3.8m for clearer B.O.T framing and obstacle visibility.
7. **Verification & Web Export:**
   - Headless automated gameplay test passed with 100% assertions.
   - Exported updated release web build into `web-build/` (`index.html`, `index.pck` 1.4 MB, `index.wasm` 39.5 MB).
   - Local HTTP server test verified status 200 on all endpoints.

## 4. How to Run & Verify
```bash
# Run automated gameplay tests:
/Users/it/bin/godot_app/Godot.app/Contents/MacOS/Godot --path . --headless -s scripts/tests/test_gameplay.gd

# Run game in Godot:
/Users/it/bin/godot_app/Godot.app/Contents/MacOS/Godot --path .

# Regenerate all 3D Blender assets:
/Applications/Blender.app/Contents/MacOS/Blender --background --python assets/blender/scripts/generate_character.py
/Applications/Blender.app/Contents/MacOS/Blender --background --python assets/blender/scripts/generate_environment.py
/Applications/Blender.app/Contents/MacOS/Blender --background --python assets/blender/scripts/generate_props.py
/Applications/Blender.app/Contents/MacOS/Blender --background --python assets/blender/scripts/generate_interactives.py

# Export web build:
/Users/it/bin/godot_app/Godot.app/Contents/MacOS/Godot --path . --headless --export-release "Web" web-build/index.html
```

## 5. Next Recommended Task
- Expand archipelago with Level 2 (Sky Archipelago Ruins with moving platforms and puzzles).
- Add settings/pause menu with volume controls.
