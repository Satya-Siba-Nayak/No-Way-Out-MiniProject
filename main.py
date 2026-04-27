"""
NO WAY OUT? — Main Entry Point

This file initializes Pygame and starts the State Machine.
All game logic lives in the states/ and engine/ packages.
"""

import sys
import pygame
from PIL import Image
from engine.state_machine import StateMachine
from states.menu_state import MenuState


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

GIF_PATH = "parallax-mountain-animX1.gif"
FPS = 60


def get_gif_dimensions(path):
    """Read the native size of the GIF so we can scale consistently."""
    with Image.open(path) as img:
        return img.size


def main():
    # --- Pygame init --------------------------------------------------------
    pygame.init()
    pygame.mixer.init()

    # Window size (816 × 480 — same as original)
    try:
        orig_w, orig_h = get_gif_dimensions(GIF_PATH)
    except FileNotFoundError:
        orig_w, orig_h = 272, 160          # fallback

    scale = 3
    screen_w = orig_w * scale
    screen_h = orig_h * scale

    screen = pygame.display.set_mode((screen_w, screen_h))
    pygame.display.set_caption("NO WAY OUT?")
    clock = pygame.time.Clock()

    # --- Shared game context ------------------------------------------------
    # This dict is passed to every state so they can share data
    # (player name, save info, screen dimensions, etc.)
    game_context = {
        "screen_w": screen_w,
        "screen_h": screen_h,
        "player_name": "",
        "load_save": False,
        "save_data": None,
    }

    # --- State Machine ------------------------------------------------------
    sm = StateMachine()
    sm.push(MenuState(sm, game_context))

    # --- Main Loop ----------------------------------------------------------
    while True:
        dt = clock.tick(FPS) / 1000.0       # delta time in seconds

        # Collect events once, pass to current state
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        sm.handle_events(events)
        sm.update(dt)
        sm.draw(screen)

        pygame.display.flip()


if __name__ == "__main__":
    main()
