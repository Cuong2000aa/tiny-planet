# Architectural & Design Decisions — Tiny Planet

## ADR 001: Godot 4.7.1 Compatibility Renderer for Web Target
- **Context:** Web browsers running WebGL 2.0 vary widely across devices, especially mobile Safari and Chrome on Android. Godot 4 Forward+ and Mobile renderers use Vulkan/WebGPU which have inconsistent browser support.
- **Decision:** Use Godot 4 `gl_compatibility` renderer exclusively.
- **Consequences:** Maximizes cross-browser compatibility, minimizes shader compile times, avoids WebGPU experimental flag requirements, runs smoothly at 60 FPS on both desktop and mobile.

## ADR 002: Single-Threaded Web Export
- **Context:** Godot multi-threaded Web export requires SharedArrayBuffer and strict HTTP headers (`Cross-Origin-Opener-Policy: same-origin`, `Cross-Origin-Embedder-Policy: require-corp`), which often fail or break on standard GitHub Pages sites or third-party web iframes.
- **Decision:** Set export preset threads option to `false` (single-threaded).
- **Consequences:** Game loads reliably on standard GitHub Pages without complex header workarounds.

## ADR 003: Procedural Audio Generation for Self-Contained Assets
- **Context:** Prototype requires original, non-infringing audio assets for jumps, landings, collection chimes, mechanisms, and ambient loops.
- **Decision:** Generate pristine, stylized WAV audio resources algorithmically via Python synthesis and import into Godot.
- **Consequences:** 100% original, zero copyright risk, perfectly tailored retro-modern soundscape, tiny file sizes optimal for fast web download.

## ADR 004: Dual Control Scheme (Keyboard/Mouse + Touch)
- **Context:** The game is Web-first, accessible on both desktop and mobile devices.
- **Decision:** Implement transparent touch controls (virtual joystick and action buttons) that simulate Godot standard `InputEventAction` events or seamlessly integrate with the input system.
- **Consequences:** Unified player controller code handles both desktop and mobile inputs identically.

## ADR 005: Blender Source Organization & Asset Pipeline (Phase 2)
- **Context:** Phase 2 requires professional stylized 3D assets rather than primitive engine shapes, with persistent editable source files and optimized GLBs for Web export.
- **Decision:** Structure pipeline into `assets/blender/source/` (keeping source `.blend` files), `assets/blender/scripts/` (reproducible Python generator scripts), and categorized GLB destinations (`assets/models/{characters,environment,props,architecture,collectibles}/`), while updating root compatibility links. Added `.gdignore` to `assets/blender/` to prevent Godot from attempting direct blend imports.
- **Consequences:** Clean separation of art sources and runtime engine assets; reproducible, automated asset generation; zero broken dependencies in Godot.

## ADR 006: ACES Tone Mapping & CPUParticles3D for Compatibility Renderer
- **Context:** The prototype suffered from washed-out white terrain under Compatibility lighting, and GPUParticles3D can trigger WebGL compute shader incompatibilities on mobile Safari.
- **Decision:** Adopt ACES Tone Mapping (`tonemap_mode = 3`) with calibrated ambient lighting (0.5 energy) and replace runtime particle bursts with `CPUParticles3D`.
- **Consequences:** Eliminates washed-out surfaces, produces rich vibrant greens and warm terracotta rocks, and ensures guaranteed cross-browser particle rendering without compute shader overhead.
