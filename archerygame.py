import sys  #represents the system and can manipulate the program
import pygame
from pygame.locals import QUIT #to get program started or ending
import time #timer
import random #random

width = 800
height = 600

SCORE_FILE = "personal_best.txt" #this is where your personal best score will be stored

pygame.init() #turning on the library
pygame.mixer.init() #initializing the smaller subset library which is used for sound and audio


screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Archery Game!") #setting the title to Archery Game!
game_running = True

#Boolean is a true or false value
#Strings - "text"
#Numbers - floats (decimal), integers (without decimals)

arrows = [] #will be storing the arrows that need to be displayed on the screen at any given moment

targets = []

arrow_speed = 30

game_duration = 10

arrow_cooldown = 0.5

target_speed = 5

target_frequency = 30 #how often a new target shows up, every 30 times the game loop a new target will show up

arrow_speed = 30

cycles_until_new_target = 0 #counting the times of the game loop/cycles/frames until a new target needs to be created

last_shot_time = 0

peersonal_best = 0


sounds = {
    "arrow_shot": pygame.mixer.Sound("sounds/arrow_shot.wav"),
    "target_hit_blue": pygame.mixer.Sound("sounds/hit_blue.wav"),
    "target_hit_red": pygame.mixer.Sound("sounds/hit_red.wav"),
    "game_start": pygame.mixer.Sound("sounds/start.ogg"),
    "game_end": pygame.mixer.Sound("sounds/end.ogg"),
    "button_click": pygame.mixer.Sound("sounds/click.wav"),
}

sounds["arrow_shot"].set_volume(0.2)      # Moderate volume for frequent shots
sounds["target_hit_blue"].set_volume(0.9)  # Higher volume for successful hits
sounds["target_hit_red"].set_volume(0.9)   # Highest volume for high-value targets
sounds["game_start"].set_volume(0.8)       # High volume for game start announcement
sounds["game_end"].set_volume(0.9)         # Very high volume for game end
sounds["button_click"].set_volume(0.6)     # Low volume for UI feedback

def safe_load_image(path, size=None):
    """Safely load and optionally resize an image."""
    image = pygame.image.load(path).convert_alpha()  #convert_alpha() converts the surface of the image to match the display surface

    transformed_image = pygame.transform.scale(image, size)

    return transformed_image


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


# Load game assets after display is initialized
load_game_assets()

