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
