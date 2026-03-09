# Escape Room Project: Login Screen Implementation

This document explains the technical implementation of the login screen for our Pygame-based escape room project.

## 1. Prerequisites
We integrated the **Pillow (PIL)** library to handle GIF files, as Pygame does not natively support animated GIFs.
* **Command:** `pip install Pillow`
* **Reason:** Allows us to open the GIF, extract individual frames, and convert them into Pygame-compatible surfaces.

## 2. Animated Background (GIF)
To create the looping background, we implemented a custom loader:
* **`load_gif_frames` function:** Iterates through every frame of the GIF, converts it to RGBA format, and scales it up.
* **Scaling:** We used a `SCALE_FACTOR` of 3. This transforms the original small GIF (272x160) into a larger window (816x480) while keeping the pixel art sharp.
* **Animation Loop:** We use a `frame_counter` and `frame_delay` in the main loop. This prevents the animation from running too fast, creating a "slow loop" effect.

## 3. User Interface (UI) Design
* **Readability Overlay:** We draw a semi-transparent black rectangle (`SRCALPHA`) over the background. This "darkens" the GIF so that white text and the input box are easy to read.
* **Relative Positioning:** Instead of hardcoding pixel values (like 100, 200), we used `WINDOW_WIDTH // 2` and `WINDOW_HEIGHT * 0.2`. This ensures that if we change the window size later, the UI stays centered.
* **Blinking Cursor:** Implemented using `pygame.time.get_ticks()`. We toggle the `|` character every 500ms to give the input box a professional feel.

## 4. Input Handling
We use the `pygame.KEYDOWN` event to capture user typing:
* **Character Limit:** Set to 15 characters to prevent the text from overflowing the box.
* **Backspace:** Allows users to correct mistakes by slicing the string: `player_name[:-1]`.
* **Enter Key:** Validates that the name isn't empty before transitioning to the next screen.

## 5. State Management
This is the most important architectural part for future development. We use a "State Machine" pattern:
* **States:** `STATE_LOGIN` and `STATE_GAME`.
* **Logic:** The `while` loop checks `current_state`. If it's `login`, it shows the input box. If it's `game`, it shows the "Work in Progress" message.
* **Benefit:** This allows us to easily add new screens (like a "Game Over" or "Settings" screen) by simply adding a new state and a corresponding `if` block.

## 6. How to Run
1. Ensure the virtual environment is active.
2. Run `python main.py`.
3. Type your name and press **Enter** to see the transition.
