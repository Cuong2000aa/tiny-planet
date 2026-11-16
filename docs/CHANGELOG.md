# Changelog — Tiny Planet

All notable changes to this project will be documented in this file.

## [1.0.0-prototype] - 2026-11-16
### Added
- Complete playable prototype of The Awakening Island.
- B.O.T player character model (`bot.glb`) with cyan emissive LED visor and procedural animation.
- Responsive 3D CharacterBody3D player controller with acceleration, air control, jump, landing squash-and-stretch, and fall recovery.
- Smooth third-person SpringArm3D orbit camera controller with mouse drag and touch swipe support.
- 3 floating Energy Fragments with sinusoidal bobbing, continuous rotation, collection chimes, and HUD counter.
- Reusable `Interactable` system with proximity detector.
- Ancient Switch Pedestal with button depress animation, color transition, and audio feedback.
- Energy Bridge with cascading sequential plank extension and dynamic collision activation.
- Exit Portal with swirling cosmic vortex, unlocking logic, and level completion trigger.
- Complete original synthesized audio suite (jump, land, collect, switch, bridge, portal, victory, ambient loop).
- Responsive HUD with fragment tracker, objective guide, contextual interaction prompt, and victory modal.
- Mobile touch controls (Virtual Joystick, Jump button, Camera drag area).
- Single-threaded Web export configured in `export_presets.cfg` and verified in `web-build/`.
- GitHub Actions deployment workflow `.github/workflows/deploy.yml` for automated GitHub Pages publishing.
- Automated gameplay verification test runner (`scripts/tests/test_gameplay.gd`).
