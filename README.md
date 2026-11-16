# Tiny Planet 🪐🤖

> A cute, stylized 3D adventure platformer built for the web with Godot 4.7.1 Stable.

Inspired by the tactile joy of *Astro Bot*, **Tiny Planet** puts you in control of **B.O.T**, a curious round robot wandering vibrant floating sky islands. Restore energy fragments, power up forgotten ancient mechanisms, extend energy bridges, and unlock dimensional portals.

---

## 🎮 Play in Browser
- **Live GitHub Pages URL:** *(Configured via GitHub Actions)*
- **Platforms:** Desktop (Chrome, Firefox, Safari, Edge) & Mobile (iOS Safari, Android Chrome).

## 🕹️ Controls
### Desktop
- **W, A, S, D:** Move
- **Space:** Jump
- **E:** Interact with switches & portals
- **Right Click / Left Drag / Mouse Drag:** Rotate Orbit Camera

### Mobile / Touch
- **Left Virtual Joystick:** Move B.O.T
- **Right A Button:** Jump
- **Right B Button (Contextual):** Interact
- **Swipe Anywhere on Right Half:** Rotate Camera

---

## 🛠️ Tech Stack & Engine Details
- **Engine:** Godot Engine 4.7.1 Stable Standard
- **Renderer:** `gl_compatibility` (WebGL 2.0 compatible, single-threaded web export)
- **Language:** GDScript
- **3D Modeling:** Blender 5.2.3 LTS & Procedural Stylized Meshes
- **Audio:** Custom procedural 16-bit sound effects & ambient soundscapes
- **Deployment:** GitHub Actions -> GitHub Pages

---

## 🚀 Running Locally

### Prerequisites
- [Godot Engine 4.7.1 Standard](https://godotengine.org)
- Web Export Templates for Godot 4.7.1

### Launching the Game
```bash
# Direct run with Godot CLI
godot --path .

# Or open this directory in the Godot Project Manager and click "Run Project" (F5)
```

### Building for Web
```bash
mkdir -p web-build
godot --headless --export-release "Web" web-build/index.html
```

### Local Web Testing
```bash
cd web-build
python3 -m http.server 8000
# Open http://localhost:8000 in your browser
```

---

## 📄 License & Credits
Created autonomously as an original 3D game project. All code, shaders, procedural assets, and audio are original.
