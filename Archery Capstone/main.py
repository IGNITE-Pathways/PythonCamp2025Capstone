import sys
import os
import pygame
from pygame.locals import QUIT
import time
import random

# =============================================================================
# ENVIRONMENT SETUP
# =============================================================================

# Set environment variables for headless systems
if os.name == 'posix':  # Linux/Mac
    os.environ['SDL_VIDEODRIVER'] = 'x11'
elif os.name == 'nt':   # Windows
    os.environ['SDL_VIDEODRIVER'] = 'windib'

# =============================================================================
# CONSTANTS AND CONFIGURATION
# =============================================================================

# Game dimensions
WIDTH, HEIGHT = 800, 600
GAME_DURATION = 60  # seconds
ARROW_SPEED = 30
TARGET_SPEED = 5
TARGET_FREQUENCY = 30  # controls how often a new target appears
ARROW_COOLDOWN = 0.5  # seconds between shots

# File paths
SCORE_FILE = "personal_best.txt"
FONT_PATH = os.path.join("fonts", "AlmendraSC-Regular.ttf")

# =============================================================================
# GAME SETUP
# =============================================================================

# Change working directory to the script's location
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Initialize Pygame with error handling
try:
    pygame.init()
    pygame.mixer.init()
except pygame.error as e:
    print(f"Error initializing Pygame: {e}")
    sys.exit(1)

# =============================================================================
# DISPLAY SETUP
# =============================================================================

def setup_display():
    """Set up the game display with error handling."""
    display_modes = [
        ((WIDTH, HEIGHT), 0),  # Normal mode
        ((WIDTH, HEIGHT), pygame.HIDDEN),  # Hidden mode
        ((WIDTH, HEIGHT), pygame.NOFRAME),  # No frame mode
        ((800, 600), 0),  # Fallback resolution
        ((640, 480), 0),  # Lower resolution
    ]
    
    for mode, flags in display_modes:
        try:
            print(f"Trying display mode: {mode} with flags: {flags}")
            screen = pygame.display.set_mode(mode, flags)
            pygame.display.set_caption('Archery!')
            print(f"Successfully created display: {mode}")
            return screen
        except pygame.error as e:
            print(f"Failed to create display {mode}: {e}")
            continue
    
    # If all modes fail, provide detailed error information
    print("\n" + "="*50)
    print("DISPLAY INITIALIZATION FAILED")
    print("="*50)
    print("Possible solutions:")
    print("1. Install/update graphics drivers")
    print("2. Install X11 (Linux): sudo apt-get install x11-apps")
    print("3. Set environment variable: export SDL_VIDEODRIVER=x11")
    print("4. Try running with: python -c 'import pygame; pygame.init()'")
    print("5. Check if you're running on a headless system (server)")
    print("6. Reinstall Pygame: pip uninstall pygame && pip install pygame")
    print("="*50)
    
    # Try one last time with minimal settings
    try:
        print("Attempting minimal display setup...")
        os.environ['SDL_VIDEODRIVER'] = 'dummy'
        pygame.display.quit()
        pygame.display.init()
        screen = pygame.display.set_mode((1, 1))
        print("Minimal display created (game may not be visible)")
        return screen
    except:
        print("All display attempts failed. Exiting...")
        sys.exit(1)

# =============================================================================
# SOUND SYSTEM
# =============================================================================

sounds = {
    "arrow_shot": pygame.mixer.Sound("sounds/arrow_shot.wav"),
    "target_hit_blue": pygame.mixer.Sound("sounds/hit_blue.wav"),
    "target_hit_red": pygame.mixer.Sound("sounds/hit_red.wav"),
    "game_start": pygame.mixer.Sound("sounds/start.ogg"),
    "game_end": pygame.mixer.Sound("sounds/end.ogg"),
    "button_click": pygame.mixer.Sound("sounds/click.wav"),
}

# Set appropriate volumes for each sound effect
sounds["arrow_shot"].set_volume(0.2)      # Moderate volume for frequent shots
sounds["target_hit_blue"].set_volume(0.9)  # Higher volume for successful hits
sounds["target_hit_red"].set_volume(0.9)   # Highest volume for high-value targets
sounds["game_start"].set_volume(0.8)       # High volume for game start announcement
sounds["game_end"].set_volume(0.9)         # Very high volume for game end
sounds["button_click"].set_volume(0.6)     # Low volume for UI feedback

