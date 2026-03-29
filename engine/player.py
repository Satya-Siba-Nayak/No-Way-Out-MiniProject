"""
Player sprite — handles movement, rendering, and collision.
Uses a simple colored rectangle until Sneha provides pixel art.
"""

import pygame


class Player:
    """The player character."""

    WIDTH = 28
    HEIGHT = 40
    SPEED = 160          # pixels per second
    COLOR = (100, 200, 255)           # light-blue placeholder
    OUTLINE_COLOR = (50, 120, 180)    # darker outline

    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, self.WIDTH, self.HEIGHT)
        self.direction = "down"       # last facing direction

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
