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
        "down": "User Facing.png",
        "up": "Away Facing.png",
        "left": "Left Facing.png",
        "right": "Right Facing.png",
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
# ~2 tiles wide, ~3 tiles tall — clearly visible to the user
SPRITE_W = 64
SPRITE_H = 96


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

    for direction in ("up", "down", "left", "right"):
        filename = config[direction]
        path = os.path.join(folder, filename)
        if os.path.exists(path):
            try:
                img = pygame.image.load(path).convert_alpha()
                # Scale down to game size
                img = pygame.transform.smoothscale(img, (SPRITE_W, SPRITE_H))
                images[direction] = img
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


class Player:
    """The player character."""

    WIDTH = SPRITE_W
    HEIGHT = SPRITE_H
    # Collision box is smaller than the visual sprite for smoother movement
    COLLIDE_W = 40
    COLLIDE_H = 40
    SPEED = 160          # pixels per second
    COLOR = (100, 200, 255)           # light-blue placeholder
    OUTLINE_COLOR = (50, 120, 180)    # darker outline

    def __init__(self, x, y, sprite_id=None):
        # The collision rect is centered at the bottom of the sprite
        self.rect = pygame.Rect(x, y, self.COLLIDE_W, self.COLLIDE_H)
        self.direction = "down"       # last facing direction
        self.sprite_id = sprite_id

        # Load sprite images if a sprite_id is given
        self.sprites = None
        if sprite_id:
            self.sprites = load_sprite_images(sprite_id)

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

        # Horizontal movement + collision
        self.rect.x += int(vx * dt)
        for wall in walls:
            if self.rect.colliderect(wall):
                if vx > 0:
                    self.rect.right = wall.left
                elif vx < 0:
                    self.rect.left = wall.right

        # Vertical movement + collision
        self.rect.y += int(vy * dt)
        for wall in walls:
            if self.rect.colliderect(wall):
                if vy > 0:
                    self.rect.bottom = wall.top
                elif vy < 0:
                    self.rect.top = wall.bottom

    # --- Drawing ------------------------------------------------------------

    def draw(self, surface):
        """Draw the player — uses sprite images if available, else placeholder."""
        if self.sprites and self.direction in self.sprites:
            sprite_img = self.sprites[self.direction]
            surface.blit(sprite_img, self.rect.topleft)
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