# Background music setup
def setup_background_music():
    """Set up and play background music."""
    try:
        pygame.mixer.music.load("sounds/backgroundmusic.wav")
        pygame.mixer.music.set_volume(0.3)  # Lower volume for background music
        pygame.mixer.music.play(-1)  # -1 means loop indefinitely
        print("Background music started")
    except pygame.error as e:
        print(f"Could not load background music: {e}")

def stop_background_music():
    """Stop the background music."""
    try:
        pygame.mixer.music.stop()
        print("Background music stopped")
    except pygame.error as e:
        print(f"Could not stop background music: {e}")

def pause_background_music():
    """Pause the background music."""
    try:
        pygame.mixer.music.pause()
    except pygame.error as e:
        print(f"Could not pause background music: {e}")

def unpause_background_music():
    """Unpause the background music."""
    try:
        pygame.mixer.music.unpause()
    except pygame.error as e:
        print(f"Could not unpause background music: {e}")

# =============================================================================
# ASSET LOADING
# =============================================================================

def safe_load_image(path, size=None):
    """Safely load and optionally resize an image."""
    try:
        img = pygame.image.load(path).convert_alpha()
        if size:
            img = pygame.transform.scale(img, size)
        return img
    except pygame.error as e:
        print(f"Error loading image '{path}': {e}")
        sys.exit(1)

def load_game_assets():
    """Load all game assets after display is initialized."""
    global arrow_image, archer_image, blue_target_image, red_target_image
    global play_button_image, main_menu_background_image, background_image
    
    print("Loading game assets...")
    
    # Load game assets
    arrow_image = safe_load_image('sprites/arrow2.png', (50, 50))
    archer_image = safe_load_image('sprites/archer.png', (100, 100))
    blue_target_image = safe_load_image('sprites/bluetarget.png', (65, 65))
    red_target_image = safe_load_image('sprites/red_target.png', (65, 65))
    play_button_image = safe_load_image('sprites/play_button.png', (200, 200))
    main_menu_background_image = safe_load_image('sprites/background.png', (800, 600))
    background_image = safe_load_image('sprites/sunset.png', (800, 600))
    
    print("All assets loaded successfully!")

# =============================================================================
# FONT SETUP
# =============================================================================

def setup_font():
    """Set up the game font."""
    global font
    try:
        font = pygame.font.Font(FONT_PATH, 36)
    except FileNotFoundError:
        print("Almendra SC font not found. Using default font.")
        font = pygame.font.Font(None, 36)

# =============================================================================
# GAME OBJECTS
# =============================================================================

class Target:
    """Represents a moving target in the game."""
    
    def __init__(self, image):
        self.image = image
        self.rect = image.get_rect()
        self.direction = random.choice(["left", "right"])
        self.speed = random.randint(1, 8)
        
        # Set initial position
        self.rect.y = random.randint(165, 450)
        
        if self.direction == "left":
            self.rect.right = WIDTH  # target starts from the right edge
        else:
            self.rect.left = 0  # target starts from the left edge

    def move(self):
        """Move the target across the screen."""
        if self.direction == "left":
            self.rect.x -= self.speed
        else:
            self.rect.x += self.speed

    def draw(self, surface):
        """Draw the target on the given surface."""
        surface.blit(self.image, self.rect)

    def is_off_screen(self, screen_width):
        """Check if target has moved off the screen."""
        return self.rect.right < 0 or self.rect.left > screen_width


class ScorePopup:
    """Represents a floating score popup when hitting targets."""
    
    def __init__(self, x, y, points):
        self.x = x
        self.y = y
        self.points = points
        self.life = 30

    def update(self):
        """Update popup position and life."""
        self.y -= 1
        self.life -= 1

    def draw(self, surface):
        """Draw the popup on the given surface."""
        popup_text = font.render(f"+{self.points}", True, (255, 215, 0))
        surface.blit(popup_text, (self.x, self.y))

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def draw_text_with_shadow(surface, text, x, y, font, color, shadow_color=(0, 0, 0), offset=2):
    """Draw text with a shadow effect."""
    shadow = font.render(text, True, shadow_color)
    surface.blit(shadow, (x + offset, y + offset))
    real_text = font.render(text, True, color)
    surface.blit(real_text, (x, y))


def load_personal_best():
    """Load the player's personal best score from file."""
    try:
        with open(SCORE_FILE, "r") as f:
            try:
                return int(f.read().strip())
            except ValueError:
                return "Error"
    except FileNotFoundError:
        return "None"


