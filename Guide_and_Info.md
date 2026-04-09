# NO WAY OUT? — Comprehensive Developer Guide & Code Explanation

Welcome to the comprehensive guide for the **"NO WAY OUT?"** Pygame Mini-Project! This document contains a deep dive into the architecture, the directory structure, and explanations of how every part of the codebase works together.

---

## 1. High-Level Architecture
This game is built in Python using the **Pygame** library. To keep the code clean and manageable, the game uses a **State Machine Design Pattern**.
Instead of having one giant `while` loop with a thousand `if-else` statements, the game relies on isolated "States" (like Menu, Gameplay/Room, and Puzzle screens). The **State Machine** manages which state is currently active and passes events (button clicks, keyboard presses, screen drawing) downward to that active state.

### Project Structure Breakdown:
- **`main.py`** : The entry point that sets up the game window and starts the loop.
- **`engine/`** : The core mechanics, rendering, and logic that run "under the hood".
- **`states/`** : The actual screens the player visits (Menu, Room gameplay, Puzzle overlays).
- **`puzzles/`** : The specific riddles, ciphers, and codes the player must solve.
- **`data/`** & **`Maps/`** : The art assets (sprite sheets, TMX maps).

---

## 2. The Core Files Explained

### `main.py` (The Entry Point)
This is where the game starts. 
- **Pygame Initialization:** It runs `pygame.init()` and sets up the screen dimensions based on a background GIF.
- **The Context Dict:** It creates `game_context = {...}`. This dictionary is passed around to every single state. It acts as a shared memory pool where states can securely store information like `player_name`, `sprite_id`, `puzzles_solved`, and `current_level`.
- **The Main Loop:** It creates a `StateMachine`, pushes the `MenuState` onto it, and runs a `while True:` loop. In each loop tick, it calculates the time passed (`dt`), reads `events`, and passes them to the machine to `update()` and `draw()`.

### `engine/state_machine.py` & `states/base_state.py`
- **`State` class:** A template. Every screen in the game inherits from a `State`. It contains empty templates for `enter()`, `update(dt)`, `draw(surface)`, and `handle_events(events)`.
- **`StateMachine` class:** Contains a stack (list) of states. 
    - `push()`: Pauses the current state and layers a new one on top (useful for puzzle pop-ups!).
    - `pop()`: Removes the top state and resumes the one underneath.
    - `change()`: Fully removes the current state and switches to a completely new one (e.g., Menu going to the Room).

### `states/menu_state.py` (The Main Menu)
The menu is broken down into mini "phases":
1. **`name_input` Phase:** Captures keyboard events and stores characters into a `self.player_name` string.
2. **`menu_select` Phase:** Lets the user choose "New Game" or "Continue". 
    - *Code Detail:* "New Game" clears the save, forces `current_level` to `level1`, and moves to character selection. "Continue" uses `load_game()` from `save_system.py` to restore where the player left off.
3. **`char_select` Phase:** Displays the pre-rendered Profile Pictures (`pfp`) of "Finn" and "Maeve" and stores the chosen ID in the `ctx` context dictionary to be accessed by the Room.
4. **Settings Overlay:** Provides a volume slider modifying the pygame mixer.

