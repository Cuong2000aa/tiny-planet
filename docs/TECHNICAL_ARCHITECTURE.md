# Technical Architecture — Tiny Planet

## 1. Engine Configuration
- **Engine Version:** Godot 4.7.1 Stable Standard
- **Render Engine:** Compatibility (`rendering/renderer/rendering_method="gl_compatibility"`), WebGL 2.0.
- **Display Resolution:** 1280x720 base, `stretch/mode="canvas_items"`, `stretch/aspect="expand"` to accommodate desktop and mobile displays.
- **Physics Engine:** 3D physics tick rate at 60Hz.

## 2. Node Hierarchy & Scene Breakdown

```text
AwakeningIsland (Node3D)
├── WorldEnvironment (Stylized sky, ambient light, ACES tone mapping)
├── DirectionalLight3D (Sun with soft stylized shadows)
├── Environment/
│   ├── FloatingIslands (island_awakening, island_sanctuary, island_portal)
│   ├── SteppingStones (stepping_stone instances with levitation crystals)
│   ├── Vegetation & Props (Low-poly trees, bushes, flowers, mushrooms, boulders, ruins)
│   └── Vistas (Distant floating islands, stylized 3D clouds)
├── Interactive/
│   ├── SwitchPedestal (Area3D + StaticBody3D with rotate crystal)
│   ├── EnergyBridge (5 sequential AnimatableBody3D crystal slabs)
│   └── ExitPortal (Area3D with dual ring frame, cosmic swirl & aura)
├── Collectibles/
│   ├── EnergyFragment1 (Area3D with floating bob & collection VFX)
│   ├── EnergyFragment2 (Area3D)
│   └── EnergyFragment3 (Area3D)
├── Player (CharacterBody3D)
│   ├── CollisionShape3D (CapsuleShape3D, radius 0.34m, height 1.15m)
│   ├── VisualRoot (Node3D)
│   │   └── BOT_Model (Instanced bot.glb - Official Model Sheet Character)
│   │       ├── BOT_Armature (Node3D)
│   │       │   └── Skeleton3D (13 deformation bones)
│   │       │       └── BOT_Character (Skinned MeshInstance3D)
│   │       └── AnimationPlayer (14 skeletal actions)
│   ├── InteractionDetector (Area3D with SphereShape3D radius 1.8m)
│   ├── DustParticles (CPUParticles3D on jump and land)
│   ├── SFXJump (AudioStreamPlayer3D)
│   └── SFXLand (AudioStreamPlayer3D)
├── CameraController (Node3D)
│   └── SpringArm3D (3.8m length, collision mask 1)
│       └── Camera3D (FOV 68°, smooth follow)
└── UI (CanvasLayer)
    ├── HUD (Energy fragment counters, objective text, victory banner)
    └── TouchControls (Virtual Joystick, Jump button, Interact button, Camera drag area)
```

## 3. Core Subsystems

### A. Player Controller & Animation State Machine (`scripts/player/player_controller.gd`)
- `CharacterBody3D` with velocity integration:
  - `move_speed = 6.0`, `acceleration = 18.0`, `deceleration = 14.0`
  - `jump_velocity = 8.5`, gravity derived from project settings (`9.8 * 2.2`).
  - Direction calculated relative to `CameraController` yaw flattened onto the XZ plane.
  - Smooth mesh rotation towards movement direction using `lerp_angle(rotation_speed * delta)`.
  - Stylized Astro Bot turn banking tilt on `visual_root.rotation.z` and `rotation.x`.
- **Animation State Machine (`AnimState` Enum):**
  - States: `IDLE`, `IDLE_SECONDARY`, `WALK`, `RUN`, `JUMP_START`, `JUMP_LOOP`, `FALL`, `LANDING`, `COLLECT`, `INTERACT`, `VICTORY`, `RESPAWN`.
  - Proportional stride speed matching: `speed_scale` dynamically scaled to horizontal velocity, preventing foot sliding.
  - Cross-fading: Configured `set_blend_time` pairs across all locomotion, air, and action states.
  - Idle timer: Periodically triggers `IDLE_SECONDARY` (curious head tilt & wave) after 6 seconds of inactivity.
  - One-shot actions: Collect (fist pump), Interact (press button), Respawn (reboot shake), Victory (celebration dance).

### B. Character Skeletal Rig & Blender Pipeline (`assets/blender/scripts/generate_character.py`)
- Created in Blender 5.2.3 LTS, saved to `assets/blender/source/bot_character.blend`.
- **Armature Hierarchy (`BOT_Armature`):**
  - `Root` (ground base 0, 0, 0)
    - `Torso` (center of mass 0.28m to 0.68m)
      - `Head` (0.68m to 0.98m)
        - `Antenna.L` (0.98m to 1.22m)
        - `Antenna.R` (0.98m to 1.22m)
      - `Arm.L` -> `Hand.L`
      - `Arm.R` -> `Hand.R`
    - `Leg.L` -> `Foot.L`
    - `Leg.R` -> `Foot.R`
- **Skinning:** Single unified mesh `BOT_Character` with vertex groups and Armature modifier, ensuring 100% deformation stability and zero mesh tearing.
- **Export:** Exported to `assets/models/characters/bot.glb` and `assets/models/bot.glb` with NLA tracks and all 14 actions.

### C. Third-Person Orbit Camera (`scripts/player/camera_controller.gd`)
- `SpringArm3D` (3.8m) with collision masking against environment layers.
- Handles mouse drag (desktop) and virtual touch camera drag area (mobile).
- Clamped pitch between -55° and +25°.

### D. Interaction System (`scripts/interactive/interactable.gd`)
- Area3D with generic `interact(player)` interface and signal `interacted`.
- Player tracks closest overlapping interactable and triggers `play_interact_animation()`.

### E. Collectibles System (`scripts/collectibles/energy_fragment.gd`)
- Floating sine-wave bobbing and continuous yaw rotation.
- Triggers `player.play_collect_animation()` on collection.

### F. Automated Verification Tests (`scripts/tests/`)
- `test_character_animation.gd`: Headless validation of skeleton bones, all 14 actions, and state machine transitions.
- `test_gameplay.gd`: Headless end-to-end verification of player spawn, fragment pickups, switch trigger, bridge extension, and portal victory.
