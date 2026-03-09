import sys

import pygame

pygame.init()


WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("NO WAY OUT?")


clock = pygame.time.Clock()
FPS = 60


BLACK = (0, 0, 0)
WHITE = (255, 255, 255)


def main():
    running = True

    # --- The Core Game Loop ---
    while running:
        # 1. Event Handling (Input)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # 2. Game Logic (Updates)

        # 3. Drawing (Rendering)
        screen.fill(BLACK)

        pygame.display.flip()

        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