def save_personal_best(score):
    """Save the player's personal best score to file."""
    with open(SCORE_FILE, "w") as f:
        f.write(str(score))


def show_countdown():
    """Display a countdown before the game starts."""
    for i in range(3, 0, -1):
        screen.blit(background_image, (0, 0))
        text = font.render(str(i), True, (255, 255, 255))
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2))
        pygame.display.flip()
        pygame.time.delay(800)

    screen.blit(background_image, (0, 0))
    text = font.render("Get Ready...", True, (255, 255, 255))
    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2))
    pygame.display.flip()
    pygame.time.delay(800)

# =============================================================================
# GAME STATE MANAGEMENT
# =============================================================================

def show_play_screen(is_game_over):
    """Display the main menu or game over screen."""
    while True:
        screen.blit(background_image, (0, 0))

        if is_game_over:
            # Game over screen
            game_over_text = font.render(f"Game Over! Your score is: {score}", True, (255, 255, 255))
            screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 100))

            # Personal best display
            title = font.render(f"Personal Best: {personal_best}", True, (255, 255, 255))
            screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 2 + 30))
        else:
            # Main menu screen
            screen.blit(main_menu_background_image, (0, 0))
            title = font.render(f"Personal Best: {personal_best}", True, (255, 255, 255))
            screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 2 + 30))

        # Draw play button
        screen.blit(play_button_image, play_button_rect)
        pygame.display.flip()

        # Handle events
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if play_button_rect.collidepoint(pygame.mouse.get_pos()):
                    sounds["button_click"].play()
                    return

# =============================================================================
# MAIN GAME LOOP
# =============================================================================

