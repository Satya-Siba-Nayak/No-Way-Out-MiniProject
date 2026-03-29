"""
TMX Loader — custom parser for Tiled .tmx / .tsx map files.

Loads tile layers from the TMX, resolves each tileset's image source,
slices the source images into individual tile surfaces, and pre-renders
the entire map to a single pygame Surface.

No external dependencies beyond pygame and the standard library.
"""

import os
import xml.etree.ElementTree as ET
import pygame


# TMX flip-flag bitmasks (high bits of the global tile ID)
FLIPPED_HORIZONTALLY_FLAG = 0x80000000
FLIPPED_VERTICALLY_FLAG   = 0x40000000
FLIPPED_DIAGONALLY_FLAG   = 0x20000000
ALL_FLIP_FLAGS            = (FLIPPED_HORIZONTALLY_FLAG |
                             FLIPPED_VERTICALLY_FLAG |
                             FLIPPED_DIAGONALLY_FLAG)


class TilesetInfo:
    """Stores metadata and tile surfaces for a single tileset."""

    def __init__(self, firstgid, name, tile_width, tile_height,
                 columns, tile_count, image_path):
        self.firstgid = firstgid
        self.name = name
        self.tile_width = tile_width
        self.tile_height = tile_height
        self.columns = columns
        self.tile_count = tile_count
        self.image_path = image_path   # absolute path to the source PNG
        self.tiles = {}                # local_id -> pygame.Surface

    def load_tiles(self):
        """Slice the source image into individual tile surfaces."""
        if not os.path.exists(self.image_path):
            print(f"[TMX] WARNING: tileset image not found: {self.image_path}")
            return

        try:
            sheet = pygame.image.load(self.image_path).convert_alpha()
        except pygame.error as e:
            print(f"[TMX] WARNING: failed to load {self.image_path}: {e}")
            return

        if self.columns <= 0:
            return

        for local_id in range(self.tile_count):
            col = local_id % self.columns
            row = local_id // self.columns
            x = col * self.tile_width
            y = row * self.tile_height

            # Clamp to image bounds
            tw = min(self.tile_width, sheet.get_width() - x)
            th = min(self.tile_height, sheet.get_height() - y)
            if tw <= 0 or th <= 0:
                continue

            tile_surf = sheet.subsurface(pygame.Rect(x, y, tw, th))
            self.tiles[local_id] = tile_surf

    def get_tile(self, global_id):
        """
        Given a global tile ID (with flip flags already stripped),
        return the tile surface or None.
        """
        local_id = global_id - self.firstgid
        return self.tiles.get(local_id)


class TileLayer:
    """A single tile layer from the TMX map."""

    def __init__(self, name, width, height, data):
        self.name = name
        self.width = width
        self.height = height
        self.data = data   # list of global tile IDs (length = width * height)


class TiledMap:
    """Represents a fully parsed TMX map."""

    def __init__(self):
        self.width = 0          # in tiles
        self.height = 0         # in tiles
        self.tile_width = 32    # map-level tile size (grid)
        self.tile_height = 32
        self.tilesets = []      # list of TilesetInfo, sorted by firstgid
        self.layers = []        # list of TileLayer (in render order)
        self.object_groups = [] # list of (name, [objects]) — for future use

    @property
    def pixel_width(self):
        return self.width * self.tile_width

    @property
    def pixel_height(self):
        return self.height * self.tile_height

    def get_tileset_for_gid(self, gid):
        """Find the tileset that owns a given global tile ID."""
        result = None
        for ts in self.tilesets:
            if ts.firstgid <= gid:
                result = ts
            else:
                break
        return result

    def render(self):
        """
        Pre-render the entire map to a single pygame Surface.
        Returns a Surface of size (pixel_width × pixel_height).
        """
        surf = pygame.Surface((self.pixel_width, self.pixel_height),
                              pygame.SRCALPHA)
        surf.fill((0, 0, 0, 0))

        for layer in self.layers:
            self._render_layer(surf, layer)

        return surf

    def _render_layer(self, surface, layer):
        """Render one tile layer onto the given surface."""
        for idx, raw_gid in enumerate(layer.data):
            if raw_gid == 0:
                continue

            # Extract flip flags
            h_flip = bool(raw_gid & FLIPPED_HORIZONTALLY_FLAG)
            v_flip = bool(raw_gid & FLIPPED_VERTICALLY_FLAG)
            d_flip = bool(raw_gid & FLIPPED_DIAGONALLY_FLAG)

            gid = raw_gid & ~ALL_FLIP_FLAGS

            ts = self.get_tileset_for_gid(gid)
            if ts is None:
                continue

            tile_surf = ts.get_tile(gid)
            if tile_surf is None:
                continue

            # Apply flip transforms
            if d_flip or h_flip or v_flip:
                tile_surf = self._apply_flips(tile_surf, h_flip, v_flip, d_flip)

            # Calculate the destination position on the map grid.
            # The tile is placed so its bottom-left aligns with the grid cell,
            # which means oversized tiles extend upward / to the right.
            col = idx % layer.width
            row = idx // layer.width

            dest_x = col * self.tile_width
            # For tiles taller than the grid cell, shift upward
            dest_y = (row + 1) * self.tile_height - tile_surf.get_height()

            surface.blit(tile_surf, (dest_x, dest_y))

    @staticmethod
    def _apply_flips(surf, h_flip, v_flip, d_flip):
        """Apply TMX flip/rotation transforms to a tile surface."""
        result = surf
        if d_flip:
            # Diagonal flip = rotate 90° CW then flip horizontally
            result = pygame.transform.rotate(result, -90)
            result = pygame.transform.flip(result, True, False)
        if h_flip:
            result = pygame.transform.flip(result, True, False)
        if v_flip:
            result = pygame.transform.flip(result, False, True)
        return result

    def get_layer_tile_positions(self, layer_name):
        """
        Return a list of (col, row) for every non-zero tile in the named layer.
        Useful for building collision/interaction rects.
        """
        for layer in self.layers:
            if layer.name == layer_name:
                positions = []
                for idx, gid in enumerate(layer.data):
                    if (gid & ~ALL_FLIP_FLAGS) != 0:
                        col = idx % layer.width
                        row = idx // layer.width
                        positions.append((col, row))
                return positions
        return []

    def get_layer_bounding_rect(self, layer_name):
        """
        Get the bounding rectangle (in pixels) of all non-zero tiles in a layer.
        Returns a pygame.Rect or None if the layer is empty / not found.
        """
        positions = self.get_layer_tile_positions(layer_name)
        if not positions:
            return None

        min_col = min(p[0] for p in positions)
        max_col = max(p[0] for p in positions)
        min_row = min(p[1] for p in positions)
        max_row = max(p[1] for p in positions)

        x = min_col * self.tile_width
        y = min_row * self.tile_height
        w = (max_col - min_col + 1) * self.tile_width
        h = (max_row - min_row + 1) * self.tile_height
        return pygame.Rect(x, y, w, h)


