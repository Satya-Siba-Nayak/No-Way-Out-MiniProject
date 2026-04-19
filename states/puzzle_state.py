"""
Puzzle State — overlay UI that lets the player solve a puzzle.

Renders as a dark overlay with a panel, the puzzle description, and a
text input field. Wraps Keya's puzzle classes from puzzles/easy_puzzles.py.

Features:
  - Puzzle image shown as a thumbnail below the text
  - Press [TAB] or click the thumbnail to enlarge the image full-screen
  - Press any key / click again to close the enlarged view
"""

import os
import sys
import pygame
from states.base_state import State
from puzzles.easy_puzzles import PUZZLE_REGISTRY


class PuzzleState(State):
    """Overlay that presents a puzzle for the player to solve."""

    def __init__(self, machine, ctx, puzzle_id, room_state):
        super().__init__(machine, ctx)
        self.puzzle_id = puzzle_id
        self.room_state = room_state    # callback reference
        self.puzzle = None
        self.puzzle_image = None
        self.puzzle_image_full = None   # larger version for zoomed view
        self.image_zoomed = False       # is the image currently enlarged?
        self.user_input = ""
        self.feedback = ""
        self.feedback_color = (255, 255, 255)
        self.feedback_timer = 0
        self.solved = False

        # Fonts
        self.title_font = pygame.font.SysFont("Arial", 30, bold=True)
        self.font = pygame.font.SysFont("Arial", 20)
        self.small_font = pygame.font.SysFont("Arial", 16)
        self.input_font = pygame.font.SysFont("Arial", 24)

        # Colors
        self.WHITE = (255, 255, 255)
        self.GOLD = (255, 215, 0)
        self.GREEN = (100, 255, 100)
        self.RED = (255, 100, 100)
        self.GRAY = (180, 180, 180)

    def enter(self):
        puzzle_cls = PUZZLE_REGISTRY.get(self.puzzle_id)
        if puzzle_cls:
            self.puzzle = puzzle_cls()
            if hasattr(self.puzzle, "image_path") and os.path.exists(self.puzzle.image_path):
                try:
                    raw = pygame.image.load(self.puzzle.image_path).convert_alpha()

                    # Create thumbnail (small version to fit in panel)
                    iw, ih = raw.get_size()
                    thumb_max = 160
                    scale = min(thumb_max / iw, thumb_max / ih)
                    self.puzzle_image = pygame.transform.smoothscale(
                        raw, (int(iw * scale), int(ih * scale)))

                    # Create full-size version for zoomed view
                    sw, sh = self.ctx["screen_w"], self.ctx["screen_h"]
                    full_max = min(sw - 80, sh - 80)
                    full_scale = min(full_max / iw, full_max / ih, 1.0)
                    self.puzzle_image_full = pygame.transform.smoothscale(
                        raw, (int(iw * full_scale), int(ih * full_scale)))

                except Exception as e:
                    print(f"[PuzzleState] Failed to load image {self.puzzle.image_path}: {e}")
        else:
            # Unknown puzzle — just pop back
            self.machine.pop()

    # --- Events -------------------------------------------------------------

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                # If image is zoomed, any key closes it
                if self.image_zoomed:
                    self.image_zoomed = False
                    return

                if self.solved:
                    # Any key closes after solving
                    self.machine.pop()
                    return

                if event.key == pygame.K_ESCAPE:
                    self.machine.pop()
                    return

                if event.key == pygame.K_TAB and self.puzzle_image:
                    # Toggle image zoom
                    self.image_zoomed = True
                    return

                if event.key == pygame.K_RETURN:
                    self._submit()
                elif event.key == pygame.K_BACKSPACE:
                    self.user_input = self.user_input[:-1]
                    self.feedback = ""
                elif event.unicode.isprintable() and len(self.user_input) < 30:
                    self.user_input += event.unicode
                    self.feedback = ""

            # Mouse click on thumbnail to enlarge
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.image_zoomed:
                    self.image_zoomed = False
                elif hasattr(self, '_thumb_rect') and self._thumb_rect and \
                     self._thumb_rect.collidepoint(event.pos):
                    self.image_zoomed = True

    def _submit(self):
        if not self.user_input.strip():
            return

        if self.puzzle.check_answer(self.user_input):
            self.solved = True
            self.feedback = "✓ Correct! Press any key to continue."
            self.feedback_color = self.GREEN
            self.room_state.on_puzzle_solved(self.puzzle_id)
        else:
            self.feedback = "✗ Wrong answer. Try again!"
            self.feedback_color = self.RED
            self.user_input = ""

    # --- Update -------------------------------------------------------------

    def update(self, dt):
        pass  # No ongoing logic needed

    # --- Draw ---------------------------------------------------------------

    def draw(self, surface):
        w = self.ctx["screen_w"]
        h = self.ctx["screen_h"]

        # Don't clear — the room is still visible underneath

        # Dark overlay
        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))

        if not self.puzzle:
            return

        # If image is zoomed in, draw it full screen and return
        if self.image_zoomed and self.puzzle_image_full:
            self._draw_zoomed_image(surface, w, h)
            return

        # Panel background
        panel_w, panel_h = 700, 420
        panel_x = (w - panel_w) // 2
        panel_y = (h - panel_h) // 2

        # Panel shadow
        shadow = pygame.Surface((panel_w + 4, panel_h + 4), pygame.SRCALPHA)
        shadow.fill((0, 0, 0, 100))
        surface.blit(shadow, (panel_x + 4, panel_y + 4))

        # Panel body
        panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        panel.fill((40, 38, 50, 240))
        pygame.draw.rect(panel, (100, 90, 120), (0, 0, panel_w, panel_h), 2)
        surface.blit(panel, (panel_x, panel_y))

        # Title bar
        title_bar = pygame.Rect(panel_x, panel_y, panel_w, 40)
        pygame.draw.rect(surface, (60, 55, 75), title_bar)
        title = self.title_font.render(self.puzzle.TITLE, True, self.GOLD)
        surface.blit(title, title.get_rect(center=title_bar.center))

        # --- Layout: text on left, thumbnail on right ---
        text_right_margin = panel_x + panel_w - 20
        thumb_w = 0

        # Draw thumbnail on the right side (if image exists)
        self._thumb_rect = None
        if self.puzzle_image:
            thumb_w = self.puzzle_image.get_width() + 20
            img_x = panel_x + panel_w - self.puzzle_image.get_width() - 15
            img_y = panel_y + 50
            # Draw a border around the thumbnail
            border_rect = pygame.Rect(
                img_x - 3, img_y - 3,
                self.puzzle_image.get_width() + 6,
                self.puzzle_image.get_height() + 6)
            pygame.draw.rect(surface, (100, 90, 120), border_rect, 2)
            surface.blit(self.puzzle_image, (img_x, img_y))
            self._thumb_rect = border_rect

            # "Click to enlarge" hint
            hint = self.small_font.render("TAB / Click to enlarge", True, self.GRAY)
            surface.blit(hint, hint.get_rect(
                centerx=img_x + self.puzzle_image.get_width() // 2,
                top=img_y + self.puzzle_image.get_height() + 5))

            text_right_margin = img_x - 10

        # Description text (wraps to avoid the thumbnail)
        y = panel_y + 55
        max_text_w = text_right_margin - (panel_x + 25)
        for line in self.puzzle.description:
            if line == "":
                y += 10
                continue
            # Word-wrap long lines
            words = line.split(' ')
            current_line = ""
            for word in words:
                test = current_line + (" " if current_line else "") + word
                test_surf = self.font.render(test, True, self.WHITE)
                if test_surf.get_width() > max_text_w and current_line:
                    txt = self.font.render(current_line, True, self.WHITE)
                    surface.blit(txt, (panel_x + 25, y))
                    y += 24
                    current_line = word
                else:
                    current_line = test
            if current_line:
                txt = self.font.render(current_line, True, self.WHITE)
                surface.blit(txt, (panel_x + 25, y))
                y += 24

        # Input area
        input_y = panel_y + panel_h - 100
        input_label = self.small_font.render("Your answer:", True, self.GRAY)
        surface.blit(input_label, (panel_x + 25, input_y - 20))

        input_box = pygame.Rect(panel_x + 25, input_y, panel_w - 50, 36)
        box_color = self.GREEN if self.solved else self.WHITE
        pygame.draw.rect(surface, box_color, input_box, 2)

        cursor = "|" if not self.solved and (pygame.time.get_ticks() // 500) % 2 == 0 else ""
        inp_surf = self.input_font.render(self.user_input + cursor, True, self.WHITE)
        surface.blit(inp_surf, (input_box.x + 8, input_box.y + 5))

        # Feedback
        if self.feedback:
            fb = self.font.render(self.feedback, True, self.feedback_color)
            surface.blit(fb, (panel_x + 25, input_y + 45))

        # Hint at bottom
        if not self.solved:
            hint = self.small_font.render("ENTER to submit | ESC to cancel",
                                          True, self.GRAY)
            surface.blit(hint, hint.get_rect(
                center=(w // 2, panel_y + panel_h - 12)))

    def _draw_zoomed_image(self, surface, w, h):
        """Draw the puzzle image enlarged, centered on screen."""
        # Darker overlay
        dark = pygame.Surface((w, h), pygame.SRCALPHA)
        dark.fill((0, 0, 0, 220))
        surface.blit(dark, (0, 0))

        img = self.puzzle_image_full
        ix = (w - img.get_width()) // 2
        iy = (h - img.get_height()) // 2

        # White border
        border = pygame.Rect(ix - 4, iy - 4, img.get_width() + 8, img.get_height() + 8)
        pygame.draw.rect(surface, self.WHITE, border, 3)

        surface.blit(img, (ix, iy))

        # Close hint
        hint = self.small_font.render("Press any key or click to close", True, self.GRAY)
        surface.blit(hint, hint.get_rect(center=(w // 2, iy + img.get_height() + 25)))
