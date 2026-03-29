"""
Menu State — Title screen with animated GIF background, music, name input,
character selection, settings overlay, and New Game / Continue buttons.

Flow:
  1. name_input  — enter player name
  2. menu_select — New Game / Continue
  3. char_select — pick Finn or Maeve  (only for New Game)
  Then → RoomState
"""

import sys
import pygame
from PIL import Image
from states.base_state import State
from engine.save_system import has_save, load_game, delete_save
from engine.player import load_pfp, SPRITE_CHARS
from engine.settings import load_settings, save_settings


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
    """Title screen — GIF bg, player name input, character select, settings."""

    GIF_PATH = "parallax-mountain-animX1.gif"
    MUSIC_PATH = "Sunstone_Meadow.mp3"

    def __init__(self, machine, ctx):
        super().__init__(machine, ctx)
        self.player_name = ""
        self.gif_frames = []
        self.current_frame = 0
        self.frame_counter = 0
        self.frame_delay = 5

        # Settings
        s = load_settings()
        self.volume = s.get("volume", 0.20)
        self.muted = s.get("muted", False)
        self.dragging_slider = False

        # UI state
        self.phase = "name_input"   # "name_input", "menu_select", "char_select", "settings"
        self.prev_phase = "name_input"
        self.menu_items = []
        self.selected_idx = 0

        # Character selection
        self.char_options = ["finn", "maeve"]
        self.char_idx = 0
        self.pfp_images = {}    # sprite_id -> scaled Surface

        # Fonts
        self.title_font = pygame.font.SysFont("Arial", 42, bold=True)
        self.font = pygame.font.SysFont("Arial", 28)
        self.small_font = pygame.font.SysFont("Arial", 18)
        self.char_name_font = pygame.font.SysFont("Arial", 24, bold=True)

        # Colors
        self.WHITE = (255, 255, 255)
        self.GRAY = (200, 200, 200)
        self.DARK_GRAY = (120, 120, 120)
        self.GOLD = (255, 215, 0)
        self.RED = (255, 100, 100)
        self.ACCENT = (130, 180, 255)    # light blue accent

    def enter(self):
        # Load GIF
        w, h = self.ctx["screen_w"], self.ctx["screen_h"]
        try:
            self.gif_frames = load_gif_frames(self.GIF_PATH, (w, h))
        except FileNotFoundError:
            self.gif_frames = []

        # Load and play music
        self._apply_volume()
        try:
            pygame.mixer.music.load(self.MUSIC_PATH)
            pygame.mixer.music.play(-1)
        except Exception:
            pass

        # Pre-load character PFP images for the selection screen
        for cid in self.char_options:
            pfp = load_pfp(cid, size=(120, 120))
            if pfp:
                self.pfp_images[cid] = pfp

    def _apply_volume(self):
        try:
            pygame.mixer.music.set_volume(0.0 if self.muted else self.volume)
        except Exception:
            pass

    # --- Events -------------------------------------------------------------

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Mouse events
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.phase == "settings":
                    if self._slider_rect().collidepoint(event.pos) or \
                       self._slider_track_rect().collidepoint(event.pos):
                        self.dragging_slider = True
                        self._update_volume_from_mouse(event.pos[0])
                    elif self._mute_rect().collidepoint(event.pos):
                        self.muted = not self.muted
                        self._apply_volume()
                        save_settings({"volume": self.volume, "muted": self.muted})
                    elif self._back_btn_rect().collidepoint(event.pos):
                        self.phase = self.prev_phase
                else:
                    if self._settings_icon_rect().collidepoint(event.pos):
                        self.prev_phase = self.phase
                        self.phase = "settings"

            if event.type == pygame.MOUSEBUTTONUP:
                if self.dragging_slider:
                    self.dragging_slider = False
                    save_settings({"volume": self.volume, "muted": self.muted})

            if event.type == pygame.MOUSEMOTION and self.dragging_slider:
                self._update_volume_from_mouse(event.pos[0])

            if event.type == pygame.KEYDOWN:
                if self.phase == "settings":
                    if event.key == pygame.K_ESCAPE or event.key == pygame.K_BACKSPACE:
                        self.phase = self.prev_phase
                elif self.phase == "name_input":
                    self._handle_name_input(event)
                elif self.phase == "menu_select":
                    self._handle_menu_select(event)
                elif self.phase == "char_select":
                    self._handle_char_select(event)

    # --- Click Areas --------------------------------------------------------

    def _settings_icon_rect(self):
        w = self.ctx["screen_w"]
        # Top right corner
        return pygame.Rect(w - 50, 10, 40, 40)

    def _slider_track_rect(self):
        w, h = self.ctx["screen_w"], self.ctx["screen_h"]
        track_w = 240
        track_x = (w - track_w) // 2
        track_y = h // 2 - 20
        return pygame.Rect(track_x, track_y, track_w, 20)

    def _slider_rect(self):
        track = self._slider_track_rect()
        knob_x = track.x + int(self.volume * track.width) - 10
        return pygame.Rect(knob_x, track.y - 5, 20, 30)

    def _mute_rect(self):
        w, h = self.ctx["screen_w"], self.ctx["screen_h"]
        box_w = 120
        box_x = (w - box_w) // 2
        box_y = h // 2 + 40
        return pygame.Rect(box_x, box_y, box_w, 40)

    def _back_btn_rect(self):
        w, h = self.ctx["screen_w"], self.ctx["screen_h"]
        box_w = 100
        box_x = (w - box_w) // 2
        box_y = h // 2 + 120
        return pygame.Rect(box_x, box_y, box_w, 40)

    def _update_volume_from_mouse(self, mouse_x):
        track = self._slider_track_rect()
        rel = (mouse_x - track.x) / track.width
        self.volume = max(0.0, min(1.0, rel))
        self._apply_volume()

    # --- Phase handlers -------------------------------------------------------

    def _handle_name_input(self, event):
        if event.key == pygame.K_RETURN and self.player_name.strip():
            self.phase = "menu_select"
            self._build_menu()
        elif event.key == pygame.K_BACKSPACE:
            self.player_name = self.player_name[:-1]
        elif len(self.player_name) < 15 and event.unicode.isprintable():
            self.player_name += event.unicode
        elif event.key == pygame.K_ESCAPE:
            pygame.quit()
            sys.exit()

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
                self.phase = "char_select"
                self.char_idx = 0
            elif choice == "Continue":
                save_data = load_game()
                self.ctx["player_name"] = save_data.get("player_name", self.player_name.strip())
                self.ctx["load_save"] = True
                self.ctx["save_data"] = save_data
                self.ctx["sprite_id"] = save_data.get("sprite_id", "finn")
                self._start_game()
        elif event.key == pygame.K_BACKSPACE or event.key == pygame.K_ESCAPE:
            self.phase = "name_input"

    def _handle_char_select(self, event):
        if event.key in (pygame.K_LEFT, pygame.K_a):
            self.char_idx = (self.char_idx - 1) % len(self.char_options)
        elif event.key in (pygame.K_RIGHT, pygame.K_d):
            self.char_idx = (self.char_idx + 1) % len(self.char_options)
        elif event.key == pygame.K_RETURN:
            chosen = self.char_options[self.char_idx]
            self.ctx["sprite_id"] = chosen
            self._start_game()
        elif event.key == pygame.K_BACKSPACE or event.key == pygame.K_ESCAPE:
            self.phase = "menu_select"
            self._build_menu()

    def _start_game(self):
        from states.room_state import RoomState
        self.machine.change(RoomState(self.machine, self.ctx))

    # --- Update -------------------------------------------------------------

    def update(self, dt):
        if self.gif_frames:
            self.frame_counter += 1
            if self.frame_counter >= self.frame_delay:
                self.current_frame = ((self.current_frame + 1) % len(self.gif_frames))
                self.frame_counter = 0

    # --- Draw ---------------------------------------------------------------

    def draw(self, surface):
        w = self.ctx["screen_w"]
        h = self.ctx["screen_h"]

        # GIF background or fallback
        if self.gif_frames:
            surface.blit(self.gif_frames[self.current_frame], (0, 0))
        else:
            surface.fill((0, 0, 0))

        # Dark overlay
        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        if self.phase == "settings":
            # Darker overlay for settings
            overlay.fill((0, 0, 0, 200))

        surface.blit(overlay, (0, 0))

        if self.phase == "settings":
            self._draw_settings(surface, w, h)
        else:
            # Settings Icon (always visible outside settings)
            self._draw_settings_icon(surface)

            # Title
            title = self.title_font.render("NO WAY OUT?", True, self.WHITE)
            surface.blit(title, title.get_rect(center=(w // 2, int(h * 0.15))))

            if self.phase == "name_input":
                self._draw_name_input(surface, w, h)
            elif self.phase == "menu_select":
                self._draw_menu_select(surface, w, h)
            elif self.phase == "char_select":
                self._draw_char_select(surface, w, h)

    def _draw_settings_icon(self, surface):
        rect = self._settings_icon_rect()
        pygame.draw.rect(surface, (60, 60, 70), rect, border_radius=5)
        pygame.draw.rect(surface, self.GRAY, rect, 2, border_radius=5)
        # Just use a gear character
        # Add special fallback for windows console / pygame rendering just in case
        gear = self.font.render("⚙", True, self.WHITE)
        surface.blit(gear, gear.get_rect(center=rect.center))

    def _draw_settings(self, surface, w, h):
        title = self.title_font.render("SETTINGS", True, self.GOLD)
        surface.blit(title, title.get_rect(center=(w // 2, int(h * 0.2))))

        # 1. Volume Slider
        track = self._slider_track_rect()
        vol_pct = int(self.volume * 100)
        label = self.font.render(f"Music Volume: {vol_pct}%", True, self.WHITE)
        surface.blit(label, label.get_rect(midbottom=(track.centerx, track.top - 15)))

        pygame.draw.rect(surface, (60, 60, 70), track, border_radius=5)
        filled_w = int(self.volume * track.width)
        if filled_w > 0:
            filled = pygame.Rect(track.x, track.y, filled_w, track.height)
            pygame.draw.rect(surface, self.ACCENT, filled, border_radius=5)
        pygame.draw.rect(surface, self.GRAY, track, 2, border_radius=5)

        knob = self._slider_rect()
        pygame.draw.rect(surface, self.WHITE, knob, border_radius=5)
        pygame.draw.rect(surface, self.DARK_GRAY, knob, 2, border_radius=5)

        # 2. Mute Toggle
        mute_btn = self._mute_rect()
        pygame.draw.rect(surface, (60, 60, 70), mute_btn, border_radius=5)
        if self.muted:
            pygame.draw.rect(surface, self.RED, mute_btn, 2, border_radius=5)
        else:
            pygame.draw.rect(surface, self.GRAY, mute_btn, 2, border_radius=5)

        mute_txt = "Muted: ON" if self.muted else "Muted: OFF"
        mute_color = self.RED if self.muted else self.WHITE
        txt = self.small_font.render(mute_txt, True, mute_color)
        surface.blit(txt, txt.get_rect(center=mute_btn.center))

        # 3. Back Button
        back_btn = self._back_btn_rect()
        pygame.draw.rect(surface, (60, 60, 70), back_btn, border_radius=5)
        pygame.draw.rect(surface, self.GRAY, back_btn, 2, border_radius=5)
        back_txt = self.small_font.render("Back", True, self.WHITE)
        surface.blit(back_txt, back_txt.get_rect(center=back_btn.center))

    def _draw_name_input(self, surface, w, h):
        prompt = self.font.render("Enter Player Name:", True, self.WHITE)
        surface.blit(prompt, prompt.get_rect(center=(w // 2, int(h * 0.40))))

        # Input box
        box = pygame.Rect(w // 2 - 150, int(h * 0.48), 300, 45)
        pygame.draw.rect(surface, (40, 40, 40), box)
        pygame.draw.rect(surface, self.WHITE, box, 2)

        cursor = "|" if (pygame.time.get_ticks() // 500) % 2 == 0 else ""
        name_surf = self.font.render(self.player_name + cursor, True, self.WHITE)
        surface.blit(name_surf, name_surf.get_rect(center=box.center))

        foot = self.small_font.render("Press ENTER to continue", True, self.GRAY)
        surface.blit(foot, foot.get_rect(center=(w // 2, int(h * 0.85))))

    def _draw_menu_select(self, surface, w, h):
        welcome = self.font.render(f"Welcome, {self.player_name.strip()}!", True, self.GOLD)
        surface.blit(welcome, welcome.get_rect(center=(w // 2, int(h * 0.35))))

        for i, item in enumerate(self.menu_items):
            color = self.GOLD if i == self.selected_idx else self.WHITE
            prefix = "▶ " if i == self.selected_idx else "  "
            txt = self.font.render(prefix + item, True, color)
            y = int(h * 0.50) + i * 45
            surface.blit(txt, txt.get_rect(center=(w // 2, y)))

        hint = self.small_font.render("↑↓ to select, ENTER to confirm, BACKSPACE to go back", True, self.GRAY)
        surface.blit(hint, hint.get_rect(center=(w // 2, int(h * 0.85))))

    def _draw_char_select(self, surface, w, h):
        header = self.font.render("Choose Your Character", True, self.GOLD)
        surface.blit(header, header.get_rect(center=(w // 2, int(h * 0.28))))

        card_w, card_h = 160, 200
        gap = 60
        total_w = len(self.char_options) * card_w + (len(self.char_options) - 1) * gap
        start_x = (w - total_w) // 2
        card_y = int(h * 0.35)

        for i, cid in enumerate(self.char_options):
            card_x = start_x + i * (card_w + gap)
            is_selected = (i == self.char_idx)
            config = SPRITE_CHARS.get(cid, {})
            char_name = config.get("name", cid.title())

            card_rect = pygame.Rect(card_x, card_y, card_w, card_h)
            card_surf = pygame.Surface((card_w, card_h), pygame.SRCALPHA)

            if is_selected:
                card_surf.fill((255, 215, 0, 50))
                border_color = self.GOLD
                border_width = 3
            else:
                card_surf.fill((40, 40, 50, 160))
                border_color = self.GRAY
                border_width = 1

            surface.blit(card_surf, card_rect.topleft)
            pygame.draw.rect(surface, border_color, card_rect, border_width, border_radius=8)

            pfp = self.pfp_images.get(cid)
            if pfp:
                pfp_rect = pfp.get_rect(centerx=card_rect.centerx, top=card_rect.top + 15)
                surface.blit(pfp, pfp_rect)
            else:
                pygame.draw.circle(surface, self.DARK_GRAY, (card_rect.centerx, card_rect.top + 75), 50)
                q = self.small_font.render("?", True, self.WHITE)
                surface.blit(q, q.get_rect(center=(card_rect.centerx, card_rect.top + 75)))

            name_color = self.GOLD if is_selected else self.WHITE
            name_surf = self.char_name_font.render(char_name, True, name_color)
            surface.blit(name_surf, name_surf.get_rect(centerx=card_rect.centerx, top=card_rect.bottom - 35))

            if is_selected:
                arrow = self.font.render("▼", True, self.GOLD)
                surface.blit(arrow, arrow.get_rect(centerx=card_rect.centerx, bottom=card_rect.top - 5))

        hint = self.small_font.render("← → to select, ENTER to confirm, BACKSPACE to go back", True, self.GRAY)
        surface.blit(hint, hint.get_rect(center=(w // 2, int(h * 0.85))))
