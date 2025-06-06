import pygame
import random
import math
import json
import os

# Initialize Pygame
pygame.init()

# Game Variables (teaching variables and data types)
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GAME_TITLE = "Simple Racing Game"
IS_RUNNING = True
FPS = 60

# Colors (teaching lists and tuples)
COLORS = [
    (255, 255, 255),  # WHITE
    (0, 0, 0),      # BLACK
    (255, 0, 0),    # RED
    (0, 255, 0),    # GREEN
    (0, 0, 255),    # BLUE
    (128, 128, 128),  # GRAY
    (255, 215, 0)   # GOLD (for coin)
]

# Create game window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption(GAME_TITLE)
clock = pygame.time.Clock()

# Teaching 2D Lists - Track Layouts
# 0 = road, 1 = wall
TRACKS = [
    # Track 1: Simple Circuit
    [
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 0, 1],
        [1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1],
        [1, 0, 1, 0, 0, 0, 1, 1, 0, 0, 0, 1, 0, 1],
        [1, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 1],
        [1, 0, 1, 0, 0, 0, 1, 1, 0, 0, 0, 1, 0, 1],
        [1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1],
        [1, 0, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    ],
    # Track 2: Figure 8
    [
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 0, 1],
        [1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 1],
        [1, 1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 1, 1],
        [1, 1, 1, 0, 0, 1, 1, 1, 1, 0, 0, 1, 1, 1],
        [1, 1, 1, 0, 0, 1, 1, 1, 1, 0, 0, 1, 1, 1],
        [1, 1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 1, 1],
        [1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 1],
        [1, 0, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    ]
]

class Track:
    """Class to represent a race track"""
    def __init__(self, layout):
        self.layout = layout
        self.block_size = 55
        self.walls = []
        self.create_walls()
        self.coin_pos = None
        self.coins_collected = 0
        self.start_time = None
        self.high_score = float('inf')
    
    def create_walls(self):
        """Convert the layout into actual wall rectangles"""
        for row in range(len(self.layout)):
            for col in range(len(self.layout[0])):
                if self.layout[row][col] == 1:  # If it's a wall
                    wall = pygame.Rect(
                        col * self.block_size + 20,  # Small offset from left
                        row * self.block_size + 10,  # Small offset from top
                        self.block_size,
                        self.block_size
                    )
                    self.walls.append(wall)
    
    def create_coin(self):
        """Create a new coin at a random empty position"""
        while True:
            row = random.randint(1, len(self.layout)-2)
            col = random.randint(1, len(self.layout[0])-2)
            if self.layout[row][col] == 0:
                self.coin_pos = (
                    col * self.block_size + 20 + self.block_size//2,
                    row * self.block_size + 10 + self.block_size//2
                )
                break
    
    def draw(self):
        """Draw the track walls and coin"""
        # Draw all walls
        for wall in self.walls:
            pygame.draw.rect(screen, COLORS[5], wall)
        
        # Draw coin if it exists
        if self.coin_pos:
            pygame.draw.circle(screen, COLORS[6], self.coin_pos, 10)
    
    def check_collision(self, car_rect):
        """Check if car has hit any walls"""
        for wall in self.walls:
            if car_rect.colliderect(wall):
                return True
        return False

    def check_coin_collision(self, car_rect):
        """Check if car has collected the coin"""
        if self.coin_pos:
            coin_rect = pygame.Rect(
                self.coin_pos[0] - 10,
                self.coin_pos[1] - 10,
                20, 20
            )
            return car_rect.colliderect(coin_rect)
        return False

class Car:
    """Class to represent the player's car"""
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.width = 30
        self.height = 15
        self.color = color
        self.speed = 0
        self.angle = 0
    
    def move(self, track):
        """Handle car movement and collision"""
        # Get pressed keys
        keys = pygame.key.get_pressed()
        
        # Store old position for collision checking
        old_x = self.x
        old_y = self.y
        
        # Rotation (reduced from 5 to 3 degrees per press)
        if keys[pygame.K_LEFT]:
            self.angle -= 3
        if keys[pygame.K_RIGHT]:
            self.angle += 3
        
        # Forward/Backward movement (reduced acceleration from 0.2 to 0.1, max speed from 5 to 3)
        if keys[pygame.K_UP]:
            self.speed = min(self.speed + 0.1, 3)
        elif keys[pygame.K_DOWN]:
            self.speed = max(self.speed - 0.1, -1.5)  # Reduced reverse speed from -2 to -1.5
        else:
            self.speed *= 0.95  # Friction
        
        # Apply movement
        self.x += math.cos(math.radians(self.angle)) * self.speed
        self.y += math.sin(math.radians(self.angle)) * self.speed
        
        # Create car rectangle for collision detection
        car_rect = pygame.Rect(self.x - self.width/2, self.y - self.height/2, 
                             self.width, self.height)
        
        # Check collision with track
        if track.check_collision(car_rect):
            # If collision, revert to old position
            self.x = old_x
            self.y = old_y
            self.speed = 0
    
    def draw(self):
        """Draw the car on the screen"""
        # Calculate car corners for rotation
        cos_angle = math.cos(math.radians(self.angle))
        sin_angle = math.sin(math.radians(self.angle))
        
        # Car corners relative to center
        corners = [
            (-self.width/2, -self.height/2),
            (self.width/2, -self.height/2),
            (self.width/2, self.height/2),
            (-self.width/2, self.height/2)
        ]
        
        # Rotate and translate corners
        rotated_corners = []
        for corner_x, corner_y in corners:
            rotated_x = corner_x * cos_angle - corner_y * sin_angle + self.x
            rotated_y = corner_x * sin_angle + corner_y * cos_angle + self.y
            rotated_corners.append((rotated_x, rotated_y))
        
        # Draw car
        pygame.draw.polygon(screen, self.color, rotated_corners)

