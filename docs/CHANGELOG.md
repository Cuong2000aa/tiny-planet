# Changelog — Tiny Planet

All notable changes to this project will be documented in this file.

## [3.5.0-bot-redesign] - 2026-11-16
### Changed
- **Replaced Egg-Shaped B.O.T with Brand-New Silhouette ("The Modular Retro-Chibi Explorer"):**
  - **Head & Helmet:** Distinct chamfered TV-monitor helmet (beveled cube chassis, separated from torso by a visible mechanical neck collar).
  - **Face & Visor:** Deep gloss obsidian visor screen with large, expressive tilted cyan LED pill eyes.
  - **Ears & Audio:** Left/right audio headphone canisters with sunset-orange trim rings and cyan sensor dots.
  - **Antennas:** Dual angled communication stems with orange accent rings and bright cyan beacon orbs.
  - **Torso & Chassis:** Tapered trapezoid chest chassis (broad at shoulders, compact at waist) with center glowing cyan reactor core medallion, orange side intake vents, and dark waist bar.
  - **Backpack Generator:** Compact rectangular power generator with dual angled rocket thrusters and horizontal cyan fuel cylinder.
  - **Segmented Limbs:** Fully articulated arms with orange shoulder pads, white upper arm struts, titanium elbow pivot spheres, white forearm cuffs, and 3-finger mech grip hands.
  - **Legs & Sneaker Boots:** Mechanical hip sockets, thigh cylinders, knee shock-absorber rings, dark shin pistons, and angular high-tech runner sneakers with dark magnetic soles and glowing cyan heel strips.
- **Armature & Rigging (`BOT_Armature`):**
  - Rebuilt 13-bone skeletal rig specifically configured for the new head/torso/limb proportions.
  - Skinning bound via vertex groups with zero joint tearing or rubbery deformation.
- **14 Rebuilt Animation Actions in Blender 5.2.3:**
  - `Idle`: Smooth breathing bob, head micro-tilts, antenna flex.
  - `Idle_Secondary`: Inquisitive head tilt, cheerful double-hand wave to player, observant look-around.
  - `Walk`: Ground-contact mechanical strides, arm counter-swings, torso bobbing.
  - `Run`: Athletic forward lean (-14°), high-knee stride, wide arm pumps, trailing antennas.
  - `Jump_Start`: Dynamic anticipation crouch into explosive launch takeoff.
  - `Jump_Loop`: Airborne glide pose with boots tucked and thrusters angled down.
  - `Fall`: Reactive balance-catching arm flail and dangling legs.
  - `Landing`: Heavy impact squash compression (-0.13m) and springy rebound.
  - `Turn_Left` / `Turn_Right`: Rapid banking twist and head anticipation turn.
  - `Collect`: Joyful celebration hop, double fist pump, proud chest puff.
  - `Interact`: Deliberate forward step, right hand button press gesture with head nod.
  - `Victory`: 360° pirouette spin, double celebratory hops, side-to-side torso sway, hero freeze pose waving to player.
  - `Respawn`: Reboot crouch, head snap, dust shake-off, energetic recovery.
- **Godot Collision Tuning:**
  - Tightened player `CapsuleShape3D` radius from 0.38m to 0.34m in `scenes/player/player.tscn` to perfectly conform to B.O.T's new athletic silhouette.
- **Web Export:**
  - Exported updated release Web build to `web-build/`.

## [3.0.0-character-animation] - 2026-11-16
### Added
- Initial 13-bone skeletal deformation armature and 14 animation actions.

## [2.0.0-visual-overhaul] - 2026-11-16
### Added
- Complete Blender 3D environment asset pipeline and ACES tone mapping.
