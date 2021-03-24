import pygame
import random
from pygame import *


class GameManager:
    def __init__(self):
        # Define constants
        self.SCREEN_WIDTH = 900
        self.SCREEN_HEIGHT = 700
        self.FPS = 120
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
        self.positions = []
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

        self.cursor_img = transform.scale(pygame.image.load("images/hammer.png"), (self.ZOMBIE_WIDTH, self.ZOMBIE_HEIGHT))

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
        # Set mouse visibiity to false
        pygame.mouse.set_visible(False)
        #Set cursor to hammer img
        self.cursor_img_rect = self.cursor_img.get_rect()
        # Sound effects
        self.soundEffect = SoundEffect()
        self.reset()

    def reset(self):

        # Generate hole positions
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
                    self.soundEffect.playHit()
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
            if self.misses > 10:
                self.endScreen()
                continue

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
                self.soundEffect.playPop()
                print(frame_num)
            mil = clock.tick(self.FPS)
            sec = mil / 1000.0
            cycle_time += sec
            pic = self.zombie[num]
            if cycle_time > interval:
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

            self.screen.blit(self.background, (0, 0))
            for position in self.hole_positions:
                self.screen.blit(self.img_hole, position)
            self.screen.blit(pic, (self.hole_positions[frame_num][0]+(self.HOLEWIDTH-self.ZOMBIE_WIDTH)/2,
                                       self.hole_positions[frame_num][1]+self.HOLEHEIGHT-self.ZOMBIE_HEIGHT*1.2))
            self.cursor_img_rect.midleft = pygame.mouse.get_pos()  # update position
            self.screen.blit(self.cursor_img, self.cursor_img_rect) # draw the cursor
            self.update()

            # Update the display
            pygame.display.flip()

    def endScreen(self):
        loop = True
        while loop:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    loop = False
                    pygame.quit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    loop = False
            self.screen.blit(self.background, (0,0))

            # Update the player's score
            current_score_string = "SCORE: " + str(self.score)
            score_text = self.font_obj.render(current_score_string, True, (255, 255, 255))
            score_text_pos = score_text.get_rect()
            score_text_pos.centerx = self.background.get_rect().centerx
            score_text_pos.centery = self.FONT_TOP_MARGIN*10
            self.screen.blit(score_text, score_text_pos)
            # Update the player's misses
            current_misses_string = "MISSES: " + str(self.misses)
            misses_text = self.font_obj.render(current_misses_string, True, (255, 255, 255))
            misses_text_pos = misses_text.get_rect()
            misses_text_pos.centerx = self.background.get_rect().centerx
            misses_text_pos.centery = self.FONT_TOP_MARGIN*12
            self.screen.blit(misses_text, misses_text_pos)
            # Update the player's level
            current_level_string = "LEVEL: " + str(self.level)
            level_text = self.font_obj.render(current_level_string, True, (255, 255, 255))
            level_text_pos = level_text.get_rect()
            level_text_pos.centerx = self.background.get_rect().centerx
            level_text_pos.centery = self.FONT_TOP_MARGIN*14
            self.screen.blit(level_text, level_text_pos)
            
            # Game Over string
            gameover_string = "GAME OVER"
            gameover_text = self.font_obj.render(gameover_string, True, (255, 255, 255))
            gameover_text_pos = gameover_text.get_rect()
            gameover_text_pos.centerx = self.background.get_rect().centerx
            gameover_text_pos.centery = self.FONT_TOP_MARGIN*5
            self.screen.blit(gameover_text, gameover_text_pos)


            # Continue string
            continue_string = "Press left mouse to restart..."
            continue_text = self.font_obj.render(continue_string, True, (255, 255, 255))
            continue_text_pos = continue_text.get_rect()
            continue_text_pos.centerx = self.background.get_rect().centerx
            continue_text_pos.centery = self.FONT_TOP_MARGIN*20
            self.screen.blit(continue_text, continue_text_pos)
        

            # Update the display
            pygame.display.flip()
        self.score = 0
        self.misses = 0
        self.level = 1
        




# The Debugger class - use this class for printing out debugging information



class SoundEffect:
    def __init__(self):
        self.mainTrack = pygame.mixer.music.load("sounds/themesong.wav")
        self.hitSound = pygame.mixer.Sound("sounds/hit.wav")
        self.hitSound.set_volume(5.0)
        self.popSound = pygame.mixer.Sound("sounds/pop.wav")
        self.hurtSound = pygame.mixer.Sound("sounds/hurt.wav")
        self.levelSound = pygame.mixer.Sound("sounds/point.wav")
        pygame.mixer.music.play(-1)

    def playHit(self):
        self.hitSound.play()

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
