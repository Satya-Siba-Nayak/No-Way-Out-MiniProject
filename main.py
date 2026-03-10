import sys

import pygame
from PIL import Image

# Initialize Pygame
pygame.init()
pygame.mixer.init()


def get_gif_dimensions(path):
    """Returns the width and height of the GIF."""
    with Image.open(path) as img:
        return img.size


# Configuration
GIF_PATH = "parallax-mountain-animX1.gif"
MUSIC_PATH = "Sunstone_Meadow.mp3"
ORIG_WIDTH, ORIG_HEIGHT = get_gif_dimensions(GIF_PATH)

# Scale factor (3x makes it 816x480)
SCALE_FACTOR = 3
WINDOW_WIDTH = ORIG_WIDTH * SCALE_FACTOR
WINDOW_HEIGHT = ORIG_HEIGHT * SCALE_FACTOR

screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("NO WAY OUT?")

clock = pygame.time.Clock()
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
GOLD = (255, 215, 0)
RED = (255, 100, 100)

# Fonts
FONT = pygame.font.SysFont("Arial", 28)
TITLE_FONT = pygame.font.SysFont("Arial", 42, bold=True)
SMALL_FONT = pygame.font.SysFont("Arial", 18)


def load_gif_frames(path, target_size):
    """Loads a GIF and returns a list of scaled pygame surfaces."""
    gif = Image.open(path)
    frames = []
    try:
        while True:
            frame_rgba = gif.convert("RGBA")
            frame_str = frame_rgba.tobytes()
            frame_surface = pygame.image.fromstring(frame_str, frame_rgba.size, "RGBA")
            scaled_surface = pygame.transform.scale(frame_surface, target_size)
            frames.append(scaled_surface)
            gif.seek(gif.tell() + 1)
    except EOFError:
        pass
    return frames


def main():
    # 1. Load Music
    try:
        pygame.mixer.music.load(MUSIC_PATH)
        pygame.mixer.music.play(-1)  # Loop indefinitely
        is_muted = False
    except Exception as e:
        print(f"Error loading music: {e}")
        is_muted = True

    # 2. Load GIF frames
    gif_frames = load_gif_frames(GIF_PATH, (WINDOW_WIDTH, WINDOW_HEIGHT))
    current_frame = 0
    frame_delay = 5
    frame_counter = 0

    # Game States
    STATE_LOGIN = "login"
    STATE_GAME = "game"
    current_state = STATE_LOGIN

    # Player Data
    player_name = ""

    # Mute Button Rect
    mute_button_rect = pygame.Rect(WINDOW_WIDTH - 50, 10, 40, 40)

    running = True
    while running:
        # 1. Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if mute_button_rect.collidepoint(event.pos):
                    is_muted = not is_muted
                    if is_muted:
                        pygame.mixer.music.pause()
                    else:
                        pygame.mixer.music.unpause()

            if current_state == STATE_LOGIN:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        if player_name.strip():
                            current_state = STATE_GAME
                    elif event.key == pygame.K_BACKSPACE:
                        player_name = player_name[:-1]
                    else:
                        if len(player_name) < 15:
                            player_name += event.unicode

        # 2. Logic (Updates)
        frame_counter += 1
        if frame_counter >= frame_delay:
            current_frame = (current_frame + 1) % len(gif_frames)
            frame_counter = 0

        # 3. Drawing (Rendering)
        if gif_frames:
            screen.blit(gif_frames[current_frame], (0, 0))
        else:
            screen.fill(BLACK)

        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        screen.blit(overlay, (0, 0))

        # --- Mute Icon (Drawn in the corner) ---
        pygame.draw.rect(screen, GRAY if is_muted else WHITE, mute_button_rect, 2)
        # Simple procedural icon: Speaker shape
        icon_color = RED if is_muted else WHITE
        pygame.draw.polygon(
            screen,
            icon_color,
            [
                (mute_button_rect.x + 10, mute_button_rect.y + 15),
                (mute_button_rect.x + 18, mute_button_rect.y + 15),
                (mute_button_rect.x + 25, mute_button_rect.y + 10),
                (mute_button_rect.x + 25, mute_button_rect.y + 30),
                (mute_button_rect.x + 18, mute_button_rect.y + 25),
                (mute_button_rect.x + 10, mute_button_rect.y + 25),
            ],
        )
        if is_muted:
            # Draw an 'X' over it
            pygame.draw.line(
                screen,
                RED,
                (mute_button_rect.x + 10, mute_button_rect.y + 10),
                (mute_button_rect.x + 30, mute_button_rect.y + 30),
                3,
            )
            pygame.draw.line(
                screen,
                RED,
                (mute_button_rect.x + 30, mute_button_rect.y + 10),
                (mute_button_rect.x + 10, mute_button_rect.y + 30),
                3,
            )

        if current_state == STATE_LOGIN:
            title_surf = TITLE_FONT.render("NO WAY OUT?", True, WHITE)
            title_rect = title_surf.get_rect(
                center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT * 0.2)
            )
            screen.blit(title_surf, title_rect)

            prompt_surf = FONT.render("Enter Player Name:", True, WHITE)
            prompt_rect = prompt_surf.get_rect(
                center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT * 0.45)
            )
            screen.blit(prompt_surf, prompt_rect)

            input_box_rect = pygame.Rect(
                WINDOW_WIDTH // 2 - 150, WINDOW_HEIGHT * 0.52, 300, 45
            )
            pygame.draw.rect(screen, WHITE, input_box_rect, 2)

            cursor = "|" if (pygame.time.get_ticks() // 500) % 2 == 0 else ""
            name_surf = FONT.render(player_name + cursor, True, WHITE)
            name_rect = name_surf.get_rect(center=input_box_rect.center)
            screen.blit(name_surf, name_rect)

            footer_surf = SMALL_FONT.render("Press ENTER to start", True, GRAY)
            footer_rect = footer_surf.get_rect(
                center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT * 0.85)
            )
            screen.blit(footer_surf, footer_rect)

        elif current_state == STATE_GAME:
            welcome_surf = TITLE_FONT.render(f"Welcome, {player_name}!", True, GOLD)
            welcome_rect = welcome_surf.get_rect(
                center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT * 0.3)
            )
            screen.blit(welcome_surf, welcome_rect)

            msg_surf = FONT.render("GAME IN PROGRESS", True, WHITE)
            msg_rect = msg_surf.get_rect(
                center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT * 0.5)
            )
            screen.blit(msg_surf, msg_rect)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
