import sys

import pygame

# --- Initialization ---
pygame.init()

# --- Display Settings ---
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("NO WAY OUT?")

# --- Game Clock ---
clock = pygame.time.Clock()
FPS = 60

# --- Colors ---
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)


def main():
    running = True

    # --- The Core Game Loop ---
    while running:
        # 1. Event Handling (Input)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # When the user clicks the window's 'X'
                running = False

        # 2. Game Logic (Updates)
        # We will add the movement engine and Keya's puzzle logic here!

        # 3. Drawing (Rendering)
        screen.fill(BLACK)  # Clear the screen with a black background

        # Update the full display Surface to the screen
        pygame.display.flip()

        # Cap the frame rate
        clock.tick(FPS)

    # --- Clean Exit ---
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
