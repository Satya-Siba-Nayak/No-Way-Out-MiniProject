"""
Player sprite — handles movement, rendering, and collision.
Supports both placeholder rectangle and loaded sprite images.
"""

import os
import pygame


# Base directory for sprite assets
_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Sprite configs: maps sprite_id to (folder_name, display_name)
SPRITE_CHARS = {
    "finn": {
        "name": "Finn",
        "folder": os.path.join(_BASE_DIR, "data", "Sprite 1(Finn)"),
        "pfp": "PFP.png",
        "sheet": "sprite sheet ( finn).png",
        "idle_down": "User Facing.png",
        "idle_up": "Away Facing.png",
        "idle_left": "Left Facing.png",
        "idle_right": "Right Facing.png",
    },
    "maeve": {
        "name": "Maeve",
        "folder": os.path.join(_BASE_DIR, "data", "Sprite 2 (Maeve)"),
        "pfp": "PFP.png",
        "down": "User Facing.png",
        "up": "Away Facing.png",
        "left": "Left Facing.png",
        "right": "Right Facing.png",
    },
}

# Target sprite size in-game (scaled down from the large originals)
# ~3 tiles wide, ~4.5 tiles tall — very large and prominent
SPRITE_W = 96
SPRITE_H = 144


def load_sprite_images(sprite_id):
    """
    Load and scale down the directional sprite images for a character.

    Returns:
        dict mapping direction ("up","down","left","right") to scaled Surface,
        or None if the sprite_id is not found or images fail to load.
    """
    config = SPRITE_CHARS.get(sprite_id)
    if not config:
        return None

    folder = config["folder"]
    images = {}

    if "sheet" in config:
        sheet_path = os.path.join(folder, config["sheet"])
        if os.path.exists(sheet_path):
            try:
                sheet = pygame.image.load(sheet_path).convert_alpha()
                sheet_w, sheet_h = sheet.get_size()
                
                num_frames = 4
                frame_w = sheet_w // num_frames
                frame_h = sheet_h // 4
                
                row_map = {"down": 0, "up": 1, "left": 2, "right": 3}
                
                for direction, row in row_map.items():
                    direction_frames = []
                    for i in range(num_frames):
                        rect = pygame.Rect(i * frame_w, row * frame_h, frame_w, frame_h)
                        frame_surf = sheet.subsurface(rect)
                        frame_surf = pygame.transform.smoothscale(frame_surf, (SPRITE_W, SPRITE_H))
                        direction_frames.append(frame_surf)
                    images[direction] = direction_frames
            except pygame.error as e:
                print(f"[Player] WARNING: failed to load sheet {sheet_path}: {e}")
        else:
            print(f"[Player] WARNING: sheet not found: {sheet_path}")
            
    else:
        # Fallback for individual directional files (e.g. Maeve still uses this if she's not updated)
        for direction in ("up", "down", "left", "right"):
            filename = config.get(direction)
            if not filename:
                continue
            path = os.path.join(folder, filename)
            if os.path.exists(path):
                try:
                    sheet = pygame.image.load(path).convert_alpha()
                    sheet_w, sheet_h = sheet.get_size()
                    
                    num_frames = 4
                    frame_w = sheet_w // num_frames
                    
                    if sheet_h > frame_w * 2: 
                        frame_h = sheet_h // 4
                    else:
                        frame_h = sheet_h
                    
                    direction_frames = []
                    for i in range(num_frames):
                        rect = pygame.Rect(i * frame_w, 0, frame_w, frame_h)
                        frame_surf = sheet.subsurface(rect)
                        frame_surf = pygame.transform.smoothscale(frame_surf, (SPRITE_W, SPRITE_H))
                        direction_frames.append(frame_surf)
                        
                    images[direction] = direction_frames
                except pygame.error as e:
                    print(f"[Player] WARNING: failed to load {path}: {e}")
            else:
                print(f"[Player] WARNING: sprite not found: {path}")

    return images if images else None


def load_pfp(sprite_id, size=(100, 100)):
    """
    Load the profile picture for a character selection screen.

    Args:
        sprite_id: "finn" or "maeve"
        size: target (width, height)

    Returns:
        pygame.Surface or None
    """
    config = SPRITE_CHARS.get(sprite_id)
    if not config:
        return None

    path = os.path.join(config["folder"], config["pfp"])
    if not os.path.exists(path):
        return None

    try:
        img = pygame.image.load(path).convert_alpha()
        img = pygame.transform.smoothscale(img, size)
        return img
    except pygame.error:
        return None


def load_idle_images(sprite_id):
    """
    Load specific single-frame idle images if defined in config,
    scaling them properly to the game size.
    """
    config = SPRITE_CHARS.get(sprite_id)
    if not config:
        return None
        
    folder = config["folder"]
    idle_images = {}
    
    for direction in ("up", "down", "left", "right"):
        key = f"idle_{direction}"
        if key in config:
            path = os.path.join(folder, config[key])
            if os.path.exists(path):
                try:
                    img = pygame.image.load(path).convert_alpha()
                    # Crop idle image to its actual bounding box to remove extra padding
                    bbox = img.get_bounding_rect()
                    img = img.subsurface(bbox)
                    
                    # Scale it such that the physical character height matches the animated frame's physical character height (~130px)
                    target_h = 130
                    scale = target_h / float(bbox.h)
                    target_w = int(bbox.w * scale)
                    img = pygame.transform.smoothscale(img, (target_w, target_h))
                    idle_images[direction] = img
                except pygame.error as e:
                    print(f"[Player] WARNING: failed to load idle {path}: {e}")
                    
    return idle_images if idle_images else None