def run_game():
    """Main game loop."""
    global score, start_time, arrows, targets, cycles_until_new_target, game_running, personal_best, target_frequency, last_shot_time, arrow_cooldown

    # Initialize game state
    score = 0
    start_time = time.time()
    arrows = []
    targets = []
    cycles_until_new_target = 0
    game_running = True
    target_frequency = TARGET_FREQUENCY
    arrow_cooldown = ARROW_COOLDOWN
    last_shot_time = 0

    # Show countdown and start game
    show_countdown()
    sounds["game_start"].stop()
    sounds["game_start"].play()
    
    # Start background music
    setup_background_music()

    # Main game loop
    while game_running:
        # Handle events
        for event in pygame.event.get():
            if event.type == QUIT:
                stop_background_music()  # Stop background music before quitting
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    # Fire arrow with cooldown
                    current_time = time.time()
                    if current_time - last_shot_time >= arrow_cooldown:
                        new_arrow = arrow_image.get_rect()
                        new_arrow.center = archer_rect.center
                        arrows.append(new_arrow)
                        
                        sounds["arrow_shot"].stop()
                        sounds["arrow_shot"].play()
                        last_shot_time = current_time
                elif event.key == pygame.K_m:
                    # Toggle background music mute/unmute
                    if pygame.mixer.music.get_busy():
                        pause_background_music()
                    else:
                        unpause_background_music()

        # Handle continuous input
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and archer_rect.left > 0:
            archer_rect.x -= 10
        if keys[pygame.K_RIGHT] and archer_rect.right < WIDTH:
            archer_rect.x += 10

        # Update arrows
        for arrow in arrows[:]:
            arrow.y -= ARROW_SPEED
            if arrow.bottom < 0:
                arrows.remove(arrow)

        # Calculate game progress for difficulty scaling
        elapsed_time = time.time() - start_time
        game_progress = elapsed_time / GAME_DURATION  # 0.0 to 1.0
        
        # Spawn new targets with limit to prevent clutter
        max_targets = 8 if game_progress < 0.7 else 5  # Reduce max targets near end
        
        if cycles_until_new_target >= target_frequency and len(targets) < max_targets:
            new_target = Target(random.choice([blue_target_image, blue_target_image, red_target_image]))
            targets.append(new_target)
            cycles_until_new_target = 0
        else:
            cycles_until_new_target += 1

        # Update targets
        for target in targets[:]:
            target.move()
            if target.is_off_screen(WIDTH):
                targets.remove(target)

        # Check collisions
        for arrow in arrows[:]:
            for target in targets[:]:
                if arrow.colliderect(target.rect):
                    if target.image == blue_target_image:
                        score += 1
                        sounds["target_hit_blue"].stop()
                        sounds["target_hit_blue"].play()
                    elif target.image == red_target_image:
                        score += 2
                        sounds["target_hit_red"].stop()
                        sounds["target_hit_red"].play()
                    
                    arrows.remove(arrow)
                    targets.remove(target)
                    break

        # Draw everything
        screen.blit(background_image, (0, 0))
        screen.blit(archer_image, archer_rect)
        
        for target in targets:
            target.draw(screen)
        
        for arrow in arrows:
            screen.blit(arrow_image, arrow)

        # Draw UI
        draw_text_with_shadow(screen, f"Score: {score}", 10, 10, font, (255, 255, 255))
        
        # Timer (positioned to stay on screen)
        elapsed_time = int(time.time() - start_time)
        remaining_time = max(0, GAME_DURATION - elapsed_time)
        timer_text = font.render(f"Time: {remaining_time}", True, (255, 255, 255))
        timer_x = WIDTH - timer_text.get_width() - 10  # Ensure it doesn't go off right edge
        screen.blit(timer_text, (timer_x, 10))
        
        # Music status indicator (positioned to stay on screen)
        music_status = "MUSIC: ON" if pygame.mixer.music.get_busy() else "MUSIC: OFF"
        music_text = font.render(music_status, True, (255, 255, 255))
        music_x = WIDTH - music_text.get_width() - 10  # Ensure it doesn't go off right edge
        screen.blit(music_text, (music_x, 40))
        
        # Controls hint (positioned to stay on screen)
        controls_text = font.render("M: Toggle Music", True, (200, 200, 200))
        controls_y = HEIGHT - controls_text.get_height() - 10  # Ensure it doesn't go off bottom
        screen.blit(controls_text, (10, controls_y))
        
        # Point values hint (top middle) with colored text
        red_text = font.render("Red=2pts", True, (255, 0, 0))  # Red color
        blue_text = font.render("Blue=1pt", True, (0, 0, 255))  # Blue color
        
        # Calculate positions to center both texts
        total_width = red_text.get_width() + 20 + blue_text.get_width()  # 20 pixels spacing
        start_x = (WIDTH - total_width) // 2
        
        screen.blit(red_text, (start_x, 10))
        screen.blit(blue_text, (start_x + red_text.get_width() + 20, 10))

        # Difficulty scaling - balanced curve to reduce clutter near end
        # Create a bell curve: increase difficulty in middle, decrease near end
        if game_progress < 0.5:
            # First half: gradually increase difficulty
            difficulty_factor = game_progress * 2  # 0.0 to 1.0
        else:
            # Second half: gradually decrease difficulty to reduce clutter
            difficulty_factor = 1.0 - (game_progress - 0.5) * 1.5  # 1.0 to 0.25
        
        # Apply difficulty with limits to prevent too many targets
        target_frequency = max(15, TARGET_FREQUENCY - (difficulty_factor * 20))
        
        # Reduce arrow cooldown more gradually
        arrow_cooldown = max(0.1, ARROW_COOLDOWN - (elapsed_time * 0.0005))

        # Check game end condition
        if remaining_time <= 0:
            sounds["game_end"].stop()
            sounds["game_end"].play()
            stop_background_music()  # Stop background music when game ends
            game_running = False

        pygame.display.flip()
        clock.tick(25)

    # Update personal best
    if not personal_best == "None" and not personal_best == "Error":
        if isinstance(personal_best, int) and score > personal_best:
            personal_best = score
    else:
        personal_best = score

    save_personal_best(personal_best)

# =============================================================================
# GAME INITIALIZATION
# =============================================================================

# Set up display
screen = setup_display()

# Load game assets after display is initialized
load_game_assets()

# Set up font
setup_font()

# Set up game objects
archer_rect = archer_image.get_rect()
archer_rect.midbottom = (WIDTH // 2, HEIGHT)

play_button_rect = play_button_image.get_rect()
play_button_rect.center = (WIDTH // 2, (HEIGHT // 2) + 125)

# Initialize game variables
arrows = []
targets = []
score = 0
personal_best = load_personal_best()
clock = pygame.time.Clock()

# =============================================================================
# MAIN PROGRAM LOOP
# =============================================================================

if __name__ == "__main__":
    show_play_screen(is_game_over=False)  # Show main menu first
    
    while True:
        run_game()
        show_play_screen(is_game_over=True)
