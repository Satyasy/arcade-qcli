"""
Arcade Shooter Game - Geometry Wars meets Tetris
"""
import pygame
import sys
import random
import math

# Initialize Pygame
pygame.init()

# Get screen dimensions
info = pygame.display.Info()
SCREEN_WIDTH = info.current_w - 100  # Leave some margin
SCREEN_HEIGHT = info.current_h - 100

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (255, 0, 255)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 5
        self.size = 15
        
    def move(self, keys):
        if keys[pygame.K_LEFT] and self.x > self.size:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] and self.x < SCREEN_WIDTH - self.size:
            self.x += self.speed
        if keys[pygame.K_UP] and self.y > self.size:
            self.y -= self.speed
        if keys[pygame.K_DOWN] and self.y < SCREEN_HEIGHT - self.size:
            self.y += self.speed
    
    def draw(self, screen):
        # Draw triangular spaceship
        points = [
            (self.x, self.y - self.size),
            (self.x - self.size, self.y + self.size),
            (self.x + self.size, self.y + self.size)
        ]
        pygame.draw.polygon(screen, WHITE, points)

class Bullet:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 8
        self.size = 3
        
    def update(self):
        self.y -= self.speed
        
    def draw(self, screen):
        pygame.draw.circle(screen, YELLOW, (int(self.x), int(self.y)), self.size)
        
    def is_off_screen(self):
        return self.y < 0

class Block:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = random.uniform(1, 3)
        self.size = random.randint(20, 40)
        self.color = random.choice([RED, GREEN, BLUE, PURPLE, CYAN, ORANGE])
        
    def update(self):
        self.y += self.speed
        
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.size, self.size))
        
    def is_off_screen(self):
        return self.y > SCREEN_HEIGHT

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Arcade Shooter - Easy Mode")
        self.clock = pygame.time.Clock()
        
        # Game objects
        self.player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50)
        self.bullets = []
        self.blocks = []
        
        # Game state
        self.score = 0
        self.running = True
        self.paused = False
        self.game_over = False
        
        # Auto-shooting
        self.last_shot_time = 0
        self.shoot_interval = 300  # milliseconds
        
        # Enemy spawning (one by one)
        self.last_spawn_time = 0
        self.spawn_interval = 2000  # 2 seconds between enemies
        self.max_blocks = 1  # Only one enemy at a time
        
        # Font
        self.font = pygame.font.Font(None, 36)
        self.big_font = pygame.font.Font(None, 72)
        
    def run(self):
        while self.running:
            self.handle_events()
            if not self.paused:
                self.update()
            self.draw()
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p and not self.game_over:
                    self.paused = not self.paused
                elif event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_r and self.game_over:
                    self.restart_game()
        
        # Player movement (only if game is active)
        if not self.paused and not self.game_over:
            keys = pygame.key.get_pressed()
            self.player.move(keys)
    
    def update(self):
        if self.game_over:
            return
            
        current_time = pygame.time.get_ticks()
        
        # Auto-shooting
        if current_time - self.last_shot_time > self.shoot_interval:
            self.bullets.append(Bullet(self.player.x, self.player.y))
            self.last_shot_time = current_time
        
        # Update bullets
        for bullet in self.bullets[:]:
            bullet.update()
            if bullet.is_off_screen():
                self.bullets.remove(bullet)
        
        # Update blocks
        for block in self.blocks[:]:
            block.update()
            if block.is_off_screen():
                self.blocks.remove(block)
                # Game over if block reaches bottom
                self.game_over = True
        
        # Spawn new blocks (one at a time)
        if (len(self.blocks) == 0 and 
            current_time - self.last_spawn_time > self.spawn_interval):
            x = random.randint(50, SCREEN_WIDTH - 90)
            self.blocks.append(Block(x, -40))
            self.last_spawn_time = current_time
        
        # Check collisions
        self.check_collisions()
    
    def restart_game(self):
        """Restart the game"""
        self.player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50)
        self.bullets = []
        self.blocks = []
        self.score = 0
        self.game_over = False
        self.last_shot_time = 0
        self.last_spawn_time = 0
    
    def check_collisions(self):
        for bullet in self.bullets[:]:
            for block in self.blocks[:]:
                if (bullet.x > block.x and bullet.x < block.x + block.size and
                    bullet.y > block.y and bullet.y < block.y + block.size):
                    self.bullets.remove(bullet)
                    self.blocks.remove(block)
                    self.score += 10
                    break
    
    def draw(self):
        self.screen.fill(BLACK)
        
        # Draw game objects
        self.player.draw(self.screen)
        for bullet in self.bullets:
            bullet.draw(self.screen)
        for block in self.blocks:
            block.draw(self.screen)
        
        # Draw UI
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))
        
        # Draw instructions
        if not self.game_over:
            instructions = self.font.render("Arrow keys to move - Auto shooting!", True, WHITE)
            self.screen.blit(instructions, (10, SCREEN_HEIGHT - 30))
        
        if self.paused and not self.game_over:
            pause_text = self.font.render("PAUSED - Press P to continue", True, WHITE)
            text_rect = pause_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            self.screen.blit(pause_text, text_rect)
        
        # Game Over screen
        if self.game_over:
            # Semi-transparent overlay
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(128)
            overlay.fill(BLACK)
            self.screen.blit(overlay, (0, 0))
            
            # Game Over text
            game_over_text = self.big_font.render("GAME OVER", True, RED)
            game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50))
            self.screen.blit(game_over_text, game_over_rect)
            
            # Final score
            final_score_text = self.font.render(f"Final Score: {self.score}", True, WHITE)
            score_rect = final_score_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            self.screen.blit(final_score_text, score_rect)
            
            # Try again instruction
            try_again_text = self.font.render("Press R to Try Again or ESC to Quit", True, WHITE)
            try_rect = try_again_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 50))
            self.screen.blit(try_again_text, try_rect)
        
        pygame.display.flip()

if __name__ == "__main__":
    game = Game()
    game.run()
