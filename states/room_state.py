"""
Room State — the main gameplay screen.

Player walks around the room, interacts with objects, and triggers puzzles.
Supports both the legacy code-built room and the TMX-rendered map.
"""

import sys
import pygame
from states.base_state import State
from engine.player import Player
from engine.room import build_easy_room_from_tmx, build_level2_room_from_tmx, build_level3_room_from_tmx, TILE
from engine.save_system import save_game


class RoomState(State):
    """Gameplay state — player moves around a room and interacts with objects."""

    def __init__(self, machine, ctx):
        super().__init__(machine, ctx)
        self.room = None
        self.player = None
        self.nearby_obj = None          # interactable the player is near
        self.puzzles_solved = set()
        self.show_prompt = False
        self.door_unlocked = False

        self.bump_hits = 0
        self.bump_msg_timer = 0.0
        self.blink_timer = 0.0

        # Per-light blink pattern: (light_index, blink_count)
        # Spatial order: top→middle→bottom (indices 1, 2, 0)
        # Top(1) blinks 3×, Middle(2) blinks 2×, Bottom(0) blinks 4×  → answer "324"
        self.BLINK_PATTERN = [(1, 3), (2, 2), (0, 4)]
        self.BLINK_ON = 0.55     # seconds light is ON (slower for easy counting)
        self.BLINK_OFF = 0.50    # seconds light is OFF
        self.BLINK_PERIOD = self.BLINK_ON + self.BLINK_OFF  # 1.05s per blink
        self.PAUSE_BETWEEN = 1.2  # pause between different lights
        self.PAUSE_END = 2.5      # pause at end of full cycle
        self.GLOW_COLOR = (255, 255, 255)  # all white
        # Pre-compute total cycle duration
        self._blink_cycle_duration = 0.0
        for i, (_, count) in enumerate(self.BLINK_PATTERN):
            self._blink_cycle_duration += count * self.BLINK_PERIOD
            if i < len(self.BLINK_PATTERN) - 1:
                self._blink_cycle_duration += self.PAUSE_BETWEEN
            else:
                self._blink_cycle_duration += self.PAUSE_END

        # TMX scaling
        self.scale = 1.0
        self.offset_x = 0
        self.offset_y = 0

        # Feedback overlays
        self.solve_flash_timer = 0.0
        self.gate_open_timer = 0.0

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
        self.RED = (255, 100, 100)

        # HUD
        self.hud_height = 50

    def enter(self):
        screen_w = self.ctx["screen_w"]
        screen_h = self.ctx["screen_h"]

        # Build the room from the TMX map
        level = self.ctx.get("current_level", "level1")
        if level == "level3":
            result = build_level3_room_from_tmx()
        elif level == "level2":
            result = build_level2_room_from_tmx()
        else:
            result = build_easy_room_from_tmx()
        self.room, start_pos = result[0], result[1]

        # Calculate scaling to fit the room in the window
        # The playable area is screen minus the HUD bar
        play_h = screen_h - self.hud_height
        scale_x = screen_w / self.room.pixel_w
        scale_y = play_h / self.room.pixel_h
        self.scale = min(scale_x, scale_y)

        # Center the scaled map in the available area
        scaled_w = int(self.room.pixel_w * self.scale)
        scaled_h = int(self.room.pixel_h * self.scale)
        self.offset_x = (screen_w - scaled_w) // 2
        self.offset_y = (play_h - scaled_h) // 2

        # Get the chosen sprite
        sprite_id = self.ctx.get("sprite_id", "finn")

        # Load save if continuing
        if self.ctx.get("load_save") and self.ctx.get("save_data"):
            sd = self.ctx["save_data"]
            pos = sd.get("player_position", list(start_pos))
            self.player = Player(pos[0], pos[1], sprite_id=sprite_id)
            self.puzzles_solved = set(sd.get("puzzles_solved", []))
            # Mark interactables as solved
            for obj in self.room.interactables:
                if obj.puzzle_id in self.puzzles_solved:
                    obj.solved = True
            self._check_door()
        else:
            self.player = Player(start_pos[0], start_pos[1], sprite_id=sprite_id)

        # Scale down player in Level 2 and Level 3
        if self.ctx.get("current_level") in ["level2", "level3"]:
            self.player.render_scale = 0.70
            self.player.rect.width = 15  # Very small physical footprint
            self.player.rect.height = 15 # to slide through tight furniture gaps

        # Save immediately upon entering a new level cleanly
        self._auto_save()

    def _check_door(self):
        """Update door label if all puzzles solved, or gate if misplaced tile is solved."""
        if self.room.all_puzzles_solved():
            self.door_unlocked = True
            for obj in self.room.interactables:
                if obj.puzzle_id is None and ("Door" in obj.label or "Elevator" in obj.label):
                    obj.label = obj.label.replace("🔒", "🔓")
                    obj.color = (60, 140, 60)
        
        # Check specific level 2 unblock logic
        if self.ctx.get("current_level") == "level2":
            if "blinking_lights" in self.puzzles_solved:
                # Remove gate once the first puzzle (blinking lights) is solved
                gate = next((o for o in self.room.interactables if getattr(o, "label", "") == "Closed Gate"), None)
                if gate:
                    self.room.interactables.remove(gate)
                    if gate.rect in self.room.walls:
                        self.room.walls.remove(gate.rect)
                    self.gate_open_timer = 3.0  # show feedback

    def _auto_save(self):
        save_game(
            player_name=self.ctx.get("player_name", "Player"),
            current_room=self.ctx.get("current_level", "level1"),
            puzzles_solved=list(self.puzzles_solved),
            player_pos=(self.player.rect.x, self.player.rect.y),
            sprite_id=self.ctx.get("sprite_id", "finn"),
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
        if obj.puzzle_id == "misplaced_tile" and not obj.solved:
            if self.bump_hits < 2:
                # Just show a general message or increment
                self.bump_msg_timer = 2.0
                return
            else:
                from states.puzzle_state import PuzzleState
                ps = PuzzleState(self.machine, self.ctx, obj.puzzle_id, self)
                self.machine.push(ps)
        elif obj.puzzle_id is not None and not obj.solved:
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
        self.solve_flash_timer = 0.6   # green flash feedback
        self._check_door()
        self._auto_save()

    def _get_active_light(self):
        """Return (light_index, is_on) for the current blink phase, or (None, False) during pauses."""
        t = self.blink_timer % self._blink_cycle_duration
        elapsed = 0.0
        for light_idx, count in self.BLINK_PATTERN:
            blink_duration = count * self.BLINK_PERIOD
            if t < elapsed + blink_duration:
                local_t = t - elapsed
                within_blink = local_t % self.BLINK_PERIOD
                is_on = within_blink < self.BLINK_ON
                return light_idx, is_on
            elapsed += blink_duration
            # Check if we're in the pause after this light
            if light_idx != self.BLINK_PATTERN[-1][0]:
                if t < elapsed + self.PAUSE_BETWEEN:
                    return None, False
                elapsed += self.PAUSE_BETWEEN
            else:
                # End pause
                return None, False
        return None, False

    # --- Update -------------------------------------------------------------

    def update(self, dt):
        if self.bump_msg_timer > 0:
            self.bump_msg_timer -= dt
        if self.solve_flash_timer > 0:
            self.solve_flash_timer -= dt
        if self.gate_open_timer > 0:
            self.gate_open_timer -= dt

        if self.ctx.get("current_level") == "level2" and "blinking_lights" not in self.puzzles_solved:
            self.blink_timer += dt

        if self.won:
            self.win_timer += dt
            if self.win_timer > 5:
                level = self.ctx.get("current_level", "level1")
                if level == "level1":
                    # Transition to Level 2
                    self.ctx["current_level"] = "level2"
                    self.ctx["puzzles_solved"] = []
                    self.ctx["load_save"] = False
                    from states.room_state import RoomState
                    self.machine.change(RoomState(self.machine, self.ctx))
                elif level == "level2":
                    # Transition to Level 3
                    self.ctx["current_level"] = "level3"
                    self.ctx["puzzles_solved"] = []
                    self.ctx["load_save"] = False
                    from states.room_state import RoomState
                    self.machine.change(RoomState(self.machine, self.ctx))
                else:
                    # Back to menu after beating game (Level 3)
                    from states.menu_state import MenuState
                    self.machine.change(MenuState(self.machine, self.ctx))
            return

        # Move player
        old_x, old_y = self.player.pos_x, self.player.pos_y
        self.player.move(dt, self.room.walls)

        # Clamp to room bounds
        self.player.rect.clamp_ip(
            pygame.Rect(0, 0, self.room.pixel_w, self.room.pixel_h)
        )
        self.player.pos_x = float(self.player.rect.x)
        self.player.pos_y = float(self.player.rect.y)

        # Check bump tile physics interaction
        if self.ctx.get("current_level") == "level2":
            bump = next((o for o in self.room.interactables if o.puzzle_id == "misplaced_tile"), None)
            if bump and not bump.solved and bump.rect.colliderect(self.player.rect):
                if self.bump_hits < 2:
                    # Push back (cancel move)
                    self.player.pos_x, self.player.pos_y = old_x, old_y
                    self.player.rect.x, self.player.rect.y = int(old_x), int(old_y)
                    # Trigger message max once every 2 seconds
                    if self.bump_msg_timer <= 0:
                        self.bump_hits += 1
                        self.bump_msg_timer = 2.0

        # Check proximity to interactables
        self.nearby_obj = self.room.get_nearby_interactable(self.player.rect)
        self.show_prompt = self.nearby_obj is not None

    # --- Draw ---------------------------------------------------------------

    def draw(self, surface):
        w = self.ctx["screen_w"]
        h = self.ctx["screen_h"]

        surface.fill(self.BLACK)

        # Create a room surface at native resolution
        room_surf = pygame.Surface(
            (self.room.pixel_w, self.room.pixel_h), pygame.SRCALPHA
        )
        self.room.draw(room_surf, self.font)

        # Draw player on the room surface (native coords)
        self.player.draw(room_surf)

        # Scale the room surface to fit the window
        scaled_w = int(self.room.pixel_w * self.scale)
        scaled_h = int(self.room.pixel_h * self.scale)
        if self.scale != 1.0:
            scaled_surf = pygame.transform.smoothscale(room_surf,
                                                        (scaled_w, scaled_h))
        else:
            scaled_surf = room_surf

        surface.blit(scaled_surf, (self.offset_x, self.offset_y))

        # Per-light blinking glow for Level 2 hallway
        if self.ctx.get("current_level") == "level2" and "blinking_lights" not in self.puzzles_solved:
            active_light, is_on = self._get_active_light()
            if active_light is not None and is_on and active_light < len(self.room.light_positions):
                light_rect = self.room.light_positions[active_light]
                color = self.GLOW_COLOR
                # Draw a glow circle on the SCALED surface at the scaled position
                cx = int(light_rect.centerx * self.scale) + self.offset_x
                cy = int(light_rect.centery * self.scale) + self.offset_y
                radius = int(36 * self.scale)
                glow_size = radius * 2 + 4
                glow_surf = pygame.Surface((glow_size, glow_size), pygame.SRCALPHA)
                pygame.draw.circle(glow_surf, (*color, 160), (glow_size // 2, glow_size // 2), radius)
                surface.blit(glow_surf, (cx - glow_size // 2, cy - glow_size // 2))

        # --- HUD bar at bottom ---
        hud_rect = pygame.Rect(0, h - self.hud_height, w, self.hud_height)
        pygame.draw.rect(surface, (30, 30, 40), hud_rect)
        pygame.draw.line(surface, (80, 80, 100), (0, h - self.hud_height),
                         (w, h - self.hud_height), 2)

        # Player name
        name = self.font.render(
            f"  {self.ctx.get('player_name', 'Player')}", True, self.GOLD)
        surface.blit(name, (10, h - self.hud_height + 14))

        # Level indicator
        level = self.ctx.get("current_level", "level1")
        if level == "level1":
            level_label = "Level 1"
        elif level == "level2":
            level_label = "Level 2"
        else:
            level_label = "Level 3"
        lvl_surf = self.small_font.render(level_label, True, self.ACCENT if hasattr(self, 'ACCENT') else (130, 180, 255))
        surface.blit(lvl_surf, (10, h - self.hud_height + 2))

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

        # Bump physics message overlay
        if self.bump_msg_timer > 0:
            msg_text = "A strange force pushes you away!" if self.bump_hits < 2 else "The force weakens..."
            msg_surf = self.font.render(msg_text, True, self.RED)
            msg_bg = pygame.Surface((msg_surf.get_width() + 20, msg_surf.get_height() + 10), pygame.SRCALPHA)
            msg_bg.fill((0, 0, 0, 180))
            msg_x = w // 2 - msg_bg.get_width() // 2
            msg_y = h // 2
            surface.blit(msg_bg, (msg_x, msg_y))
            surface.blit(msg_surf, (msg_x + 10, msg_y + 5))

        # Puzzle solve green flash
        if self.solve_flash_timer > 0:
            flash_alpha = int(80 * (self.solve_flash_timer / 0.6))
            flash = pygame.Surface((w, h), pygame.SRCALPHA)
            flash.fill((40, 200, 80, flash_alpha))
            surface.blit(flash, (0, 0))

        # Gate opened message
        if self.gate_open_timer > 0:
            msg = self.font.render("🔓 The gate creaks open...", True, self.GOLD)
            msg_bg = pygame.Surface((msg.get_width() + 20, msg.get_height() + 10), pygame.SRCALPHA)
            msg_bg.fill((0, 0, 0, 180))
            mx = w // 2 - msg_bg.get_width() // 2
            my = h // 3
            surface.blit(msg_bg, (mx, my))
            surface.blit(msg, (mx + 10, my + 5))

        # Win overlay
        if self.won:
            self._draw_win(surface, w, h)

    def _draw_win(self, surface, w, h):
        # Fade-to-black: starts at 160 alpha, ramps to 255 over 5 seconds
        fade = min(255, 160 + int((self.win_timer / 5.0) * 95))
        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, fade))
        surface.blit(overlay, (0, 0))

        # Fade out text as we approach transition
        text_alpha = max(0, 255 - int(max(0, self.win_timer - 3.5) / 1.5 * 255))

        win_text = self.big_font.render("🎉  YOU ESCAPED!  🎉", True, self.GOLD)
        win_text.set_alpha(text_alpha)
        surface.blit(win_text, win_text.get_rect(center=(w // 2, h // 2 - 20)))

        level = self.ctx.get("current_level", "level1")
        if level == "level1":
            sub_text = "Moving to Level 2..."
        elif level == "level2":
            sub_text = "Moving to Level 3..."
        else:
            sub_text = "Congratulations! Game complete."
        sub = self.font.render(sub_text, True, self.WHITE)
        sub.set_alpha(text_alpha)
        surface.blit(sub, sub.get_rect(center=(w // 2, h // 2 + 25)))

        if level in ["level1", "level2"]:
            hint_text = "Loading next area..."
        else:
            hint_text = "Returning to menu..."
        hint = self.small_font.render(hint_text, True, (150, 150, 160))
        hint.set_alpha(text_alpha)
        surface.blit(hint, hint.get_rect(center=(w // 2, h // 2 + 60)))

    # --- Lifecycle ----------------------------------------------------------

    def pause(self):
        """Game pauses when puzzle overlay is on top."""
        pass

    def resume(self):
        """Puzzle closed — back to gameplay."""
        pass
