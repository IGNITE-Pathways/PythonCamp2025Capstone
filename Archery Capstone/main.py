import sys
import pygame
from pygame.locals import QUIT
import time
import random

pygame.init()

width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('Archery!')

arrow_image_loaded = pygame.image.load('sprites/arrow.bmp')
arrow_image = pygame.transform.scale(arrow_image_loaded, (50, 50))

greenarrow_image_loaded = pygame.image.load('sprites/greenarrow.png')
greenarrow_image = pygame.transform.scale(greenarrow_image_loaded, (200, 200))

target_image_loaded = pygame.image.load('sprites/blue_target.png')
blue_target_image = pygame.transform.scale(target_image_loaded, (65, 65))

target_image_loaded2 = pygame.image.load('sprites/red_target.png')
red_target_image = pygame.transform.scale(target_image_loaded2, (65, 65))

play_button_image_loaded = pygame.image.load('sprites/play_button.bmp')
play_button_image = pygame.transform.scale(play_button_image_loaded, (200, 100))
play_button_rect = play_button_image.get_rect()
play_button_rect.center = (width // 2, (height // 2)+125)

main_menu_background_image_loaded = pygame.image.load('sprites/main_menu.bmp') 
main_menu_background_image = pygame.transform.scale(main_menu_background_image_loaded, (800, 600))


background_image_loaded = pygame.image.load('sprites/sunset.png') #this background is big enough so it doesn't need to be resized
background_image = pygame.transform.scale(background_image_loaded, (800, 600))


archer_rect = greenarrow_image.get_rect(
)  #only creates and stores the position/size of the rectangle, doesn't draw it
archer_rect.center = (width // 2, height - 80)

arrows = []  # Each item will be a Rect for an active arrow

arrow_speed = 30

game_duration = 60  # game will end after 120 seconds

targets = []
target_speed = 5
target_frequency = 30  #controls how often a new target appears, 25 represents every 25 ticks of the game loop
cycles_until_new_target = 0  #counts until a new target needs to be created

arrow_cooldown = 0.5  # how much time must pass before another arrow can be fired
last_shot_time = 0  # time of the last arrow fired

personal_best = 0

font = pygame.font.Font(None, 36) #None means we are using the default system font, we could use a custom font with a .ttf file if we wanted
#.Font(None,36) shows that we are creating a font object from the class of Font which can be rendered

SCORE_FILE = "personal_best.txt"

def load_personal_best():
    try:
        with open(SCORE_FILE, "r") as f: #"r" means reading the file, as f gives the opened file a classification/name, and we can use f to refer to that file
            #with helps execute safe resource management by opening the file, excecuting the code block, then closing the file safely
            try:
                return int(f.read().strip())  # Read score from file
            #.read() often create an invisible new line at the end of the file content
            #.strip() removes any whitespaces/new lines allowing for a clean input
            except ValueError:
                return "Error"  # Return "Invalid Content" if file contents are invalid
    except (FileNotFoundError):
        return "None"

def save_personal_best(score):
    with open(SCORE_FILE, "w") as f: #"w" is telling Python that I intend to write in the file
        #"w" automatically creates the file if it doesn't exist
        #"w" causes the file the empty all its contents, meaning that whatever we write will "overwrite" the previous content of the file (the best score)
        f.write(str(score))

personal_best = load_personal_best()

def show_play_screen(is_game_over):
    while True:

        screen.blit(background_image, (0, 0))  # Clear the screen every frame, so the text doesn't topple on top of each other causing blurry/bolded text

        if is_game_over:

            game_over_text = font.render("Game Over! Your score is: {}".format(score), True, (255, 255, 255)) #True is representing that edges will be smoothed to the background so it looks less pixelated and jagged, but it takes a smidge more time!
            screen.blit(game_over_text, (width // 2 - game_over_text.get_width() // 2, height // 2 - 100))


            # Drawing the personal best score
            title = font.render("Personal Best: {}".format(personal_best), True, (255, 255, 255))
            screen.blit(title, (width // 2 - title.get_width() // 2, height // 2 + 30))

        if is_game_over == False:
            screen.blit(main_menu_background_image, (0, 0)) 

            title = font.render("Personal Best: {}".format(personal_best), True, (255, 255, 255))
            screen.blit(title, (width // 2 - title.get_width() // 2, height // 2 + 30))



        # Drawing the play button no matter if its the beginning of program or end of a game
        screen.blit(play_button_image, play_button_rect)


        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if play_button_rect.collidepoint(pygame.mouse.get_pos()):
                    return  # exit screen to start a new game


class Target:

    def __init__(self, image):
        self.image = image
        self.rect = image.get_rect()
        self.direction = random.choice(["left", "right"])

        self.rect.y = random.randint(
            165, 450
        )  # targets appear at random y positions around the top of the screen
        #.x and .y are properties that represent the top left corner of the rectangle

        if self.direction == "left":
            self.rect.right = width  # targets starts from the right edge
        else:
            self.rect.left = 0  # target starts from the left edge

        self.speed = random.randint(1,8)

    def move(self):
        if self.direction == "left":
            self.rect.x -= self.speed
        else:
            self.rect.x += self.speed

    def draw(self, surface):
        surface.blit(self.image, self.rect)

    def is_off_screen(self, screen_width):
        return self.rect.right < 0 or self.rect.left > screen_width


score = 0

start_time = time.time() #this is used for the timer

clock = pygame.time.Clock(
)  #creates a clock object that can be used to control the frame rate of the game

game_running = True

def run_game():

    #resetting the variables every game round because we want to completely replicate a new round
    global score, start_time, arrows, targets, cycles_until_new_target, game_running, personal_best, target_frequency, last_shot_time, arrow_cooldown #we need to declare these variables with the global keyword so we can edit them in the function

    score = 0
    start_time = time.time()
    arrows = []
    targets = []
    cycles_until_new_target = 0
    game_running = True
    global personal_best #we need to declare personal_best with the global keyword for we can modify the variable inside the game loop if the user beats their personal score


    while game_running:  #game loop

        for event in pygame.event.get():  # this for loop senses for one-time events/triggers like user pressing space or exiting the window, not continous events like holding down right or left arrow key in this game's context

            if event.type == QUIT:
                pygame.quit()
                sys.exit()
                

            elif event.type == pygame.KEYDOWN:

                if event.key == pygame.K_SPACE:
                    # Fire an arrow
                    current_time = time.time(
                    )  # Get the current time to compare with the last shot time to see if enough time has passed to fire another arrow

                    if current_time - last_shot_time >= arrow_cooldown:  # Check if enough time has passed since the last shot in order to fire another arrow
                        new_arrow = arrow_image.get_rect(
                        )  #this does the cloning magic - a new instance of pygame.Rect is created for each arrow
                        new_arrow.center = archer_rect.center
                        # Fire from archer's position
                        arrows.append(
                            new_arrow
                        )  # Add the new arrow to the list of active arrows

                        last_shot_time = current_time  # update last shot time

        keys = pygame.key.get_pressed(
        )  # returns a list representing the state of all keys
        if keys[pygame.K_LEFT] and archer_rect.left > 0:  #we use the named constants such as K_LEFT instead of indices, to get the item from the list (special for pygame), basically it represents a "number under the hood"
            #this makes sure the archer doesn't go off the screen when left arrow is pressed'''
            archer_rect.x -= 10

        if keys[pygame.K_RIGHT] and archer_rect.right < width:
            archer_rect.x += 10  #you are modifying a property of an global object, not a global variable so you don't need to use the global keyword

        #when the arrow is fired, it moves up the screen, and this happens immediately when the space bar is pressed
        for arrow in arrows[:]:  # the [:] creates a copy of the list so no arrows are missed during iteration
            arrow.y -= arrow_speed
            if arrow.bottom < 0:
                arrows.remove(arrow)

        if cycles_until_new_target >= target_frequency:  #checks if its time to create a new target
            #code for creating a new target
            new_target = Target(random.choice([blue_target_image, blue_target_image, red_target_image]))  # creates a new target
            targets.append(new_target)  # and adds it to the list of targets
            cycles_until_new_target = 0
        else:
            cycles_until_new_target += 1  #incrementing the counter each game loop cycle

        for target in targets[:]:
            target.move()  #moving the target across the screen
            if target.is_off_screen(width):
                targets.remove(target)  #target gets removed from the list when it goes off the screen, meaning that it will no longer be drawn

        for arrow in arrows[:]:  # the [:] creates a copy of the list so no arrows are missed during iteration
            for target in targets[:]:
                if arrow.colliderect(target.rect):  #we are accessing the rect property of the target object, which is a pygame.Rect object, and calling the colliderect() method on it
                    # this is because the colliderect() method is a method of the pygame.Rect class
                    # and we are calling it on the arrow, which is also a pygame.Rect object
                    if target.image == blue_target_image:

                        score += 1

                    if target.image == red_target_image:
                        score += 2

                    arrows.remove(arrow)
                    targets.remove(target)
                    break  # Break out of target loop once collision is handled, moves on to the next arrow in the list

        #draw the background
        #.blit is a method that takes in an image and the top left position of that image and puts it on the destination surface

        #background
        screen.blit(background_image, (0, 0))

        #other things
        screen.blit(greenarrow_image, archer_rect)

        for target in targets:
            target.draw(
                screen
            )  #this is the method we defined in the Target class where we draw the target on the screen

        for arrow in arrows:
            screen.blit(arrow_image, arrow)

        score_text = font.render("Score: {}".format(score), True, (255, 255, 255))
        #.render() is a method that takes in the text to be rendered and the color of the text and returns a surface object that can be blitted to the screen

        #.format() is a method that is applied to the string and returns a new string with the placeholders {} replaced with the values passed in as arguments. It converts the arguments into strings and inserts them into the string.

        screen.blit(score_text, (10, 10))


        # Calculate remaining time
        elapsed_time = int(time.time() - start_time)
        remaining_time = max(0, game_duration - elapsed_time) #game_duration - elapsed_time represents the time passed since the game started
        # max() method returns the largest value among the arguments you give it, thus our remaining time can never go under 0, keeping everything in the game clean

        timer_text = font.render("Time: {}".format(remaining_time), True, (255, 255, 255))
        screen.blit(timer_text, (width - 150, 10))  # top-right corner

        target_frequency -= 0.01  #increases the frequency of targets as the game goes on, making it harder
        target_frequency -= score*0.0003

        arrow_cooldown -= 0.0001 #slowly as the game approaches an end, the user can start shooting arrows more faster

        # End game if timer is over
        if remaining_time <= 0:
            game_running = False


        pygame.display.flip()
        #updates the ENTIRE screen vs just a portion which is what .update() does

        clock.tick(25)  #limits the game loop to 25 frames per second, so the game doesn't run too fast

    if not personal_best == "None" and not personal_best == "Error": #it will be "None" only if it is the users first time opening the program, and invalid content only if the user opens the file and edits it
        if score > personal_best: #when the game is over, if the user has beaten their personal best score, their current score will become their personal best
            personal_best = score #to modify personal best, this is why we used the global keyword at the beginning of this function
    else:
        personal_best = score

    save_personal_best(personal_best)

show_play_screen(is_game_over=False)  # only show the main menu once at the start

while True: #program running
    run_game()  # run game
    show_play_screen(is_game_over=True)
