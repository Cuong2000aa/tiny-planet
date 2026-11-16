# Known Issues & Workarounds — Tiny Planet

## Open Issues
- None currently recorded.

## Solved Issues
- **Raw Blend Import in Godot Headless Mode:** Placing `bot.blend` directly inside `assets/models/source/` triggered Godot's built-in Blender importer check in headless mode; resolved by placing `.gdignore` in `assets/models/source/` so Godot imports the optimized `bot.glb` while preserving the editable `.blend` source on disk.
- **Eye Cylinder Profile Extrusion:** Initial eye cylinders protruded slightly in profile views; resolved by flattening the depth to 0.006m and placing them flush against the curved visor glass faceplate.
