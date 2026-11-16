# Changelog — Tiny Planet

All notable changes to this project will be documented in this file.

## [2.0.0-visual-overhaul] - 2026-11-16
### Added
- **Complete Blender 3D Asset Pipeline:**
  - `assets/blender/source/`: source `.blend` files (`bot_character.blend`, `environment_islands.blend`, `environment_props.blend`, `interactive_props.blend`).
  - `assets/blender/scripts/`: modular automated generation scripts for Blender 5.2.3 LTS.
  - Organized model directories: `characters/`, `environment/`, `props/`, `architecture/`, `collectibles/`.
- **Character Upgrade (B.O.T):**
  - High-appeal silhouette with porcelain-ceramic material, dark curved reflective visor, expressive tilted cyan eyes, jetpack battery pack with dual golden thrusters, articulated shoulder/mitten arms, and magnetic titanium boots with heel glow.
- **Environment Overhaul:**
  - Awakening Island: sculpted grass plateau, cobblestone spawn path, grass fringe rim, stratified sandstone cliffs, floating rock roots.
  - Sanctuary Island: circular ancient stone dais with cyan glowing runic inlays.
  - Portal Island: octagonal ancient temple platform with rune steps.
  - Stepping Stones: floating ancient rune slabs with moss tops and levitation crystals underneath.
  - Vistas: distant floating islands and fluffy 3D stylized clouds.
- **Vegetation & Props:**
  - Low-poly canopy trees, rounded bushes, multi-colored flower clusters (pink, blue, yellow), glowing mushrooms, chiseled boulders, glowing crystal clusters, ancient ruin pillars, and celestial lantern posts.
- **Lighting & Color Grading:**
  - ACES filmic tone mapping to eliminate washed-out whites and deliver vibrant greens and warm stone.
  - Deep azure sky with peach horizon gradient.
  - Calibrated directional sunlight and ambient lighting.
- **Visual Effects:**
  - Jump and landing dust puffs via `CPUParticles3D` on player feet.
  - Sparkling collection burst on Energy Fragments.
  - Portal swirling energy particles on unlock.
- **Camera Tuning:**
  - Shortened camera arm from 4.8m to 3.8m for clearer B.O.T framing and improved platforming readability.
- **Web Build:**
  - Exported updated release Web build with all new assets into `web-build/`.
