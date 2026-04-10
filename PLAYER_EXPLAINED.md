# Deep Dive: engine/player.py (Line-by-Line)

This file is the "Heart" of the character. It handles how they look, how they walk, and how they interact with the physical world (walls).

---

## 1. Configurations & Constants
- **`SPRITE_CHARS` (Lines 14-41)**: This is a dictionary that acts as a library. It tells the game exactly where the images for "Finn" and "Maeve" are stored.
    - `folder`: The path to the character's images.
    - `sheet`: The main animation file.
    - `idle_down/up/left/right`: Specific files used when the character is standing still.
- **`SPRITE_W = 96, SPRITE_H = 144` (Lines 45-46)**: These set the visual size of the character. Notice they are taller than they are wide, which gives that classic RPG look.

---

## 2. Image Loading Logic
- **`load_sprite_images(sprite_id)` (Lines 49-119)**:
    - This function "chops" the sprite sheet.
    - **`sheet.subsurface(pygame.Rect(...))`**: This is a powerful Pygame command. It says "Take this big image, but only give me a small piece of it."
    - It uses a loop to cut out 4 frames for each direction (Down, Up, Left, Right).
    - **`pygame.transform.smoothscale(...)`**: This takes those small pieces and stretches them to the 96x144 size we want.
- **`load_idle_images(sprite_id)` (Lines 148-181)**:
    - This loads the "Idle" (standing still) pictures.
    - **`img.get_bounding_rect()`**: This is smart logic. It finds the actual colored pixels and removes any empty transparent space around the character. This ensures Finn doesn't look like he's floating.

---

## 3. The Player Class (The Blueprint)
- **`class Player` (Lines 184-332)**:
    - **`COLLIDE_W = 50, COLLIDE_H = 50` (Lines 190-191)**: This is crucial. The character's *visual* size is 96x144, but their *physical* hitbox is only 50x50. This allows the character's head/shoulders to overlap walls slightly, making the game feel 3D (Z-axis depth).
    - **`self.pos_x, self.pos_y` (Lines 199-200)**: We use floats (decimal numbers) so movement is perfectly smooth.
    - **`self.frame_index` (Line 207)**: A counter that decides which of the 4 walking frames to show. It increases by `anim_speed` every second.

---

## 4. Movement & Physics (The Hardest Part)
- **`handle_input(keys)` (Lines 220-234)**:
    - Checks `pygame.K_LEFT`, `K_w`, etc.
    - Sets `vx` (horizontal speed) and `vy` (vertical speed).
    - Updates `self.direction` so we know which way to face.
- **`move(dt, walls)` (Lines 236-271)**:
    - **The 2-Step Collision**: 
        1. **X-Axis**: We move the player horizontally. We check if they hit a wall. If they did, we stop them exactly at the wall's edge.
        2. **Y-Axis**: *Then* we move them vertically and check walls again.
    - **Why 2 steps?** If we did both at once, you would get stuck on corners. By doing it separately, you can "slide" along a wall while walking diagonally.
    - **`round(self.pos_x)`**: We convert our decimal position back to a whole pixel number before drawing, so the character doesn't look "blurry."

---

## 5. Rendering (The Final Result)
- **`draw(surface)` (Lines 275-300)**:
    - **`if not self.is_moving`**: If the player is standing still, it uses the "Idle" image.
    - **`idx = int(self.frame_index) % len(frames)`**: This math takes our constantly increasing `frame_index` (0.0, 0.1, 0.2...) and turns it into an integer (0, 1, 2, or 3) to pick the current walking frame.
    - **`draw_x = self.rect.centerx - ...`**: This math centers the character image over their feet (the collision box).
- **`_draw_placeholder` (Lines 302-332)**:
    - This is a "Safety" function. If the character's images fail to load, the game draws a blue rectangle with eyes so you can still play.
    - It even draws the eyes in different spots based on which way the rectangle is "facing"!

---
*End of Player Breakdown*