class Player:
    """The player character."""

    WIDTH = SPRITE_W
    HEIGHT = SPRITE_H
    # Collision box is smaller than the visual sprite for smoother movement
    COLLIDE_W = 50
    COLLIDE_H = 50
    SPEED = 160          # pixels per second
    COLOR = (100, 200, 255)           # light-blue placeholder
    OUTLINE_COLOR = (50, 120, 180)    # darker outline

    def __init__(self, x, y, sprite_id=None):
        # The collision rect is centered at the bottom of the sprite
        self.rect = pygame.Rect(x, y, self.COLLIDE_W, self.COLLIDE_H)
        
        # Use float variables to track actual position without losing sub-pixel precision
        self.pos_x = float(x)
        self.pos_y = float(y)
        
        self.direction = "down"       # last facing direction
        self.sprite_id = sprite_id
        self.render_scale = 1.0       # allow resizing the drawn sprite

        # Animation state
        self.frame_index = 0.0
        self.anim_speed = 6.0 # frames per second
        self.is_moving = False
        
        # Load sprite images if a sprite_id is given
        self.sprites = None
        self.idle_sprites = None
        if sprite_id:
            self.sprites = load_sprite_images(sprite_id)
            self.idle_sprites = load_idle_images(sprite_id)

    # --- Movement -----------------------------------------------------------

    def handle_input(self, keys):
        """Read WASD / Arrow keys and return a velocity vector."""
        vx, vy = 0, 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            vx = -self.SPEED
            self.direction = "left"
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            vx = self.SPEED
            self.direction = "right"
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            vy = -self.SPEED
            self.direction = "up"
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            vy = self.SPEED
            self.direction = "down"
        return vx, vy

    def move(self, dt, walls):
        """Move the player, handling wall collisions axis-by-axis."""
        keys = pygame.key.get_pressed()
        vx, vy = self.handle_input(keys)

        old_x, old_y = self.rect.x, self.rect.y

        # Horizontal movement + collision
        self.pos_x += vx * dt
        self.rect.x = int(round(self.pos_x))
        for wall in walls:
            if self.rect.colliderect(wall):
                if vx > 0:
                    self.rect.right = wall.left
                elif vx < 0:
                    self.rect.left = wall.right
                # Sync float pos to actual integer pos if collision happens
                self.pos_x = float(self.rect.x)

        # Vertical movement + collision
        self.pos_y += vy * dt
        self.rect.y = int(round(self.pos_y))
        for wall in walls:
            if self.rect.colliderect(wall):
                if vy > 0:
                    self.rect.bottom = wall.top
                elif vy < 0:
                    self.rect.top = wall.bottom
                # Sync float pos to actual integer pos if collision happens
                self.pos_y = float(self.rect.y)
                
        # Check actual physical displacement indicating non-obstructed moving
        self.is_moving = (self.rect.x != old_x) or (self.rect.y != old_y)
        
        # Animation update: only advance frames if actually moving (not stuck)
        if self.is_moving:
            self.frame_index += self.anim_speed * dt
            if self.frame_index >= 4:
                self.frame_index = 0.0
        else:
            self.frame_index = 0.0 # reset to idle frame

    # --- Drawing ------------------------------------------------------------

    def draw(self, surface):
        """Draw the player — uses sprite images if available, else placeholder."""
        if self.sprites and self.direction in self.sprites:
            # If we're not moving and have a dedicated idle sprite, use it!
            if not self.is_moving and self.idle_sprites and self.direction in self.idle_sprites:
                sprite_img = self.idle_sprites[self.direction]
            else:
                frames = self.sprites[self.direction]
                idx = int(self.frame_index) % len(frames)
                sprite_img = frames[idx]
            
            # Apply render_scale dynamically if needed
            if getattr(self, "render_scale", 1.0) != 1.0:
                w = int(sprite_img.get_width() * self.render_scale)
                h = int(sprite_img.get_height() * self.render_scale)
                sprite_img = pygame.transform.smoothscale(sprite_img, (w, h))
            
            # Align the bottom of the sprite image with the bottom of the collision rect
            # Center the sprite horizontally on the collision rect
            draw_x = self.rect.centerx - (sprite_img.get_width() // 2)
            draw_y = self.rect.bottom - sprite_img.get_height()
            
            surface.blit(sprite_img, (draw_x, draw_y))
        else:
            self._draw_placeholder(surface)

    def _draw_placeholder(self, surface):
        """Draw a placeholder character (rectangle with eyes)."""
        # Body
        pygame.draw.rect(surface, self.COLOR, self.rect)
        pygame.draw.rect(surface, self.OUTLINE_COLOR, self.rect, 2)

        # Simple face — two eyes depending on direction
        cx, cy = self.rect.centerx, self.rect.centery - 4
        eye_offset = 5
        eye_size = 3

        if self.direction == "down":
            pygame.draw.circle(surface, (0, 0, 0), (cx - eye_offset, cy), eye_size)
            pygame.draw.circle(surface, (0, 0, 0), (cx + eye_offset, cy), eye_size)
        elif self.direction == "up":
            # Eyes not visible from behind — draw hair line
            pygame.draw.line(surface, self.OUTLINE_COLOR,
                             (self.rect.left + 4, self.rect.top + 4),
                             (self.rect.right - 4, self.rect.top + 4), 2)
        elif self.direction == "left":
            pygame.draw.circle(surface, (0, 0, 0), (cx - eye_offset, cy), eye_size)
        elif self.direction == "right":
            pygame.draw.circle(surface, (0, 0, 0), (cx + eye_offset, cy), eye_size)
