import pygame
import random
from pygame import *


class GameManager:
    def __init__(self):
        # Define constants
        self.SCREEN_WIDTH = 900
        self.SCREEN_HEIGHT = 700
        self.FPS = 60
        self.HOLEROWS = 5  # !!
        self.HOLECOLUMNS = 3  # !!
        self.HOLEWIDTH = 100
        self.HOLEHEIGHT = int(self.HOLEWIDTH * (3 / 8))
        self.ZOMBIE_WIDTH =int( self.HOLEWIDTH*(7/8) )
        self.ZOMBIE_HEIGHT = self.ZOMBIE_WIDTH
        self.FONT_SIZE = 31
        self.FONT_TOP_MARGIN = 26
        self.LEVEL_SCORE_GAP = 4
        self.LEFT_MOUSE_BUTTON = 1
        self.GAME_TITLE = "Whack A Mole - Game Programming - Assignment 1"
        # Initialize player's score, number of missed hits and level
        self.score = 0
        self.misses = 0
        self.level = 1
        # Initialize screen
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        pygame.display.set_caption(self.GAME_TITLE)
        self.background = transform.scale(pygame.image.load("images/background.png"), (self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        self.img_hole = transform.scale(pygame.image.load("images/hole.png"), (self.HOLEWIDTH, self.HOLEHEIGHT))

        # Font object for displaying text
        self.font_obj = pygame.font.Font('./fonts/GROBOLD.ttf', self.FONT_SIZE)
        # Initialize the zombie's sprite sheet
        # 6 different states
        sprite_sheet = pygame.image.load("images/zombie.png")
        zombie = pygame.image.load("images/zombie.png")
        zombie_hit = pygame.image.load("images/zombie_hit.png")
        zombie = transform.scale(zombie, (self.ZOMBIE_WIDTH, self.ZOMBIE_HEIGHT))
        zombie_hit = transform.scale(zombie_hit, (self.ZOMBIE_WIDTH, self.ZOMBIE_HEIGHT))
        self.zombie = []
        self.zombie.append(zombie)
        self.zombie.append(zombie_hit)
        # Positions of the holes in background
        self.hole_positions = []
        # Init debugger
        self.debugger = Debugger("debug")
        # Sound effects
        self.soundEffect = SoundEffect()
        self.reset()

    def reset(self):

        # Generate hole positions
        self.holes = []
        self.used_holes = []
        base_row = (self.SCREEN_HEIGHT - self.FONT_TOP_MARGIN*3) / self.HOLEROWS
        base_column = self.SCREEN_WIDTH / self.HOLECOLUMNS
        for row in range(self.HOLEROWS):
            rowY = base_row * row
            rowY += (base_row - self.HOLEHEIGHT) / 2 + self.FONT_TOP_MARGIN*3
            for column in range(self.HOLECOLUMNS):
                thisX = base_column * column
                thisX += (base_column - self.HOLEWIDTH) / 2
                self.hole_positions.append((int(thisX), int(rowY)))


        # Indicates whether the HUD indicators should be displayed
        self.score = 0
        self.misses = 0


    # Calculate the player level according to his current score & the LEVEL_SCORE_GAP constant
    def get_player_level(self):
        newLevel = 1 + int(self.score / self.LEVEL_SCORE_GAP)
        if newLevel != self.level:
            # if player get a new level play this sound
            self.soundEffect.playLevelUp()
        return 1 + int(self.score / self.LEVEL_SCORE_GAP)

    # Get the new duration between the time the zombie pop up and down the holes
    # It's in inverse ratio to the player's current level
    def get_interval_by_level(self, initial_interval):
        new_interval = initial_interval - self.level * 0.15
        if new_interval > 0:
            return new_interval
        else:
            return 0.05

    # Check whether the mouse click hit the zombie or not
    def is_zombie_hit(self, mouse_position, current_hole_position):
        mouse_x = mouse_position[0]
        mouse_y = mouse_position[1]
        current_hole_x = current_hole_position[0] + (self.HOLEWIDTH-self.ZOMBIE_WIDTH)/2
        current_hole_y = current_hole_position[1]+self.HOLEHEIGHT-self.ZOMBIE_HEIGHT*1.2
        if (mouse_x > current_hole_x) \
                and (mouse_x < current_hole_x + self.ZOMBIE_WIDTH) \
                and (mouse_y > current_hole_y) \
                and (mouse_y < current_hole_y + self.ZOMBIE_HEIGHT):
            return True
        else:
            return False

    # Update the game states, re-calculate the player's score, misses, level
    def update(self):
        # Update the player's score
        current_score_string = "SCORE: " + str(self.score)
        score_text = self.font_obj.render(current_score_string, True, (255, 255, 255))
        score_text_pos = score_text.get_rect()
        score_text_pos.centerx = self.background.get_rect().centerx
        score_text_pos.centery = self.FONT_TOP_MARGIN
        self.screen.blit(score_text, score_text_pos)
        # Update the player's misses
        current_misses_string = "MISSES: " + str(self.misses)
        misses_text = self.font_obj.render(current_misses_string, True, (255, 255, 255))
        misses_text_pos = misses_text.get_rect()
        misses_text_pos.centerx = self.SCREEN_WIDTH / 5 * 4
        misses_text_pos.centery = self.FONT_TOP_MARGIN
        self.screen.blit(misses_text, misses_text_pos)
        # Update the player's level
        current_level_string = "LEVEL: " + str(self.level)
        level_text = self.font_obj.render(current_level_string, True, (255, 255, 255))
        level_text_pos = level_text.get_rect()
        level_text_pos.centerx = self.SCREEN_WIDTH / 5 * 1
        level_text_pos.centery = self.FONT_TOP_MARGIN
        self.screen.blit(level_text, level_text_pos)

    # Start the game's main loop
    # Contains some logic for handling animations, zombie hit events, etc..
    def start(self):
        cycle_time = 0
        num = -1
        loop = True
        is_down = False
        interval = 1
        initial_interval = 1
        hit_interval = 0.2
        hit_loop = 0
        frame_num = 0
        # Time control variables
        clock = pygame.time.Clock()

        for i in range(len(self.zombie)):
            self.zombie[i].set_colorkey((0, 0, 0))
            self.zombie[i] = self.zombie[i].convert_alpha()

        while loop:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    loop = False
                if event.type == MOUSEBUTTONDOWN and event.button == self.LEFT_MOUSE_BUTTON:
                    self.soundEffect.playFire()
                    if self.is_zombie_hit(mouse.get_pos(), self.hole_positions[frame_num]) and num > -1 and hit_loop == 0:
                        num = 1
                        is_down = False
                        interval = 0
                        hit_loop = 1
                        self.score += 1  # Increase player's score
                        self.level = self.get_player_level()  # Calculate player's level
                        # Stop popping sound effect
                        self.soundEffect.stopPop()
                        # Play hurt sound
                        self.soundEffect.playHurt()
                        self.update()
                    else:
                        self.misses += 1
                        self.update()

            if num > 1:
                self.screen.blit(self.background, (0, 0))
                for position in self.hole_positions:
                    self.screen.blit(self.img_hole, position)
                self.update()
                num = -1
            if num == -1 and (hit_loop > 2 or hit_loop == 0):
                hit_loop = 0
                self.screen.blit(self.background, (0, 0))
                for position in self.hole_positions:
                    self.screen.blit(self.img_hole, position)
                self.update()
                num = 0
                is_down = False
                interval = 0.5
                frame_num = random.randint(0, self.HOLEROWS*self.HOLECOLUMNS-1)

            mil = clock.tick(self.FPS)
            sec = mil / 1000.0
            cycle_time += sec
            if cycle_time > interval:
                pic = self.zombie[num]
                self.screen.blit(self.background, (0, 0))
                for position in self.hole_positions:
                    self.screen.blit(self.img_hole, position)
                self.screen.blit(pic, (self.hole_positions[frame_num][0]+(self.HOLEWIDTH-self.ZOMBIE_WIDTH)/2,
                                       self.hole_positions[frame_num][1]+self.HOLEHEIGHT-self.ZOMBIE_HEIGHT*1.2))
                self.update()
                if hit_loop ==0:
                    if is_down is False:
                        num += 1
                    else:
                        num -= 1
                    if num == 1:
                        self.soundEffect.playPop()
                if num == 1:
                    num -= 1
                    if hit_loop > 2:
                        num = -1
                        hit_loop = 0
                    if hit_loop > 0:
                        interval = hit_interval
                        num = 1
                        hit_loop += 1
                    else:
                        interval = self.get_interval_by_level(initial_interval)  # get the newly decreased interval value
                    is_down = True

                else:
                    interval = 0.5
                cycle_time = 0
            # Update the display
            pygame.display.flip()


# The Debugger class - use this class for printing out debugging information
class Debugger:
    def __init__(self, mode):
        self.mode = mode

    def log(self, message):
        if self.mode is "debug":
            print("> DEBUG: " + str(message))


class SoundEffect:
    def __init__(self):
        self.mainTrack = pygame.mixer.music.load("sounds/themesong.wav")
        self.fireSound = pygame.mixer.Sound("sounds/fire.wav")
        self.fireSound.set_volume(1.0)
        self.popSound = pygame.mixer.Sound("sounds/pop.wav")
        self.hurtSound = pygame.mixer.Sound("sounds/hurt.wav")
        self.levelSound = pygame.mixer.Sound("sounds/point.wav")
        pygame.mixer.music.play(-1)

    def playFire(self):
        self.fireSound.play()

    def stopFire(self):
        self.fireSound.sop()

    def playPop(self):
        self.popSound.play()

    def stopPop(self):
        self.popSound.stop()

    def playHurt(self):
        self.hurtSound.play()

    def stopHurt(self):
        self.hurtSound.stop()

    def playLevelUp(self):
        self.levelSound.play()

    def stopLevelUp(self):
        self.levelSound.stop()

###############################################################
# Initialize the game
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
pygame.init()

# Run the main loop
my_game = GameManager()
my_game.start()
# Exit the game if the main loop ends
pygame.quit()
