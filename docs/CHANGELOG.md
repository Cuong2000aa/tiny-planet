# Changelog — Tiny Planet

All notable changes to this project will be documented in this file.

## [3.0.0-character-animation] - 2026-11-16
### Added
- **13-Bone Skeletal Deformation Armature in Blender 5.2.3 LTS:**
  - Armature `BOT_Armature` featuring `Root`, `Torso`, `Head`, `Antenna.L`, `Antenna.R`, `Arm.L`, `Hand.L`, `Arm.R`, `Hand.R`, `Leg.L`, `Foot.L`, `Leg.R`, `Foot.R`.
  - Zero distortion skinning via dedicated vertex groups and Armature modifier on unified mesh `BOT_Character`.
- **14 Professional Keyframed Animation Actions Authored in Blender:**
  - `Idle`: Subtle body hover/breathing bobbing, gentle micro head tilt, springy antenna delay.
  - `Idle_Secondary`: Inquisitive head tilt, cheerful double-hand wave to player, observant look-around.
  - `Walk`: Rhythmic alternating strides, natural arm counter-swings, cute torso bounce, antenna bounce.
  - `Run`: High-cadence energetic sprint with -12° forward torso lean, wider arm pumps, antenna trailing back.
  - `Jump_Start`: Quick crouch anticipation (-0.09m) and explosive upward launch takeoff.
  - `Jump_Loop`: Dynamic aerodynamic airborne posture with boots tucked, thruster angle, arms outspread.
  - `Fall`: Reactive balance-catching arm flail, legs dangling, antenna fluttering upward.
  - `Landing`: Heavy impact squash compression (-0.12m), elastic rebound recovery to neutral.
  - `Turn_Left` / `Turn_Right`: Cute rapid banking twist and head anticipation turn.
  - `Collect`: Celebratory victory hop, double fist pump to the sky, proud chest puff.
  - `Interact`: Deliberate forward step, right hand button press gesture with head nod.
  - `Victory`: Astro-Bot style celebration dance: 360° pirouette spin, double celebratory hops, rhythmic side-to-side torso sway, final hero freeze pose waving to player.
  - `Respawn`: Emergence reboot: crouch boot-up, head snap, dust shake-off, energetic recovery.
- **Godot Character Animation State Machine:**
  - `PlayerController` state machine managing `AnimState` enum and seamless cross-fading.
  - Stride speed scaling proportional to velocity, preventing foot sliding.
  - Astro Bot stylized turn banking tilt (`visual_root.rotation.z` and `rotation.y`).
  - Seamless one-shot action hooks for Collect, Interact, Respawn, and Victory.
- **Automated Animation Verification Suite:**
  - `scripts/tests/test_character_animation.gd` validating skeleton bones, all 14 actions, and runtime state transitions.
- **Web Export & Deployment:**
  - Updated WebGL 2.0 release build in `web-build/` with single-threaded export.

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
