"""
Room — defines the tile-based room layout, walls, and interactable objects.

This is a placeholder room built with code. When Keya finishes the .tmx file
in Tiled, we can replace `build_easy_room()` with a TMX loader.
"""

import pygame

# Tile size in pixels
TILE = 32


class Interactable:
    """An object the player can interact with (desk, panel, bed, door)."""

    def __init__(self, rect, label, puzzle_id=None, color=(180, 140, 80)):
        self.rect = rect
        self.label = label              # display name
        self.puzzle_id = puzzle_id      # which puzzle this triggers (None = door)
        self.color = color
        self.solved = False

    def draw(self, surface, font):
        """Draw the object as a colored block with a label."""
        c = (80, 180, 80) if self.solved else self.color
        pygame.draw.rect(surface, c, self.rect)
        pygame.draw.rect(surface, (0, 0, 0), self.rect, 2)

        # Label above the object
        lbl = font.render(self.label, True, (255, 255, 255))
        lbl_rect = lbl.get_rect(midbottom=(self.rect.centerx, self.rect.top - 2))
        surface.blit(lbl, lbl_rect)


class Room:
    """Holds the layout for a single room."""

    def __init__(self, width_tiles, height_tiles):
        self.w = width_tiles
        self.h = height_tiles
        self.pixel_w = width_tiles * TILE
        self.pixel_h = height_tiles * TILE
        self.walls = []               # list of pygame.Rect (collision)
        self.interactables = []       # list of Interactable
        self.floor_color = (60, 55, 50)
        self.wall_color = (90, 80, 70)

    # --- Layout builders (called once) --------------------------------------

    def build_walls_border(self):
        """Create wall rects around the room perimeter."""
        # Top wall
        self.walls.append(pygame.Rect(0, 0, self.pixel_w, TILE))
        # Bottom wall
        self.walls.append(pygame.Rect(0, self.pixel_h - TILE, self.pixel_w, TILE))
        # Left wall
        self.walls.append(pygame.Rect(0, 0, TILE, self.pixel_h))
        # Right wall
        self.walls.append(pygame.Rect(self.pixel_w - TILE, 0, TILE, self.pixel_h))

    # --- Drawing ------------------------------------------------------------

    def draw(self, surface, font):
        """Draw floor, walls, and interactables."""
        # Floor
        surface.fill(self.floor_color)

        # Walls
        for wall in self.walls:
            pygame.draw.rect(surface, self.wall_color, wall)
            # Brick pattern
            for bx in range(wall.left, wall.right, TILE):
                for by in range(wall.top, wall.bottom, TILE):
                    pygame.draw.rect(surface, (70, 65, 55),
                                     (bx, by, TILE, TILE), 1)

        # Interactable objects
        for obj in self.interactables:
            obj.draw(surface, font)

    # --- Query helpers ------------------------------------------------------

    def get_nearby_interactable(self, player_rect, reach=10):
        """Return the interactable the player is close enough to, or None."""
        expanded = player_rect.inflate(reach * 2, reach * 2)
        for obj in self.interactables:
            if expanded.colliderect(obj.rect):
                return obj
        return None

    def all_puzzles_solved(self):
        """Check if every puzzle interactable is solved."""
        return all(
            obj.solved for obj in self.interactables if obj.puzzle_id is not None
        )


def build_easy_room():
    """
    Build the Easy-level escape room.
    Layout (25×15 tiles = 800×480 pixels — fits in our 816×480 window):

        ┌──────────────────────────┐
        │  [Desk]          [Panel] │
        │                          │
        │                          │
        │        (player start)    │
        │                          │
        │  [Bed]           [Door]  │
        └──────────────────────────┘
    """
    room = Room(25, 15)
    room.build_walls_border()

    # Offset to center the 800px room in the 816px window
    ox, oy = 8, 0

    # === Interactable Objects ===============================================

    # Desk (top-left area) — triggers Caesar Cipher puzzle
    desk = Interactable(
        rect=pygame.Rect(ox + TILE * 2, TILE + 8, TILE * 3, TILE * 2),
        label="Desk",
        puzzle_id="caesar_cipher",
        color=(139, 90, 43),       # brown wood
    )

    # Light Panel (top-right area) — triggers Binary Lock puzzle
    panel = Interactable(
        rect=pygame.Rect(ox + TILE * 20, TILE + 8, TILE * 2, TILE * 2),
        label="Panel",
        puzzle_id="binary_lock",
        color=(60, 60, 90),        # dark metal
    )

    # Bed (bottom-left area) — triggers String Slicing puzzle
    bed = Interactable(
        rect=pygame.Rect(ox + TILE * 2, TILE * 11, TILE * 3, TILE * 2),
        label="Bed",
        puzzle_id="bed_slicing",
        color=(120, 80, 80),       # reddish-brown
    )

    # Door (bottom-right) — locked until all puzzles solved
    door = Interactable(
        rect=pygame.Rect(ox + TILE * 21, TILE * 11, TILE * 2, TILE * 3),
        label="Door 🔒",
        puzzle_id=None,            # not a puzzle — it's the exit
        color=(100, 60, 40),       # dark wood door
    )

    room.interactables = [desk, panel, bed, door]

    # Add the interactable rects as walls so the player can't walk through them
    for obj in room.interactables:
        room.walls.append(obj.rect)

    # Some extra interior walls for atmosphere (table, bookshelf)
    # Bookshelf along top-center
    bookshelf_rect = pygame.Rect(ox + TILE * 9, TILE, TILE * 5, TILE)
    room.walls.append(bookshelf_rect)

    # Player start position (center of room)
    start_x = ox + room.pixel_w // 2 - 14
    start_y = room.pixel_h // 2 - 20

    return room, (start_x, start_y), bookshelf_rect
