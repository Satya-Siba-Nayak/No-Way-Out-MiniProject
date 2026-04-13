"""
Room — defines the tile-based room layout, walls, and interactable objects.

Supports both the legacy code-built room and TMX-loaded rooms.
"""

import os
import pygame
from engine.tmx_loader import load_tmx

# Tile size in pixels (map grid size)
TILE = 32

# Path to the TMX map for the Easy level
_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EASY_TMX_PATH = os.path.join(
    _BASE_DIR, "Maps", "Level 1", "Tiled images", "EasyLevel1.tmx"
)
LEVEL2_TMX_PATH = os.path.join(
    _BASE_DIR, "Maps", "Level 2 - new", "Tiled images", "HallwayLevel2.tmx"
)


class Interactable:
    """An object the player can interact with (desk, panel, couch, door)."""

    def __init__(self, rect, label, puzzle_id=None, color=(180, 140, 80)):
        self.rect = rect
        self.label = label              # display name
        self.puzzle_id = puzzle_id      # which puzzle this triggers (None = door)
        self.color = color
        self.solved = False

    def draw(self, surface, font, show_colored_block=True):
        """Draw the object as a colored block with a label (legacy mode)."""
        if show_colored_block:
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
        self.light_positions = []     # list of pygame.Rect (for blinking lights)
        self.floor_color = (60, 55, 50)
        self.wall_color = (90, 80, 70)

        # TMX rendering
        self.tmx_surface = None       # pre-rendered map (or None for legacy)

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
        if self.tmx_surface is not None:
            # TMX mode — blit the pre-rendered tile map
            surface.blit(self.tmx_surface, (0, 0))
            # Don't draw colored blocks over the tile art
            for obj in self.interactables:
                obj.draw(surface, font, show_colored_block=False)
        else:
            # Legacy mode — colored rectangles
            surface.fill(self.floor_color)
            for wall in self.walls:
                pygame.draw.rect(surface, self.wall_color, wall)
                for bx in range(wall.left, wall.right, TILE):
                    for by in range(wall.top, wall.bottom, TILE):
                        pygame.draw.rect(surface, (70, 65, 55),
                                         (bx, by, TILE, TILE), 1)
            for obj in self.interactables:
                obj.draw(surface, font, show_colored_block=True)

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


# ═══════════════════════════════════════════════════════════════════════════════
# Room Builders
# ═══════════════════════════════════════════════════════════════════════════════


