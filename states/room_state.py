"""
Room State — the main gameplay screen.

Player walks around the room, interacts with objects, and triggers puzzles.
"""

import sys
import pygame
from states.base_state import State
from engine.player import Player
from engine.room import build_easy_room, TILE
from engine.save_system import save_game


class RoomState(State):
    """Gameplay state — player moves around a room and interacts with objects."""

    def __init__(self, machine, ctx):
        super().__init__(machine, ctx)
        self.room = None
        self.player = None
        self.bookshelf_rect = None
        self.nearby_obj = None          # interactable the player is near
        self.puzzles_solved = set()
        self.show_prompt = False
        self.door_unlocked = False

        # Win state
        self.won = False
        self.win_timer = 0

        # Fonts
        self.font = pygame.font.SysFont("Arial", 20)
        self.big_font = pygame.font.SysFont("Arial", 36, bold=True)
        self.small_font = pygame.font.SysFont("Arial", 16)

        # Colors
        self.WHITE = (255, 255, 255)
        self.GOLD = (255, 215, 0)
        self.BLACK = (0, 0, 0)
        self.DARK_GREEN = (40, 80, 40)

        # HUD
        self.hud_height = 50

    def enter(self):
        # Build the room
        self.room, start_pos, self.bookshelf_rect = build_easy_room()

        # Load save if continuing
        if self.ctx.get("load_save") and self.ctx.get("save_data"):
            sd = self.ctx["save_data"]
            pos = sd.get("player_position", list(start_pos))
            self.player = Player(pos[0], pos[1])
            self.puzzles_solved = set(sd.get("puzzles_solved", []))
            # Mark interactables as solved
            for obj in self.room.interactables:
                if obj.puzzle_id in self.puzzles_solved:
                    obj.solved = True
            self._check_door()
        else:
            self.player = Player(start_pos[0], start_pos[1])

    def _check_door(self):
        """Update door label if all puzzles solved."""
        if self.room.all_puzzles_solved():
            self.door_unlocked = True
            for obj in self.room.interactables:
                if obj.puzzle_id is None:  # the door
                    obj.label = "Door 🔓"
                    obj.color = (60, 140, 60)

    def _auto_save(self):
        save_game(
            player_name=self.ctx.get("player_name", "Player"),
            current_room="easy_room",
            puzzles_solved=list(self.puzzles_solved),
            player_pos=(self.player.rect.x, self.player.rect.y),
        )

    # --- Events -------------------------------------------------------------

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                self._auto_save()
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self._auto_save()
                    # Return to menu
                    from states.menu_state import MenuState
                    self.machine.change(MenuState(self.machine, self.ctx))
                    return

                if event.key == pygame.K_e and self.nearby_obj and not self.won:
                    self._interact(self.nearby_obj)

    def _interact(self, obj):
        """Handle interaction with an object."""
        if obj.puzzle_id is not None and not obj.solved:
            # Launch a puzzle overlay
            from states.puzzle_state import PuzzleState
            ps = PuzzleState(self.machine, self.ctx, obj.puzzle_id, self)
            self.machine.push(ps)
        elif obj.puzzle_id is None:
            # It's the door
            if self.door_unlocked:
                self.won = True
                self.win_timer = 0
                self._auto_save()

    def on_puzzle_solved(self, puzzle_id):
        """Callback from PuzzleState when the player solves a puzzle."""
        self.puzzles_solved.add(puzzle_id)
        for obj in self.room.interactables:
            if obj.puzzle_id == puzzle_id:
                obj.solved = True
        self._check_door()
        self._auto_save()

    # --- Update -------------------------------------------------------------

    def update(self, dt):
        if self.won:
            self.win_timer += dt
            if self.win_timer > 5:
                # Back to menu after 5 seconds
                from states.menu_state import MenuState
                self.machine.change(MenuState(self.machine, self.ctx))
            return

        # Move player
        self.player.move(dt, self.room.walls)

        # Clamp to room bounds
        self.player.rect.clamp_ip(
            pygame.Rect(0, 0, self.room.pixel_w, self.room.pixel_h)
        )

        # Check proximity to interactables
        self.nearby_obj = self.room.get_nearby_interactable(self.player.rect)
        self.show_prompt = self.nearby_obj is not None

    # --- Draw ---------------------------------------------------------------

    def draw(self, surface):
        w = self.ctx["screen_w"]
        h = self.ctx["screen_h"]

        # Offset to center the room
        ox = (w - self.room.pixel_w) // 2

        # Create a room surface
        room_surf = pygame.Surface((self.room.pixel_w, self.room.pixel_h))
        self.room.draw(room_surf, self.font)

        # Draw bookshelf decoration
        if self.bookshelf_rect:
            pygame.draw.rect(room_surf, (100, 70, 50), self.bookshelf_rect)
            pygame.draw.rect(room_surf, (60, 40, 30), self.bookshelf_rect, 2)
            lbl = self.small_font.render("Bookshelf", True, self.WHITE)
            room_surf.blit(lbl, lbl.get_rect(
                midbottom=(self.bookshelf_rect.centerx,
                           self.bookshelf_rect.top - 2)))

        # Draw player
        self.player.draw(room_surf)

        # Blit room to screen
        surface.fill(self.BLACK)
        surface.blit(room_surf, (ox, 0))

        # --- HUD bar at bottom ---
        hud_rect = pygame.Rect(0, h - self.hud_height, w, self.hud_height)
        pygame.draw.rect(surface, (30, 30, 40), hud_rect)
        pygame.draw.line(surface, (80, 80, 100), (0, h - self.hud_height),
                         (w, h - self.hud_height), 2)

        # Player name
        name = self.font.render(
            f"  {self.ctx.get('player_name', 'Player')}", True, self.GOLD)
        surface.blit(name, (10, h - self.hud_height + 14))

        # Puzzle progress
        total = sum(1 for o in self.room.interactables if o.puzzle_id)
        solved = len(self.puzzles_solved)
        prog = self.font.render(
            f"Puzzles: {solved}/{total}", True, self.WHITE)
        surface.blit(prog, (w - 160, h - self.hud_height + 14))

        # Controls hint
        ctrl = self.small_font.render(
            "WASD/Arrows: Move | E: Interact | ESC: Menu", True, (150, 150, 160))
        surface.blit(ctrl, ctrl.get_rect(center=(w // 2, h - self.hud_height + 25)))

        # Interaction prompt
        if self.show_prompt and self.nearby_obj and not self.won:
            label = self.nearby_obj.label
            if self.nearby_obj.puzzle_id is None:
                if self.door_unlocked:
                    prompt_text = f"Press E to open the {label}"
                else:
                    prompt_text = f"{label} — Solve all puzzles to unlock"
            elif self.nearby_obj.solved:
                prompt_text = f"{label} — Already solved ✓"
            else:
                prompt_text = f"Press E to examine the {label}"

            prompt_surf = self.font.render(prompt_text, True, self.GOLD)
            prompt_bg = pygame.Surface(
                (prompt_surf.get_width() + 20, prompt_surf.get_height() + 10),
                pygame.SRCALPHA)
            prompt_bg.fill((0, 0, 0, 180))
            prompt_x = w // 2 - prompt_bg.get_width() // 2
            prompt_y = h - self.hud_height - 40
            surface.blit(prompt_bg, (prompt_x, prompt_y))
            surface.blit(prompt_surf, (prompt_x + 10, prompt_y + 5))

        # Win overlay
        if self.won:
            self._draw_win(surface, w, h)

    def _draw_win(self, surface, w, h):
        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        surface.blit(overlay, (0, 0))

        win_text = self.big_font.render("🎉  YOU ESCAPED!  🎉", True, self.GOLD)
        surface.blit(win_text, win_text.get_rect(center=(w // 2, h // 2 - 20)))

        sub = self.font.render("Congratulations! Easy level complete.",
                               True, self.WHITE)
        surface.blit(sub, sub.get_rect(center=(w // 2, h // 2 + 25)))

        hint = self.small_font.render("Returning to menu...", True, (150, 150, 160))
        surface.blit(hint, hint.get_rect(center=(w // 2, h // 2 + 60)))

    # --- Lifecycle ----------------------------------------------------------

    def pause(self):
        """Game pauses when puzzle overlay is on top."""
        pass

    def resume(self):
        """Puzzle closed — back to gameplay."""
        pass
