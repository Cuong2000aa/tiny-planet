# Technical Architecture — Tiny Planet

## 1. Engine Configuration
- **Engine Version:** Godot 4.7.1 Stable
- **Render Engine:** Compatibility (`rendering/renderer/rendering_method="gl_compatibility"`)
- **Display Resolution:** 1280x720 base, `stretch/mode="canvas_items"`, `stretch/aspect="expand"` to accommodate various desktop and mobile screen ratios seamlessly.
- **Physics Engine:** 3D physics tick rate at 60Hz.

## 2. Node Hierarchy & Scene Breakdown

```text
Main / AwakeningIsland (Node3D)
├── WorldEnvironment (Stylized sky, ambient light, tone mapping)
├── DirectionalLight3D (Sun with soft stylized shadows)
├── Environment/
│   ├── FloatingIslands (StaticBody3D meshes with colliders)
│   ├── SteppingStones (StaticBody3D floating platforms)
│   ├── Vegetation & Props (Low-poly trees, crystals, flowers)
│   └── EnergyBridge (AnimatableBody3D or animated bridge segments)
├── Interactive/
│   ├── SwitchPedestal (Area3D + StaticBody3D)
│   └── ExitPortal (Area3D with swirl particles & trigger)
├── Collectibles/
│   ├── EnergyFragment1 (Area3D)
│   ├── EnergyFragment2 (Area3D)
│   └── EnergyFragment3 (Area3D)
├── Player (CharacterBody3D)
│   ├── CollisionShape3D (Capsule)
│   ├── RobotVisuals (MeshInstance3D hierarchy + AnimationPlayer)
│   └── CameraPivot (SpringArm3D)
│       └── Camera3D
└── UI (CanvasLayer)
    ├── HUD (Fragment counter, objective text)
    ├── InteractionPrompt (Contextual "Press E / Tap" prompt)
    ├── MobileControls (Virtual Joystick, Jump Button, Action Button)
    └── VictoryModal (Level complete celebration)
```

## 3. Core Subsystems

### A. Player Controller (`scripts/player/player_controller.gd`)
- `CharacterBody3D` with velocity integration:
  - `SPEED = 6.0`, `ACCEL = 14.0`, `DECEL = 16.0`
  - `JUMP_VELOCITY = 8.5`, gravity derived from project settings.
  - Direction calculated relative to `Camera3D` basis flattened onto the XZ plane.
  - Smooth mesh rotation towards movement direction using `slerp` or `lerp_angle`.
  - Procedural squash-and-stretch on jump and land.

### B. Third-Person Orbit Camera (`scripts/player/camera_controller.gd`)
- `SpringArm3D` with collision masking against environment layers.
- Handles mouse motion (mouse drag / right click drag or captured cursor) and mobile swipe gestures.
- Pitch clamped between -60° and +20° to prevent disorienting angles.

### C. Interaction System (`scripts/interactive/interactable.gd`)
- Area3D with generic `interact(player)` interface and signal `interacted`.
- The player maintains a list of overlapping interactables and targets the closest one.
- Sends signal to UI to show/hide prompt.

### D. Collectibles System (`scripts/collectibles/energy_fragment.gd`)
- Floating sine-wave bobbing and continuous yaw rotation in `_process`.
- Area3D `body_entered` trigger.
- Emits `collected` signal to global/level manager, plays chime sound, triggers spark particle burst, frees node cleanly.

### E. Mobile Virtual Controls (`scripts/ui/mobile_controls.gd`)
- Auto-detected or forced on touch devices.
- Touch joystick handles vector mapping onto standard Godot action inputs (`move_left`, `move_right`, `move_forward`, `move_back`).
- Virtual buttons trigger `jump` and `interact` actions.