def build_easy_room():
    """
    Build the Easy-level escape room (legacy / fallback version).
    Layout (25×15 tiles = 800×480 pixels — fits in our 816×480 window):

        ┌──────────────────────────┐
        │  [Desk]          [Panel] │
        │                          │
        │                          │
        │        (player start)    │
        │                          │
        │  [Couch]         [Door]  │
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

    # Couch (bottom-left area) — triggers String Slicing puzzle
    couch = Interactable(
        rect=pygame.Rect(ox + TILE * 2, TILE * 11, TILE * 3, TILE * 2),
        label="Couch",
        puzzle_id="couch_slicing",
        color=(120, 80, 80),       # reddish-brown
    )

    # Door (bottom-right) — locked until all puzzles solved
    door = Interactable(
        rect=pygame.Rect(ox + TILE * 21, TILE * 11, TILE * 2, TILE * 3),
        label="Door 🔒",
        puzzle_id=None,            # not a puzzle — it's the exit
        color=(100, 60, 40),       # dark wood door
    )

    room.interactables = [desk, panel, couch, door]

    # Add the interactable rects as walls so the player can't walk through them
    for obj in room.interactables:
        room.walls.append(obj.rect)

    # Some extra interior walls for atmosphere (bookshelf)
    bookshelf_rect = pygame.Rect(ox + TILE * 9, TILE, TILE * 5, TILE)
    room.walls.append(bookshelf_rect)

    # Player start position (center of room)
    start_x = ox + room.pixel_w // 2 - 14
    start_y = room.pixel_h // 2 - 20

    return room, (start_x, start_y), bookshelf_rect


def build_easy_room_from_tmx():
    """
    Build the Easy-level escape room from the EasyLevel1.tmx Tiled map.

    The TMX map is 15×20 tiles (480×640 px).
    Interactable objects are placed based on the named tile layers in the TMX:
      - desk       → Caesar cipher puzzle
      - lightboard → Binary lock puzzle
      - couch      → String slicing puzzle
      - escapedoor → Exit door (unlocks when all puzzles solved)

    Returns:
        (room, player_start_pos)
    """
    if not os.path.exists(EASY_TMX_PATH):
        print("[Room] TMX file not found, falling back to legacy room.")
        room, start, _ = build_easy_room()
        return room, start

    print("[Room] Loading TMX map...")
    tiled_map = load_tmx(EASY_TMX_PATH)

    room = Room(tiled_map.width, tiled_map.height)

    # Pre-render the tile map
    room.tmx_surface = tiled_map.render()

    # === Build wall collisions from the border layer =========================
    # The border layer has tiles around the perimeter — use those as walls.
    border_positions = tiled_map.get_layer_tile_positions("border")
    if border_positions:
        for col, row in border_positions:
            wall_rect = pygame.Rect(col * TILE, row * TILE, TILE, TILE)
            room.walls.append(wall_rect)
    else:
        # Fallback: simple perimeter walls
        room.build_walls_border()

    # === Interactable Objects from TMX layers ================================

    # Desk — layer "desk" — Caesar cipher puzzle
    desk_rect = tiled_map.get_layer_bounding_rect("desk")
    if desk_rect:
        desk = Interactable(
            rect=desk_rect,
            label="Desk",
            puzzle_id="caesar_cipher",
            color=(139, 90, 43),
        )
        room.interactables.append(desk)
        room.walls.append(desk_rect)

    # Lightboard/Switchboard — layer "lightboard" — Binary lock puzzle
    lb_rect = tiled_map.get_layer_bounding_rect("lightboard")
    if lb_rect:
        panel = Interactable(
            rect=lb_rect,
            label="Switchboard",
            puzzle_id="binary_lock",
            color=(60, 60, 90),
        )
        room.interactables.append(panel)
        room.walls.append(lb_rect)

    # Couch — layer "couch" — String slicing puzzle
    couch_rect = tiled_map.get_layer_bounding_rect("couch")
    if couch_rect:
        couch = Interactable(
            rect=couch_rect,
            label="Couch",
            puzzle_id="couch_slicing",
            color=(120, 80, 80),
        )
        room.interactables.append(couch)
        room.walls.append(couch_rect)

    # Escape door — layer "escapedoor"
    door_rect = tiled_map.get_layer_bounding_rect("escapedoor")
    if door_rect:
        door = Interactable(
            rect=door_rect,
            label="Door 🔒",
            puzzle_id=None,
            color=(100, 60, 40),
        )
        room.interactables.append(door)
        # Don't add the door as a wall — the player needs to walk to it

    # === Additional collision rects from furniture layers ====================
    # These are non-interactable objects the player should not walk through
    furniture_layers = [
        "coffeetable", "drawer", "anotherplant", "box1", "box2", "box3",
        "talllamp", "globe", "lamp",
    ]
    for layer_name in furniture_layers:
        rect = tiled_map.get_layer_bounding_rect(layer_name)
        if rect:
            room.walls.append(rect)

    # === Player start position ==============================================
    # Place the player in an open floor area (around tile 7, 12 — center-ish)
    start_x = 7 * TILE - 14
    start_y = 12 * TILE - 20

    return room, (start_x, start_y)


def build_level2_room_from_tmx():
    """Build the Level 2 escape room from HallwayLevel2.tmx."""
    if not os.path.exists(LEVEL2_TMX_PATH):
        print("[Room] Level 2 TMX file not found.")
        # Fallback to empty room
        return Room(15, 20), (100, 100)

    print("[Room] Loading Level 2 TMX map...")
    tiled_map = load_tmx(LEVEL2_TMX_PATH)
    room = Room(tiled_map.width, tiled_map.height)
    room.tmx_surface = tiled_map.render()

    # Border walls
    border_positions = tiled_map.get_layer_tile_positions("border")
    if border_positions:
        for col, row in border_positions:
            room.walls.append(pygame.Rect(col * TILE, row * TILE, TILE, TILE))
    else:
        room.build_walls_border()

    # Door 2 — Blinking lights puzzle
    door2_rect = tiled_map.get_layer_bounding_rect("door2")
    if door2_rect:
        door2 = Interactable(
            rect=door2_rect,
            label="Door",
            puzzle_id="blinking_lights",
            color=(100, 100, 100)
        )
        room.interactables.append(door2)
        room.walls.append(door2_rect)

    # Bump — Misplaced tile puzzle
    bump_rect = tiled_map.get_layer_bounding_rect("bump")
    if bump_rect:
        bump = Interactable(
            rect=bump_rect,
            label="Loose Tile",
            puzzle_id="misplaced_tile",
            color=(80, 80, 80)
        )
        room.interactables.append(bump)
        # It's a floor tile, so maybe not a wall

    # Painting — Painting puzzle
    painting_rect = tiled_map.get_layer_bounding_rect("painting")
    if painting_rect:
        painting = Interactable(
            rect=painting_rect,
            label="Eerie Painting",
            puzzle_id="painting_code",
            color=(100, 50, 50)
        )
        room.interactables.append(painting)
        room.walls.append(painting_rect)

    # Gate — initially blocks path
    gate_rect = tiled_map.get_layer_bounding_rect("gate")
    if gate_rect:
        gate = Interactable(
            rect=gate_rect,
            label="Closed Gate",
            puzzle_id=None,
            color=(60, 60, 60)
        )
        # Note: We'll identify it by label in room_state to hide/show it
        room.interactables.append(gate)
        room.walls.append(gate_rect)

    # Elevator — exit
    elevator_rect = tiled_map.get_layer_bounding_rect("elevator")
    if elevator_rect:
        elevator = Interactable(
            rect=elevator_rect,
            label="Elevator 🔒",
            puzzle_id=None,
            color=(80, 80, 90)
        )
        room.interactables.append(elevator)
        # Don't wall the front of the elevator so player can interact easily? 
        # But maybe still wall the exact rect so player doesn't wander in.
        # Actually in level 1 door was not a wall.

    # Light positions for blinking animation
    light_layer_names = ["mediumlamplight", "mediumlamplight2", "mediumlamplight3"]
    for ln in light_layer_names:
        rect = tiled_map.get_layer_bounding_rect(ln)
        if rect:
            room.light_positions.append(rect)

    # Player start position (easyleveldoor)
    start_pos = (150, 150)
    start_rect = tiled_map.get_layer_bounding_rect("easyleveldoor")
    if start_rect:
        start_pos = (start_rect.centerx - 14, start_rect.centery - 20)

    return room, start_pos