def _parse_tsx(tsx_path, firstgid):
    """
    Parse a .tsx tileset file and return a TilesetInfo.
    """
    tree = ET.parse(tsx_path)
    root = tree.getroot()

    name = root.get("name", "")
    tile_width = int(root.get("tilewidth", 32))
    tile_height = int(root.get("tileheight", 32))
    tile_count = int(root.get("tilecount", 0))
    columns = int(root.get("columns", 0))

    # Find the <image> element
    image_el = root.find("image")
    if image_el is not None:
        img_source = image_el.get("source", "")
        # Resolve relative path from the TSX file's directory
        tsx_dir = os.path.dirname(tsx_path)
        image_path = os.path.normpath(os.path.join(tsx_dir, img_source))
    else:
        image_path = ""

    return TilesetInfo(
        firstgid=firstgid,
        name=name,
        tile_width=tile_width,
        tile_height=tile_height,
        columns=columns,
        tile_count=tile_count,
        image_path=image_path,
    )


def load_tmx(tmx_path):
    """
    Parse a .tmx file and return a fully loaded TiledMap.

    Args:
        tmx_path: Absolute or relative path to the .tmx file.

    Returns:
        A TiledMap with all tilesets loaded and tile surfaces sliced.
    """
    tmx_path = os.path.abspath(tmx_path)
    tmx_dir = os.path.dirname(tmx_path)

    tree = ET.parse(tmx_path)
    root = tree.getroot()

    tmap = TiledMap()
    tmap.width = int(root.get("width", 0))
    tmap.height = int(root.get("height", 0))
    tmap.tile_width = int(root.get("tilewidth", 32))
    tmap.tile_height = int(root.get("tileheight", 32))

    # --- Parse tilesets -------------------------------------------------------
    seen_firstgids = set()
    for ts_el in root.findall("tileset"):
        firstgid = int(ts_el.get("firstgid", 1))

        # Skip duplicate firstgid entries (the TMX has two with firstgid=10765)
        if firstgid in seen_firstgids:
            continue
        seen_firstgids.add(firstgid)

        source = ts_el.get("source")
        if source:
            # External TSX file
            tsx_path = os.path.normpath(os.path.join(tmx_dir, source))
            if os.path.exists(tsx_path):
                ts_info = _parse_tsx(tsx_path, firstgid)
                tmap.tilesets.append(ts_info)
            else:
                print(f"[TMX] WARNING: TSX file not found: {tsx_path}")
        else:
            # Embedded tileset (inline in the TMX)
            name = ts_el.get("name", "")
            tw = int(ts_el.get("tilewidth", 32))
            th = int(ts_el.get("tileheight", 32))
            tc = int(ts_el.get("tilecount", 0))
            cols = int(ts_el.get("columns", 0))
            image_el = ts_el.find("image")
            img_path = ""
            if image_el is not None:
                img_source = image_el.get("source", "")
                img_path = os.path.normpath(os.path.join(tmx_dir, img_source))
            ts_info = TilesetInfo(firstgid, name, tw, th, cols, tc, img_path)
            tmap.tilesets.append(ts_info)

    # Sort tilesets by firstgid (important for GID lookup)
    tmap.tilesets.sort(key=lambda ts: ts.firstgid)

    # Load all tile images
    for ts in tmap.tilesets:
        ts.load_tiles()

    # --- Parse tile layers ----------------------------------------------------
    for layer_el in root.findall("layer"):
        name = layer_el.get("name", "")
        width = int(layer_el.get("width", tmap.width))
        height = int(layer_el.get("height", tmap.height))

        data_el = layer_el.find("data")
        if data_el is None:
            continue

        encoding = data_el.get("encoding", "")
        if encoding != "csv":
            print(f"[TMX] WARNING: unsupported encoding '{encoding}' "
                  f"in layer '{name}', skipping")
            continue

        # Parse CSV tile data
        csv_text = data_el.text.strip()
        tile_ids = []
        for val in csv_text.replace("\r", "").replace("\n", "").split(","):
            val = val.strip()
            if val:
                tile_ids.append(int(val))

        tmap.layers.append(TileLayer(name, width, height, tile_ids))

    # --- Parse object groups (names only, for interactable mapping) -----------
    for og_el in root.findall("objectgroup"):
        name = og_el.get("name", "")
        tmap.object_groups.append(name)

    return tmap