archer_rect = archer_image.get_rect()
archer_rect.midbottom = (width//2, height)

play_button_rect = play_button_image.get_rect()
play_button_rect.center = (width // 2, (height // 2) + 125)


def setup_font():
    """Set up the game font."""
    global font

    font = pygame.font.Font('fonts/AlmendraSC-Regular.ttf', 36)

def show_countdown():

    for i in range(3,0,-1):  #3,2,1 - 0 is not included, and -1 represents how much it is decreasing by
        screen.blit(background_image, (0,0))
        text = font.render(str(i), True, (255,255,255))
            #True is telling that the edges need to be smoothed out

        screen.blit(text, (width // 2 - (text.get_width() // 2), height//2))
        pygame.display.flip()
        pygame.time.delay(800) # waiting 0.8 seconds between each presentation of the countdown

def load_personal_best():

    try:
        with open(SCORE_FILE, "r") as file:
            try:
                return int(file.read().strip()) #strip() removes any whitespaces
            
            except ValueError:
                return "Error"
            
    except (FileNotFoundError):
        return "None"

def save_personal_best(score):
    with open(SCORE_FILE, "w") as file:

        #when you are the writing file, it empties the file FIRST, and then it writes whatever you want to

        #write creates the new file automatically if its not there

        file.write(str(score))

personal_best = load_personal_best()

def show_play_screen(is_game_over):
    while True:

        screen.blit(background_image, (0,0))

        if is_game_over == True:
            game_over_text = font.render("Game Over! Your score is: {}".format(score), True, (255,255,255)) #font to be nicely merged into my background
            #makes my font look nice
            #white color is the color of the combination of (255,255,255)

            screen.blit(game_over_text, (width //2 - game_over_text.get_width() //2, height//2 -100))

            title = font.render("Personal Best: {}".format(personal_best), True, (255,255,255))
            screen.blit(title, (width //2 - title.get_width() // 2, height // 2 + 30))

        if is_game_over == False:
            screen.blit(main_menu_background_image, (0,0))
            title = font.render("Personal Best: {}".format(personal_best), True, (255,255,255))
            screen.blit(title, (width//2 - title.get_width() // 2, height//2+30))

        screen.blit(play_button_image, play_button_rect)

        pygame.display.flip()

        for event in pygame.event.get(): #pressing an arrow key, pressing a button, not holding down (single events not continuous)
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if play_button_rect.collidepoint(pygame.mouse.get_pos()):
                    sounds["button_click"].stop()
                    sounds["button_click"].play()
                    return


class Target:
    def __init__(self, image):
        self.image = image
        self.rect = image.get_rect()
        self.direction = random.choice(["left", "right"])
        self.rect.y = random.randint(165,450)

        if self.direction == "left":
            self.rect.right = width

        else:
            self.rect.left = 0

        self.speed = random.randint(1,8)

    def move(self):
        if self.direction == "left":
            self.rect.x -= self.speed

        else:
            self.rect.x += self.speed

    def draw(self, surface):
        surface.blit(self.image, self.rect)

    def is_off_screen(self):
        return self.rect.right < 0 or self.rect.left > width
    
start_time = time.time()

clock = pygame.time.Clock()

last_shot_time = 0


def run_game():
    global score, start_time, arrows, targets, cycles_until_new_target, game_running, personal_best, target_frequency, last_shot_time, arrow_cooldown #we need to declare these variables with the global keyword so we can edit them in the function


    score = 0
    arrows = []
    targets = []
    cycles_until_new_target = 0
    game_running = True
    target_frequency = 30
    arrow_cooldown = 0.5
    last_shot_time = 0

    show_countdown()

    sounds["game_start"].stop()
    sounds["game_start"].play()

    start_time = time.time()

    while game_running: #this our game loop

        for event in pygame.event.get():  #this line is sensing all the events (we will go more into this later)
            if event.type == pygame.QUIT:  #when the user closes the program
                pygame.quit() #stopping the loop
                sys.exit() #exiting the program

            if event.type == pygame.KEYDOWN:
                
                if event.key == pygame.K_SPACE:  #a space being pressed is a single event
                    current_time = time.time()

                    if current_time - last_shot_time >= arrow_cooldown:

                        new_arrow = arrow_image.get_rect()

                        new_arrow.center = archer_rect.center

                        arrows.append(new_arrow) #adding the new arrow created to the list

                        sounds["arrow_shot"].stop()
                        sounds["arrow_shot"].play()

                        last_shot_time = current_time

        #continuous event - holding the arrow key

        keys = pygame.key.get_pressed() #returns a list representing the state of all keys

        if (keys[pygame.K_LEFT] == True) and archer_rect.left > 0:
            archer_rect.x -= 10

        if (keys[pygame.K_RIGHT] == True) and archer_rect.right < width:
            archer_rect.x += 10

        for arrow in arrows[:]: #arrows[:] returns a copy of the list so no arrow are missed in the iteration
            arrow.y -= arrow_speed

            if arrow.bottom < 0:
                arrows.remove(arrow)

        if cycles_until_new_target >= target_frequency:
            new_target = Target(random.choice([blue_target_image, blue_target_image, red_target_image]))

            targets.append(new_target)

            cycles_until_new_target = 0
        
        else:
            cycles_until_new_target += 1

        for target in targets[:]: #targets[:] returns a copy of the list so no arrow are missed in the iteration
            target.move()

            if target.is_off_screen():
                targets.remove(target)

        for arrow in arrows[:]: #we are essentially taking in the copy of whatever arrows are on the screen right now
            for target in targets[:]:
                if arrow.colliderect(target.rect):
                    if target.image == blue_target_image:

                        score+=1

                        sounds["target_hit_blue"].stop()
                        sounds["target_hit_blue"].play()

                    if target.image == red_target_image:
                        score +=2

                        sounds["target_hit_red"].stop()
                        sounds["target_hit_red"].play()

                    arrows.remove(arrow)
                    targets.remove(target)
                    break
        

        screen.blit(background_image, (0,0))   #taking the top left of the background and putting it at the top left of the screen so it aligns whit the screen
        

        screen.blit(archer_image, archer_rect)

        for target in targets[:]:
            target.draw(screen)

        for arrow in arrows[:]:
            screen.blit(arrow_image, arrow)

        score_text = font.render("Score: {}".format(score), True, (255,255,255))

        #(255,255,255) represents a white color
        #True means that the font will blend in with the background of the screen making it more neat
        #.format() basically just a rip-off f-string but for rendering fonts, whatever goes in the brackets, is the parameter for format()

        screen.blit(score_text, (10,10))

        elapsed_time = int(time.time() - start_time)
        remaining_time = max(0, game_duration-elapsed_time) #will return the largest value among the arguments

        timer_text = font.render("Time: {}".format(remaining_time), True, (255,255,255))
        screen.blit(timer_text, (width - 150, 10)) #top right of our screen

        red_text = font.render("Red=2pts", True, (255,0,0)) #red color

        blue_text = font.render("Blue=1pt", True, (0,0,255)) #blue color


        screen.blit(red_text, (200, 10))
        screen.blit(blue_text, (400, 10))


        target_frequency -= 0.01

        target_frequency -= score*0.0003

        arrow_cooldown -= 0.0001

        if remaining_time <= 0:
            sounds["game_end"].stop()
            sounds["game_end"].play()

            game_running = False

        pygame.display.flip()

        clock.tick(25) #FPS

    if not personal_best == "None" and not personal_best == "Error":
        if score>personal_best:
            personal_best = score

    else:
        personal_best = score

    save_personal_best(personal_best)

setup_font()

show_play_screen(is_game_over=False)

while True:
    run_game()
    show_play_screen(is_game_over=True)