### `engine/player.py` (Sprite & Movement Logic)
This file handles loading the character art and responding to keyboard movement natively.
- **`load_sprite_images()` & `load_idle_images()`:** These complex functions parse sprite sheets. They slice large sheets into individual frames (using Pygame's `subsurface()`) based on directions (Up, Down, Left, Right).
- **Movement (`move`):** Instead of moving directly in pixels, the player updates float coordinates `self.pos_x` and `self.pos_y` based on velocity * delta time (`dt`). This prevents jitter and makes walking buttery-smooth.
- **Collision Checking:** The player has a small `COLLIDE_W/H` hitbox on their feet. When scanning walls, code like `self.rect.colliderect(wall)` snaps the player's bounding box back to the edge of the wall if they intersect it.
- **Drawing:** Animates frames. Calculates `idx = int(self.frame_index) % len(frames)` to continuously update the walking animation while the `is_moving` flag is active. Also checks for `render_scale` property to resize sprites in smaller rooms (like Level 2).

### `engine/room.py` & `engine/tmx_loader.py` (World Building)
The game imports levels from **Tiled Editor** (`.tmx` maps).
- **`tmx_loader.py`:** An XML parser that reads the map `.tmx` tile layers to determine which graphic to draw at which coordinate, ultimately building a master `tmx_surface` visual map.
- **`room.py`:** Reads objects from those tiles specifically. 
    - *Example (Collision):* Checks if tiles exist on a map layer called "border" or "furniture" and attaches invisible `pygame.Rect` collision walls over them.
    - *Example (Interactables):* Checks if a layer named "desk" or "door2" exists and associates them with `Interactable` objects linked to puzzle string IDs (like `blinking_lights`).

### `states/room_state.py` (The Main Gameplay Loop)
The brains of the Escape Room itself. 
- **`enter()`:** Builds the correct level map using `build_easy_room_from_tmx()` or `build_level2_room_from_tmx()`. It spawns the player either at the starting origin, or wherever the resume snapshot dictates.
- **Camera Scaling:** Uses math like `scale_x = screen_w / self.room.pixel_w` to ensure that no matter the native pixel size of the Tiled map, it elegantly expands to fill the game window while remaining centered.
- **`_interact(self, obj)`:** Executed when "E" is pressed on an object. 
    - If the object has a puzzle, it `self.machine.push(PuzzleState(...))`.
    - Level 2 uniquely overrides this to introduce physical bump-back mechanics if the player hits the "Loose Tile", rejecting their coordinates backwards until they attempt it a third time.
- **Blinking Lights Logic:** Generates real-time ambient lighting pulses mapping to RGB loop sequences based on math: `if (t % 1.0) < 0.5: draw red` before drawing the HUD.

### `states/puzzle_state.py` & `puzzles/` (Solving Riddles)
- **`puzzle_state.py`:** An interactive "pop-up" window state drawn specifically with a translucent black background over the paused Room background. It accepts raw keyboard string manipulation.
- **`easy_puzzles.py` / `level2_puzzles.py`:** These hold dedicated Classes for every riddle. They define descriptions and the required `solution` strings. 
    - When you type an answer in `PuzzleState`, it passes your input to the puzzle class's `check_answer(user_input)` function. If `True` is returned, a callback updates the Room, visually unlocks the interactive, and saves the game mechanically.

### `engine/save_system.py`
A simple JSON database script. When the user transitions maps, opens the menu, or quits, `save_game()` gathers variables like `current_room` and the array of strings defining `puzzles_solved`. It writes them securely inside an invisible `.save` json file. Checking for "Continue" strictly searches the local disk for this saved file map.

---

## Summary of the Gameplay Loop Code:
1. User types name and hits **New Game** in `MenuState`.
2. Machine removes `MenuState` and creates `RoomState`.
3. `RoomState.enter()` notices we want Level 1. Calls `tmx_loader` to fetch Tiled layout and create a `Room` Class with walls. Puts `Player` in the room.
4. User presses WASD. Code in `Player.move` updates coordinates smoothly based on framerate `dt` and prevents overlapping the rectangle math of `Room.walls`.
5. User steps near a desk (`Room` function checks inflation overlap between objects and player) and hits 'E'.
6. `RoomState` triggers `machine.push(PuzzleState)`. The room freezes, the puzzle pops up!
7. User types correct code. PuzzleState returns `True`, runs puzzle callback. Object marked as `solved`.
8. Once all objects solved, Door changes label from 🔒 to 🔓. Interacting opens it and alters `current_level` in the global `ctx` dict, refreshing the loop for Level 2!
