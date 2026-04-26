import sys
import math
import random
import pygame
from states.base_state import State
from states.menu_state import MenuState

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.vx = random.uniform(-3, 3)
        self.vy = random.uniform(-6, -2)
        self.color = color
        self.life = 255
        self.decay = random.uniform(2, 5)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.1  # gravity
        self.life -= self.decay

    def draw(self, surface):
        if self.life > 0:
            alpha = int(self.life)
            surf = pygame.Surface((6, 6), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*self.color, alpha), (3, 3), 3)
            surface.blit(surf, (int(self.x), int(self.y)))


class VictoryState(State):
    """A celebratory screen shown when the player beats the game."""

    def __init__(self, machine, ctx):
        super().__init__(machine, ctx)
        self.title_font = pygame.font.SysFont("Arial", 60, bold=True)
        self.font = pygame.font.SysFont("Arial", 24)
        
        self.particles = []
        self.colors = [
            (255, 215, 0),   # Gold
            (255, 100, 100), # Red
            (100, 255, 100), # Green
            (100, 200, 255), # Blue
            (255, 150, 255)  # Pink
        ]
        
        self.time = 0
        self.bg_y_offset = 0

    def enter(self):
        # Clear saved state since they beat the game
        self.ctx["current_level"] = "level1"
        self.ctx["puzzles_solved"] = []
        
        # Spawn initial burst of confetti
        w = self.ctx["screen_w"]
        h = self.ctx["screen_h"]
        for _ in range(150):
            self.particles.append(Particle(w//2, h, random.choice(self.colors)))

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                # Return to menu on any key/click
                self.machine.change(MenuState(self.machine, self.ctx))

    def update(self, dt):
        self.time += dt
        
        # Continuously spawn some particles
        w = self.ctx["screen_w"]
        if random.random() < 0.3:
            for _ in range(5):
                self.particles.append(Particle(random.randint(0, w), self.ctx["screen_h"] + 10, random.choice(self.colors)))
                
        # Update particles
        for p in self.particles:
            p.update()
        self.particles = [p for p in self.particles if p.life > 0]
        
        # Slow panning background
        self.bg_y_offset = (self.bg_y_offset + 20 * dt) % 100

    def draw(self, surface):
        w = self.ctx["screen_w"]
        h = self.ctx["screen_h"]

        # Dynamic gradient-like background using moving stripes
        surface.fill((20, 15, 30))
        for y in range(-100, h, 100):
            rect = pygame.Rect(0, y + self.bg_y_offset, w, 50)
            pygame.draw.rect(surface, (30, 20, 45), rect)

        # Draw particles
        for p in self.particles:
            p.draw(surface)

        # Floating Title text
        float_y = math.sin(self.time * 3) * 10
        title = self.title_font.render("YOU ESCAPED!", True, (255, 215, 0))
        # Add shadow
        shadow = self.title_font.render("YOU ESCAPED!", True, (0, 0, 0))
        title_rect = title.get_rect(center=(w // 2, h // 3 + float_y))
        surface.blit(shadow, (title_rect.x + 4, title_rect.y + 4))
        surface.blit(title, title_rect)

        # Congratulations message
        msg1 = self.font.render("Congratulations! You have solved all the puzzles", True, (255, 255, 255))
        msg2 = self.font.render("and made it out alive.", True, (255, 255, 255))
        
        surface.blit(msg1, msg1.get_rect(center=(w // 2, h // 2 + 20)))
        surface.blit(msg2, msg2.get_rect(center=(w // 2, h // 2 + 55)))

        # Blinking prompt
        if int(self.time * 2) % 2 == 0:
            prompt = self.font.render("Press any key to return to Menu", True, (150, 150, 150))
            surface.blit(prompt, prompt.get_rect(center=(w // 2, h - 80)))
