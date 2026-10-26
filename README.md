# karhutla-cube 🇮🇩🔥

A hand-tracked 3D story about Indonesia's forest fires (*karhutla*), built with computer vision, Python and TouchDesigner.

Make an **L pose** with one hand to open a wireframe cube. Close your **other hand into a fist** and the scene inside shatters into particles. Open it and the next scene forms:

🌳 forest → 🔥 burning forest → 🪵 burnt forest → 🦧 mother & baby orangutan

## How it works

- **[MediaPipe for TouchDesigner](https://github.com/torinmb/mediapipe-touchdesigner)** tracks 21 landmarks on each hand in real time.
- **Python** (inside TouchDesigner) reads the landmarks:
  - thumb–index distance → detects the L pose and scales the cube
  - fingertips curled toward the wrist → detects a fist
  - fist → old scene shatters, open hand → new scene forms from particles
- **TouchDesigner** renders the 3D models, fire, smoke, ash and ~70k transition particles.

The Python logic lives inside the `.toe` file. Readable copies are in [`python/`](python/):

| File | What it does |
|---|---|
| `hand_gestures.py` | L-pose detection, cube position/size, hand skeleton toggle |
| `fist_state_machine.py` | Debounced fist open/close detection |
| `transitions.py` | Scene switching, particle shatter & form, colour morph |
| `hand_skeleton.py` | Draws finger lines + joint dots for the other hand |

## Setup

1. Install [TouchDesigner](https://derivative.ca) (the free Non-Commercial licence works).
2. Download `release.zip` from [mediapipe-touchdesigner releases](https://github.com/torinmb/mediapipe-touchdesigner/releases) and copy its `toxes/` folder into this repo's root.
3. Open `karhutla-cube.toe`.
4. In the **MediaPipe** component, pick your webcam. Only **Detect hands** needs to be on.
5. Open the `over4` viewer (right-click → View…) and try it.

To record, toggle **Record** on the `recorder` node. Videos go to `recordings/` (ProRes .mov).

## Controls

| Gesture | Action |
|---|---|
| L pose (thumb + index) | Open the cube, spread fingers to zoom |
| Other hand: fist ✊ | Shatter the current scene |
| Other hand: open ✋ | Form the next scene |
| Drop the L | Close the cube, story restarts next time |

## Credits

- Hand tracking: [MediaPipe for TouchDesigner](https://github.com/torinmb/mediapipe-touchdesigner) by Torin Blankensmith
- "Low poly forest" by [konstaintin](https://sketchfab.com/konstaintin), CC BY 4.0
- "Ape" by Poly by Google, CC BY

Made by [@naniludiana](https://github.com/naniludiana). Get well soon, Indonesia 🌳
