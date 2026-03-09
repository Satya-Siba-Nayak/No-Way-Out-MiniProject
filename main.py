import sys
import pygame
from PIL import Image

# Initialize Pygame
pygame.init()

def get_gif_dimensions(path):
    """Returns the width and height of the GIF."""
    with Image.open(path) as img:
        return img.size

# Configuration
GIF_PATH = "parallax-mountain-animX1.gif"
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
    # Load GIF frames
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
    
    running = True

    while running:
        # 1. Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if current_state == STATE_LOGIN:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        if player_name.strip(): # Only proceed if name is not empty
                            current_state = STATE_GAME
                            print(f"Starting game for: {player_name}")
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
        # Background is shared across states
        if gif_frames:
            screen.blit(gif_frames[current_frame], (0, 0))
        else:
            screen.fill(BLACK)

        # Semi-transparent overlay for readability
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120)) 
        screen.blit(overlay, (0, 0))

        if current_state == STATE_LOGIN:
            # --- LOGIN SCREEN UI ---
            title_surf = TITLE_FONT.render("NO WAY OUT?", True, WHITE)
            title_rect = title_surf.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT * 0.2))
            screen.blit(title_surf, title_rect)

            prompt_surf = FONT.render("Enter Player Name:", True, WHITE)
            prompt_rect = prompt_surf.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT * 0.45))
            screen.blit(prompt_surf, prompt_rect)

            input_box_rect = pygame.Rect(WINDOW_WIDTH // 2 - 150, WINDOW_HEIGHT * 0.52, 300, 45)
            pygame.draw.rect(screen, WHITE, input_box_rect, 2)
            
            cursor = "|" if (pygame.time.get_ticks() // 500) % 2 == 0 else ""
            name_surf = FONT.render(player_name + cursor, True, WHITE)
            name_rect = name_surf.get_rect(center=input_box_rect.center)
            screen.blit(name_surf, name_rect)

            footer_surf = SMALL_FONT.render("Press ENTER to start", True, GRAY)
            footer_rect = footer_surf.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT * 0.85))
            screen.blit(footer_surf, footer_rect)

        elif current_state == STATE_GAME:
            # --- WORK IN PROGRESS SCREEN ---
            welcome_surf = TITLE_FONT.render(f"Welcome, {player_name}!", True, GOLD)
            welcome_rect = welcome_surf.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT * 0.3))
            screen.blit(welcome_surf, welcome_rect)

            msg_surf = FONT.render("GAME IN PROGRESS", True, WHITE)
            msg_rect = msg_surf.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT * 0.5))
            screen.blit(msg_surf, msg_rect)

            sub_msg_surf = SMALL_FONT.render("Building the escape room... Check back soon!", True, GRAY)
            sub_msg_rect = sub_msg_surf.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT * 0.6))
            screen.blit(sub_msg_surf, sub_msg_rect)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