def load_high_scores():
    """Load high scores from file"""
    try:
        if os.path.exists('racing_high_scores.json'):
            with open('racing_high_scores.json', 'r') as f:
                scores = json.load(f)
                # Convert track layouts to strings for dictionary keys
                return {0: scores.get('0', float('inf')),
                       1: scores.get('1', float('inf'))}
    except:
        pass
    return {0: float('inf'), 1: float('inf')}

def save_high_scores(track_index, time):
    """Save new high score if it's better than previous"""
    scores = load_high_scores()
    # Only save if it's a better time
    if time < scores[track_index]:
        scores[track_index] = time
        try:
            with open('racing_high_scores.json', 'w') as f:
                # Convert track indices to strings for JSON
                json_scores = {str(k): v for k, v in scores.items()}
                json.dump(json_scores, f)
        except:
            pass
    return scores[track_index]

# Load high scores at start
high_scores = load_high_scores()

def display_track_select():
    """Draw the track selection menu"""
    font = pygame.font.Font(None, 48)
    small_font = pygame.font.Font(None, 36)
    
    # Display title
    title = font.render('Racing Game', True, COLORS[0])
    title_rect = title.get_rect(center=(SCREEN_WIDTH/2, 100))
    screen.blit(title, title_rect)
    
    # Track names and their numbers
    track_names = ["Simple Circuit", "Figure 8"]
    for i, name in enumerate(track_names):
        # Track number and name
        text = small_font.render(f'{i+1}: {name}', True, COLORS[0])
        text_rect = text.get_rect(center=(SCREEN_WIDTH/2, 200 + i * 80))
        screen.blit(text, text_rect)
        
        # Display high score
        if high_scores[i] != float('inf'):
            score = f'Best Time: {high_scores[i]:.1f}s'
        else:
            score = 'Not attempted'
        
        score_text = small_font.render(score, True, COLORS[6])
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH/2, 230 + i * 80))
        screen.blit(score_text, score_rect)
    
    # Instructions
    inst_text = small_font.render('Press 1-2 to select track, ESC to quit', True, COLORS[0])
    inst_rect = inst_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT - 100))
    screen.blit(inst_text, inst_rect)
    
    # Game objective
    obj_text = small_font.render('Collect 5 coins as fast as you can!', True, COLORS[6])
    obj_rect = obj_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT - 50))
    screen.blit(obj_text, obj_rect)

def display_game_info(track, elapsed_time):
    """Display game information during gameplay"""
    font = pygame.font.Font(None, 36)
    
    # Display coins collected
    coins_text = font.render(f'Coins: {track.coins_collected}/5', True, COLORS[0])
    screen.blit(coins_text, (10, 10))
    
    # Display timer
    time_text = font.render(f'Time: {elapsed_time:.1f}s', True, COLORS[0])
    screen.blit(time_text, (10, 40))
    
    # Display track's high score
    track_index = TRACKS.index(track.layout)
    if high_scores[track_index] != float('inf'):
        high_score_text = font.render(f'Best: {high_scores[track_index]:.1f}s', True, COLORS[0])
        screen.blit(high_score_text, (10, 70))

# Game states
MENU = 0
RACING = 1
game_state = MENU
current_track = None
player = None

# Main game loop
while IS_RUNNING:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            IS_RUNNING = False
        elif event.type == pygame.KEYDOWN:
            if game_state == MENU:
                if event.key == pygame.K_1:
                    current_track = Track(TRACKS[0])
                    player = Car(125, 75, COLORS[2])  # Red car at track start
                    game_state = RACING
                elif event.key == pygame.K_2:
                    current_track = Track(TRACKS[1])
                    player = Car(125, 75, COLORS[2])  # Red car at track start
                    game_state = RACING
                elif event.key == pygame.K_ESCAPE:
                    IS_RUNNING = False
            elif game_state == RACING:
                if event.key == pygame.K_ESCAPE:
                    game_state = MENU
                    current_track.coins_collected = 0
                    current_track.coin_pos = None
                    current_track.start_time = None
    
    # Clear screen
    screen.fill(COLORS[1])  # Black background
    
    # Game state handling
    if game_state == MENU:
        display_track_select()
    elif game_state == RACING:
        # Initialize coin and timer if starting new game
        if current_track.coin_pos is None:
            current_track.create_coin()
            current_track.start_time = pygame.time.get_ticks() / 1000  # Convert to seconds
        
        current_track.draw()
        player.move(current_track)
        player.draw()
        
        # Check coin collection
        car_rect = pygame.Rect(player.x - player.width/2, player.y - player.height/2, 
                             player.width, player.height)
        if current_track.check_coin_collision(car_rect):
            current_track.coins_collected += 1
            if current_track.coins_collected < 5:
                current_track.create_coin()
            else:
                # Game complete
                elapsed_time = pygame.time.get_ticks() / 1000 - current_track.start_time
                track_index = TRACKS.index(current_track.layout)
                # Save and update high score
                high_scores[track_index] = save_high_scores(track_index, elapsed_time)
                current_track.coin_pos = None
                current_track.coins_collected = 0
                current_track.start_time = None
                game_state = MENU
        
        # Display game information
        if current_track.start_time:
            elapsed_time = pygame.time.get_ticks() / 1000 - current_track.start_time
            display_game_info(current_track, elapsed_time)
    
    # Update display
    pygame.display.flip()
    clock.tick(FPS)

# Quit game
pygame.quit()