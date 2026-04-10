# NO WAY OUT? - Line-by-Line Technical Breakdown

This document provides a detailed explanation of every file and the logic behind the code.

---

## 1. main.py (The Entry Point)
This file initializes the game window and runs the main loop.

- **`import sys, pygame`**: Standard libraries for system operations and game development.
- **`from engine.state_machine import StateMachine`**: Imports our custom manager that handles switching between Menu, Game, and Puzzles.
- **`GIF_PATH = ...`**: Defines the background animation file.
- **`get_gif_dimensions(path)`**: Uses the Pillow library to find the original size of the GIF (272x160). We scale this by 3 to get our 816x480 window.
- **`main()` function**:
    - `pygame.init()`: Starts Pygame's internal engines (graphics, sound).
    - `screen = pygame.display.set_mode(...)`: Creates the actual window you see.
    - `game_context = { ... }`: A dictionary passed to every state. It stores "global" data like the player's name and screen size without using global variables (cleaner code).
    - `sm = StateMachine()`: Creates the "brain" of our game navigation.
    - `sm.push(MenuState(...))`: Tells the brain to start on the Menu screen.
- **The While Loop**:
    - `dt = clock.tick(60) / 1000.0`: Calculates "Delta Time". If the game lags, `dt` gets larger, ensuring player movement stays at the same speed regardless of FPS.
    - `sm.handle_events(events)`: Passes mouse clicks/keypresses to the current screen.
    - `sm.update(dt)` / `sm.draw(screen)`: Runs the math and graphics for the current screen.

---

## 2. engine/state_machine.py (The Brain)
Manages the "Stack" of game screens.

- **`self._states = []`**: A list (stack). The last item in the list is the screen you are currently looking at.
- **`push(state)`**: When you open a puzzle, we "push" the PuzzleState onto the list. The RoomState stays in the list but stops moving (`pause()`).
- **`pop()`**: When you close a puzzle, we remove it from the list. The RoomState becomes the top item again and resumes.
- **`change(state)`**: Replaces the current state entirely (e.g., from Menu to Room).

---

## 3. engine/player.py (Movement & Animation)
Handles everything related to the character "Finn" or "Maeve".

- **`SPRITE_CHARS`**: Configures the folder paths for the character images.
- **`load_sprite_images()`**:
    - It loads the "sprite sheet" (a grid of character poses).
    - It uses `subsurface()` to cut that grid into individual frames (Walking Down, Up, Left, Right).
    - It scales them up for the game window.
- **`Player` class**:
    - `self.pos_x, self.pos_y`: Uses floats for coordinates to allow for smooth, slow movement that isn't jerky.
    - `handle_input()`: Checks if A, W, S, D or Arrows are held. It returns a "velocity" (speed and direction).
    - `move(dt, walls)`: 
        - It tries to move the player horizontally. 
        - It loops through all `walls`. If the player's box overlaps a wall, it snaps the player back to the edge of the wall.
        - It then repeats this for the vertical axis. This is why you can "slide" along walls!
    - `draw()`: Based on `self.direction` and `self.frame_index`, it picks the correct image from the list and draws it so the character's feet are at the bottom of their collision box.

---

## 4. engine/room.py (The Map & Interaction)
Defines what is in the room and how it looks.

- **`Interactable` class**:
    - `rect`: The physical space the object (desk/couch) occupies.
    - `puzzle_id`: Tells the game which puzzle to open when the player interacts with this object.
- **`Room` class**:
    - `self.walls`: A list of rectangles the player cannot walk through.
    - `draw()`: If using a Tiled map (TMX), it draws the pre-rendered image. Otherwise, it draws colored boxes.
    - `get_nearby_interactable()`: Uses `rect.inflate()` to create an invisible "interaction circle" around the player. If this circle touches an object, the "Press E" prompt appears.
- **`build_easy_room_from_tmx()`**:
    - Uses our `tmx_loader` to load `EasyLevel1.tmx`.
    - It looks for map layers named "desk", "couch", etc., and automatically creates walls and interactable objects at those locations.

---

## 5. engine/tmx_loader.py (The Map Importer)
The most complex part. It reads the `.tmx` files (which are just XML data) and turns them into images.

- **`TilesetInfo`**: Loads the "tileset" image (e.g., floor and wall textures) and cuts it into 32x32 tiles.
- **`TiledMap.render()`**: 
    - This creates one giant, empty image the size of the whole room.
    - It loops through every "Layer" in the Tiled file.
    - It draws every tile onto this giant image once.
    - This is way faster for the computer than drawing 1,000 tiny tiles every frame.

---

## 6. states/menu_state.py (The Title Screen)
- **`load_gif_frames()`**: Uses the Pillow library to frame-by-frame extract the background GIF.
- **`handle_events()`**: 
    - Checks for mouse clicks on the Settings icon.
    - Handles typing the player name.
    - Handles moving the selection cursor in the menu.
- **`_draw_settings()`**: Features the logic for the Volume Slider. It calculates how far the mouse is across the "slider track" to set the volume percentage.

---

## 7. states/room_state.py (The Gameplay)
The bridge between the Player, the Room, and the Puzzles.

- **`enter()`**: Loads the map, places the player, and loads any saved game data.
- **`update()`**: 
    - Calls `player.move()`.
    - Updates the `blink_timer` for the Level 2 light show.
    - Handles the "Bump Physics" in Level 2 (pushes you back if you haven't solved the tile puzzle).
- **`_interact()`**: When you press 'E', it finds the puzzle associated with the object and pushes a new `PuzzleState`.
- **`draw()`**: Draws the map, then the player, then the "HUD" (the bar at the bottom with your name and progress).

---

## 8. states/puzzle_state.py (The Puzzle Overlay)
- **`draw()`**: Draws a dark semi-transparent rectangle to dim the gameplay, then draws the "Puzzle Box".
- **`handle_events()`**: 
    - Capture keyboard typing.
    - `self.user_input += event.unicode` adds the letter you typed to the screen.
- **`_submit()`**: Calls the specific puzzle logic (e.g., Caesar Cipher) to check if your answer matches the solution.

---

## 9. puzzles/easy_puzzles.py & level2_puzzles.py (The Logic)
- **`CaesarCipher`**: Takes a string like "KHOOR" and checks if the user types "HELLO" (shift of 3).
- **`BinaryLock`**: Uses `random.randint` to generate a binary code. It uses the formula `sum(bit * (2 ** i))` to calculate the correct answer.
- **`CouchSlicing`**: Checks if the user types `ZZZGOLDZZZ[3:7]`, which is "GOLD".
- **`PaintingPuzzle`**: Loads the `Painting.png` image and checks for the code "1379".

---
*End of Code Explanation*
