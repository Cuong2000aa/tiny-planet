# AGENTS.md — AI Agent Guidelines & Architecture for Tiny Planet

## Project Overview
**Tiny Planet** is a cute, colorful, stylized 3D single-player adventure platformer built for the browser using Godot 4.7.1 Stable, inspired by the playful charm and tactile feel of Astro Bot. Players control B.O.T, a small friendly robot exploring floating sky islands, collecting energy fragments, triggering forgotten mechanisms, and unlocking dimensional portals.

## Technical Stack & Constraints
- **Engine:** Godot 4.7.1 Stable Standard (`/Users/it/bin/godot_app/Godot.app/Contents/MacOS/Godot`).
- **Language:** GDScript (Godot 4.x syntax only).
- **Renderer:** `gl_compatibility` (WebGL 2.0 compatible, Web-first).
- **Export Target:** Web export (single-threaded / `threads=false`, Progressive Web / HTML5).
- **3D Modeling & Pipeline:** Blender 5.2.3 (`/Applications/Blender.app/Contents/MacOS/Blender`) / Procedural Godot primitives with stylized PBR StandardMaterial3D.
- **VCS & Hosting:** Git, GitHub, GitHub Actions, GitHub Pages.
- **Strict Restrictions:**
  - NO C# / .NET.
  - NO GDExtension.
  - NO Forward+ or Mobile renderer for Web targets (Compatibility only).
  - NO multi-threading dependencies that break WebGL/WASM on cross-origin isolated or non-isolated pages.
  - NO external proprietary dependencies or copyrighted assets.
  - Never commit `.godot/` cache directory.

## Directory Structure
```text
tiny-planet/
├── AGENTS.md                       # AI Agent instructions & onboarding
├── README.md                       # Project overview & quick start
├── project.godot                   # Engine configuration
├── export_presets.cfg              # Godot export presets (Web)
├── .gitignore                      # Git ignore rules
├── docs/                           # Living project documentation
│   ├── GDD.md                      # Game Design Document
│   ├── TECHNICAL_ARCHITECTURE.md   # Systems, node hierarchy, scripts
│   ├── DEVELOPMENT_ROADMAP.md      # Milestones and acceptance criteria
│   ├── PROJECT_STATUS.md           # Live progress & current blockers
│   ├── CHANGELOG.md                # Notable change log
│   ├── DECISIONS.md                # Architecture and design decisions
│   ├── KNOWN_ISSUES.md             # Bug and performance tracker
│   └── handoffs/
│       └── LATEST_HANDOFF.md       # Cross-agent session handover document
├── scenes/                         # Godot scene files (.tscn)
│   ├── player/                     # B.O.T player character & camera
│   ├── environment/                # Floating islands, platforms, bridges
│   ├── interactive/                # Switches, mechanisms, portals
│   ├── collectibles/               # Energy fragments, pickups
│   └── levels/                     # Level scenes (e.g. awakening_island.tscn)
├── scripts/                        # GDScript files (.gd)
│   ├── player/                     # Player controller, state machine, camera
│   ├── interactive/                # Switch, bridge, portal scripts
│   ├── collectibles/               # Collectible logic
│   └── ui/                         # Virtual joystick, HUD, touch controls
├── assets/                         # Static assets
│   ├── models/                     # 3D models (.glb)
│   ├── materials/                  # StandardMaterial3D resources
│   ├── textures/                   # Texture maps (512x512 / 1024x1024)
│   ├── audio/                      # Sound effects & ambient loops (.wav, .ogg)
│   └── particles/                  # GPUParticles3D / CPUParticles3D setups
├── ui/                             # UI Scenes (HUD, touch controls, overlays)
├── web-build/                      # Exported WebGL files for GitHub Pages
└── .github/
    └── workflows/
        └── deploy.yml              # GitHub Actions deploy to GitHub Pages
```

## New-Agent Onboarding Procedure
When taking over this project, execute in this order:
1. Read `AGENTS.md` (this file).
2. Read `README.md`.
3. Read `docs/handoffs/LATEST_HANDOFF.md` to see the current state and exact next task.
4. Read `docs/PROJECT_STATUS.md` and `docs/KNOWN_ISSUES.md`.
5. Check `git status` and recent commits (`git log -n 5 --oneline`).
6. Verify runtime: test with Godot CLI headless check.
7. Continue development without asking the human for permission on routine tasks.

## Godot CLI Quick Reference
- Godot Binary: `/Users/it/bin/godot_app/Godot.app/Contents/MacOS/Godot`
- Run Main Scene: `/Users/it/bin/godot_app/Godot.app/Contents/MacOS/Godot --path .`
- Check / Validate Headless: `/Users/it/bin/godot_app/Godot.app/Contents/MacOS/Godot --path . --headless --quit`
- Web Export Command: `/Users/it/bin/godot_app/Godot.app/Contents/MacOS/Godot --path . --headless --export-release "Web" web-build/index.html`
