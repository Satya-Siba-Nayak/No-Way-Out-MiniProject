"""
Menu State — Title screen with animated GIF background, music, name input,
and New Game / Continue buttons.

Preserves the look & feel of the original main.py login screen.
"""

import sys
import pygame
from PIL import Image
from states.base_state import State
from engine.save_system import has_save, load_game, delete_save


def load_gif_frames(path, target_size):
    """Load an animated GIF and return a list of scaled pygame surfaces."""
    gif = Image.open(path)
    frames = []
    try:
        while True:
            frame_rgba = gif.convert("RGBA")
            raw = frame_rgba.tobytes()
            surf = pygame.image.fromstring(raw, frame_rgba.size, "RGBA")
            scaled = pygame.transform.scale(surf, target_size)
            frames.append(scaled)
            gif.seek(gif.tell() + 1)
    except EOFError:
        pass
    return frames


class MenuState(State):
    """Title screen — GIF bg, player name input, New/Continue selection."""

    GIF_PATH = "parallax-mountain-animX1.gif"
    MUSIC_PATH = "Sunstone_Meadow.mp3"

    def __init__(self, machine, ctx):
        super().__init__(machine, ctx)
        self.player_name = ""
        self.gif_frames = []
        self.current_frame = 0
        self.frame_counter = 0
        self.frame_delay = 5
        self.is_muted = False

        # UI state
        self.phase = "name_input"   # "name_input" → "menu_select"
        self.menu_items = []
        self.selected_idx = 0

        # Fonts
        self.title_font = pygame.font.SysFont("Arial", 42, bold=True)
        self.font = pygame.font.SysFont("Arial", 28)
        self.small_font = pygame.font.SysFont("Arial", 18)

        # Colors
        self.WHITE = (255, 255, 255)
        self.GRAY = (200, 200, 200)
        self.GOLD = (255, 215, 0)
        self.RED = (255, 100, 100)

        # Mute button
        w = self.ctx["screen_w"]
        self.mute_rect = pygame.Rect(w - 50, 10, 40, 40)

    def enter(self):
        # Load GIF
        w, h = self.ctx["screen_w"], self.ctx["screen_h"]
        try:
            self.gif_frames = load_gif_frames(self.GIF_PATH, (w, h))
        except FileNotFoundError:
            self.gif_frames = []

        # Load and play music
        try:
            pygame.mixer.music.load(self.MUSIC_PATH)
            pygame.mixer.music.play(-1)
            self.is_muted = False
        except Exception:
            self.is_muted = True

    # --- Events -------------------------------------------------------------

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Mute toggle
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.mute_rect.collidepoint(event.pos):
                    self._toggle_mute()

            if event.type == pygame.KEYDOWN:
                if self.phase == "name_input":
                    self._handle_name_input(event)
                elif self.phase == "menu_select":
                    self._handle_menu_select(event)

    def _toggle_mute(self):
        self.is_muted = not self.is_muted
        if self.is_muted:
            pygame.mixer.music.pause()
        else:
            pygame.mixer.music.unpause()

    def _handle_name_input(self, event):
        if event.key == pygame.K_RETURN and self.player_name.strip():
            # Move to menu selection
            self.phase = "menu_select"
            self._build_menu()
        elif event.key == pygame.K_BACKSPACE:
            self.player_name = self.player_name[:-1]
        elif len(self.player_name) < 15 and event.unicode.isprintable():
            self.player_name += event.unicode

    def _build_menu(self):
        self.menu_items = ["New Game"]
        if has_save():
            self.menu_items.append("Continue")
        self.selected_idx = 0

    def _handle_menu_select(self, event):
        if event.key in (pygame.K_UP, pygame.K_w):
            self.selected_idx = (self.selected_idx - 1) % len(self.menu_items)
        elif event.key in (pygame.K_DOWN, pygame.K_s):
            self.selected_idx = (self.selected_idx + 1) % len(self.menu_items)
        elif event.key == pygame.K_RETURN:
            choice = self.menu_items[self.selected_idx]
            if choice == "New Game":
                delete_save()
                self.ctx["player_name"] = self.player_name.strip()
                self.ctx["load_save"] = False
                self._start_game()
            elif choice == "Continue":
                save_data = load_game()
                self.ctx["player_name"] = save_data.get("player_name",
                                                         self.player_name.strip())
                self.ctx["load_save"] = True
                self.ctx["save_data"] = save_data
                self._start_game()
        elif event.key == pygame.K_BACKSPACE:
            # go back to name input
            self.phase = "name_input"

    def _start_game(self):
        # Import here to avoid circular imports
        from states.room_state import RoomState
        self.machine.change(RoomState(self.machine, self.ctx))

    # --- Update -------------------------------------------------------------

    def update(self, dt):
        # Animate GIF
        if self.gif_frames:
            self.frame_counter += 1
            if self.frame_counter >= self.frame_delay:
                self.current_frame = ((self.current_frame + 1)
                                      % len(self.gif_frames))
                self.frame_counter = 0

    # --- Draw ---------------------------------------------------------------

    def draw(self, surface):
        w = self.ctx["screen_w"]
        h = self.ctx["screen_h"]

        # GIF background
        if self.gif_frames:
            surface.blit(self.gif_frames[self.current_frame], (0, 0))
        else:
            surface.fill((0, 0, 0))

        # Dark overlay
        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        surface.blit(overlay, (0, 0))

        # Mute icon
        self._draw_mute(surface)

        # Title
        title = self.title_font.render("NO WAY OUT?", True, self.WHITE)
        surface.blit(title, title.get_rect(center=(w // 2, int(h * 0.15))))

        if self.phase == "name_input":
            self._draw_name_input(surface, w, h)
        elif self.phase == "menu_select":
            self._draw_menu_select(surface, w, h)

    def _draw_name_input(self, surface, w, h):
        prompt = self.font.render("Enter Player Name:", True, self.WHITE)
        surface.blit(prompt, prompt.get_rect(center=(w // 2, int(h * 0.40))))

        # Input box
        box = pygame.Rect(w // 2 - 150, int(h * 0.48), 300, 45)
        pygame.draw.rect(surface, self.WHITE, box, 2)

        cursor = "|" if (pygame.time.get_ticks() // 500) % 2 == 0 else ""
        name_surf = self.font.render(self.player_name + cursor, True, self.WHITE)
        surface.blit(name_surf, name_surf.get_rect(center=box.center))

        foot = self.small_font.render("Press ENTER to continue", True, self.GRAY)
        surface.blit(foot, foot.get_rect(center=(w // 2, int(h * 0.85))))

    def _draw_menu_select(self, surface, w, h):
        welcome = self.font.render(f"Welcome, {self.player_name.strip()}!",
                                   True, self.GOLD)
        surface.blit(welcome, welcome.get_rect(center=(w // 2, int(h * 0.35))))

        for i, item in enumerate(self.menu_items):
            color = self.GOLD if i == self.selected_idx else self.WHITE
            prefix = "▶ " if i == self.selected_idx else "  "
            txt = self.font.render(prefix + item, True, color)
            y = int(h * 0.50) + i * 45
            surface.blit(txt, txt.get_rect(center=(w // 2, y)))

        hint = self.small_font.render("↑↓ to select, ENTER to confirm, BACKSPACE to go back",
                                      True, self.GRAY)
        surface.blit(hint, hint.get_rect(center=(w // 2, int(h * 0.85))))

    def _draw_mute(self, surface):
        color = self.GRAY if self.is_muted else self.WHITE
        pygame.draw.rect(surface, color, self.mute_rect, 2)
        icon_c = self.RED if self.is_muted else self.WHITE
        bx, by = self.mute_rect.x, self.mute_rect.y
        pygame.draw.polygon(surface, icon_c, [
            (bx + 10, by + 15), (bx + 18, by + 15),
            (bx + 25, by + 10), (bx + 25, by + 30),
            (bx + 18, by + 25), (bx + 10, by + 25),
        ])
        if self.is_muted:
            pygame.draw.line(surface, self.RED,
                             (bx + 10, by + 10), (bx + 30, by + 30), 3)
            pygame.draw.line(surface, self.RED,
                             (bx + 30, by + 10), (bx + 10, by + 30), 3)
