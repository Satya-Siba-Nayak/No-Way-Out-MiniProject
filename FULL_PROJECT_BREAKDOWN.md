# NO WAY OUT? - COMPLETE TECHNICAL MANUAL

This document provides a line-by-line and section-by-section explanation for EVERY file in the project.

---

## 📂 ROOT DIRECTORY

### 📄 main.py (The Entry Point)
This file is the "Engine Starter." It creates the window and runs the heart of the game.
- **Lines 1-13**: Imports `sys` for closing the program, `pygame` for graphics, and `PIL` (Pillow) to read the background GIF.
- **`get_gif_dimensions` (Lines 26-29)**: Opens the GIF file once just to see its size (272x160). We do this so the game knows how much to scale up the window.
- **`main()` (Lines 32-84)**: 
    - **Initialization**: `pygame.init()` and `mixer.init()` start the graphics and sound systems.
    - **Window Scaling**: We take the original size (272x160) and multiply by `scale = 3` to get `816x480`. This gives the game its "Pixel Art" look.
    - **`game_context`**: This is a shared dictionary. Instead of using global variables, we put things like `player_name` and `screen_w` here so every screen can access them.
    - **The Main Loop**: `while True` runs 60 times a second. `dt` (Delta Time) ensures that if the computer slows down, the player doesn't move slower—they move the same distance based on time.

---

## 📂 engine/ (The Game's Mechanics)

### 📄 state_machine.py (Navigation Manager)
This file handles how you move from the Menu to the Room to the Puzzle.
- **The Stack (`self._states`)**: Think of this like a stack of pancakes. The top pancake is the screen you see.
- **`push(state)`**: Puts a new screen on top (like opening a puzzle). The room underneath "pauses."
- **`pop()`**: Removes the top screen (closing a puzzle). The room underneath "resumes."
- **`change(state)`**: Throws away the current screen and puts a new one there (moving from Menu to Game).

### 📄 player.py (The Character)
- **`SPRITE_CHARS`**: A dictionary containing the file paths for Finn and Maeve.
- **`load_sprite_images`**: Uses `subsurface()` to cut a single large image into 16 small walking frames (4 for each direction).
- **`move(dt, walls)`**: This is the physics engine. It moves the player left/right, checks if they hit a wall, then moves them up/down and checks again. This "Step-by-Step" movement prevents you from getting stuck on corners.
- **`draw()`**: Centers the character image over their feet (the collision box) and picks the right animation frame.

### 📄 tmx_loader.py (The Map Importer)
- **`TilesetInfo`**: Loads the "Tile Palette" and cuts it into 32x32 squares.
- **`TiledMap.render()`**: This creates one massive image of the entire room. Drawing one big image is much faster for the computer than drawing 500 small tiles individually.
- **`FLIPPED_HORIZONTALLY_FLAG`**: Uses "Bitwise Math" to check if you flipped a tile in the Tiled editor.

### 📄 room.py (Objects & Collision)
- **`Interactable`**: A simple box on the map. It has a `puzzle_id`. If the player stands inside or near this box and presses 'E', the puzzle starts.
- **`build_easy_room_from_tmx`**: This function connects the visual map to the code. It looks for a layer named "desk" in the Tiled file and attaches the `caesar_cipher` puzzle to it.

---

## 📂 states/ (The Visual Screens)

### 📄 menu_state.py (Title & Settings)
- **`load_gif_frames`**: Converts every frame of the background GIF into a list of Pygame images.
- **`_update_volume_from_mouse`**: Math logic: `(mouse_x - track_x) / track_width`. This converts where you clicked on the slider into a percentage (0 to 100) for the music volume.
- **Phases**: Uses a variable `self.phase` to switch between typing your name, picking a character, and the settings menu.

### 📄 room_state.py (Main Gameplay)
- **`enter()`**: Calculates the `scale` of the room to ensure it fits on your screen with a HUD bar at the bottom.
- **`_interact()`**: This handles the "E" key. If you are standing near the door, it checks if `all_puzzles_solved` is True.
- **Level 2 Effects**: 
    - `blink_timer`: Cycles through Red, Green, and Blue overlays.
    - `bump_hits`: Tracks how many times the "Strange Force" pushed you back.

### 📄 puzzle_state.py (The Puzzle Overlay)
- **Overlay Drawing**: Uses `pygame.SRCALPHA` to draw a dark, transparent box over the room so you can still see the game behind the puzzle.
- **`_submit()`**: This is the "Judge." It takes what you typed and asks the specific Puzzle class if you are right.

---

## 📂 puzzles/ (The Puzzle Logic)

### 📄 easy_puzzles.py (Level 1)
- **`CaesarCipher`**: Shifts letters by 3 (A becomes D). It expects the user to type "HELLO."
- **`BinaryLock`**: Uses `2 ** i` (powers of 2) to calculate the decimal value of the flashing lights.
- **`CouchSlicing`**: Teaches Python slicing `[3:7]`. It extracts "GOLD" from "ZZZGOLDZZZ."

### 📄 level2_puzzles.py (Level 2)
- **`BlinkingLights`**: Simply checks for the sequence "324."
- **`MisplacedTile`**: A simple text-match puzzle for the riddle "ECHO."
- **`PaintingPuzzle`**: Tells the `PuzzleState` to draw `Painting.png` on the screen so the player can look for the hidden number "1379."

---
*End of Full Technical Manual*
