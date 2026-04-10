"""
Puzzle State — overlay UI that lets the player solve a puzzle.

Renders as a dark overlay with a panel, the puzzle description, and a
text input field. Wraps Keya's puzzle classes from puzzles/easy_puzzles.py.
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
                    img = pygame.image.load(self.puzzle.image_path).convert_alpha()
                    # Scale down if needed to fit on the right side of the panel (e.g. 340x340 max)
                    iw, ih = img.get_size()
                    scale = min(340 / iw, 340 / ih)
                    img = pygame.transform.scale(img, (int(iw * scale), int(ih * scale)))
                    self.puzzle_image = img
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
                if self.solved:
                    # Any key closes after solving
                    self.machine.pop()
                    return

                if event.key == pygame.K_ESCAPE:
                    self.machine.pop()
                    return

                if event.key == pygame.K_RETURN:
                    self._submit()
                elif event.key == pygame.K_BACKSPACE:
                    self.user_input = self.user_input[:-1]
                    self.feedback = ""
                elif event.unicode.isprintable() and len(self.user_input) < 30:
                    self.user_input += event.unicode
                    self.feedback = ""

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

        # Description text
        y = panel_y + 55
        for line in self.puzzle.description:
            if line == "":
                y += 10
                continue
            txt = self.font.render(line, True, self.WHITE)
            surface.blit(txt, (panel_x + 25, y))
            y += 24

        # Puzzle image
        if self.puzzle_image:
            img_x = panel_x + panel_w - self.puzzle_image.get_width() - 20
            img_y = panel_y + 55
            # Center vertically somewhat if there's height
            surface.blit(self.puzzle_image, (img_x, img_y))

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
