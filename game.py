import pygame
import cv2
import random
import os
import sys

if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
else:
    base_path = os.path.dirname(__file__)

pygame.init()

highscore_file = "highscore.txt"
if os.path.exists(highscore_file):
    with open(highscore_file, "r") as file:
        highscore = int(file.read().strip())
else:
    highscore = 0

font_path = os.path.join(base_path, "retro_font.ttf")
score_font = pygame.font.Font(font_path, 20)
highscore_num = score_font.render(f'Highscore: {highscore}', True, (255, 255, 0))

screen_width = 1024
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height), pygame.SCALED | pygame.DOUBLEBUF, vsync=1)


x, y = 300, 275

pygame.mixer.init()

bg_music_path = os.path.join(base_path, "lighthouse bg music.mp3")
pygame.mixer.music.load(bg_music_path)
pygame.mixer.music.set_volume(0.25)
pygame.mixer.music.play(-1)
music_start_time = pygame.time.get_ticks()

jump_sound_path = os.path.join(base_path, "jump arcade.mp3")
jump_sound = pygame.mixer.Sound(jump_sound_path)
jump_sound.set_volume(0.05)

gameover_sound_path = os.path.join(base_path, "game-over.mp3")
gameover_sound = pygame.mixer.Sound(gameover_sound_path)
gameover_sound.set_volume(1)

bird_wup_path = os.path.join(base_path, "bird_image_wup.png")
bird_image_flapup = pygame.image.load(bird_wup_path)
bird_image_flapup = pygame.transform.scale(bird_image_flapup, (60, 55)).convert_alpha()
bird_wdown_path = os.path.join(base_path, "bird_image_wdown.png")
bird_image_flapdown = pygame.image.load(bird_wdown_path)
bird_image_flapdown = pygame.transform.scale(bird_image_flapdown, (60, 55)).convert_alpha()
bird_image_death_path = os.path.join(base_path, "bird_image_death.png")
bird_image_dead = pygame.image.load(bird_image_death_path).convert_alpha()
bird_image_dead = pygame.transform.scale(bird_image_dead, (60, 55)).convert_alpha()

pipe_width = 315
pipe_height = 600
pipe_top_path = os.path.join(base_path, "redpipe up.png")
pipe_top_img = pygame.image.load(pipe_top_path)
pipe_top_img = pygame.transform.scale(pipe_top_img, (pipe_width, pipe_height)).convert_alpha()
pipe_bottom_path = os.path.join(base_path, "redpipe down.png")
pipe_bottom_img = pygame.image.load(pipe_bottom_path)
pipe_bottom_img = pygame.transform.scale(pipe_bottom_img, (pipe_width, pipe_height)).convert_alpha()

font = pygame.font.Font("retro_font.ttf", 26)

video = cv2.VideoCapture("synth light.webm")

score = 0
start = False


class Bird:
    def __init__(self, x, y):

        self.x = x
        self.y = y
        self.speed = 0
        self.gravity = 0.5
        self.flap = -10
        self.max_fall_speed = 10
        self.life = True
        self.image = bird_image_flapup
        self.flap_timer = 0

    def jump(self):

        self.speed = self.flap
        self.image = bird_image_flapdown
        self.flap_timer = 12
        jump_sound.play()

    def update(self):

        if not self.life:
            return

        self.speed += self.gravity

        if self.speed > self.max_fall_speed:
            self.speed = self.max_fall_speed

        self.y += self.speed

        if self.y < 0:
            self.y = 0
            self.speed = 0

        if self.y >= screen_height - self.image.get_height():
            self.y = screen_height - self.image.get_height()
            self.life = False
            bird.death()

        if self.flap_timer > 0:
            self.flap_timer -= 1
            if self.flap_timer == 0:
                self.image = bird_image_flapup

    def draw(self):

        if not self.life:
            self.image = bird_image_dead
        screen.blit(self.image, (self.x, self.y))

    def death(self):

        global highscore, highscore_num

        scoreflag = False
        if score > highscore:
            scoreflag = True
            highscore = score
            with open(highscore_file, "w") as file:
                file.write(str(highscore))

        highscore_num = score_font.render(f'Highscore: {highscore}', True, (255, 255, 0))

        self.image = bird_image_dead
        screen.blit(self.image, (self.x, self.y))

        for pipe in pipes:
            pipe.draw()

        gameover_font = pygame.font.Font(font_path, 45)
        sub_font = pygame.font.Font(font_path, 15)

        end_text = gameover_font.render("***** GAME OVER *****", True, (255, 255, 0))
        sub_text = sub_font.render("Press SPACE to restart.", True, (255, 255, 0))

        screen.blit(end_text, (screen_width // 2 - end_text.get_width() // 2, 250))
        screen.blit(sub_text, (screen_width // 2 - sub_text.get_width() // 2, 500))
        screen.blit(highscore_num, (25, 30))
        screen.blit(score_num, (25, 70))

        if scoreflag:
            highscore_font = pygame.font.Font(font_path, 25)
            highscore_text = highscore_font.render('!!NEW HIGHSCORE!!', True, (255, 255, 0))
            screen.blit(highscore_text, (screen_width // 2 - highscore_text.get_width() // 2, 400))

        gameover_sound.play()

        pygame.display.flip()
        pygame.time.wait(1000)

        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    restart_game()
                    waiting = False

    def restart(self):

        for alpha in range(0, 256, 5):
            fade_surface = pygame.Surface((screen_width, screen_height))
            fade_surface.fill((0, 0, 0))
            fade_surface.set_alpha(alpha)
            screen.blit(fade_surface, (0, 0))
            pygame.display.flip()
            pygame.time.delay(10)

        self.x = 300
        self.y = 275
        self.speed = 0
        self.life = True
        self.image = bird_image_flapup


def restart_game():
    global pipes, score, start
    bird.restart()
    pipes = [Pipe(screen_width + i * 300, random.randint(5, 400), 200, 4) for i in range(3)]
    score = 0
    start = False


class Pipe:
    def __init__(self, x, gap_y, gap_size, speed):

        self.x = x
        self.gap_y = gap_y
        self.gap_size = gap_size
        self.image_width = 300
        self.width = 80
        self.height = 400
        self.speed = speed
        self.passed = False

    def update(self):

        if start:
            self.x -= self.speed
            if self.x + self.width < 0:
                self.x = screen_width
                self.gap_y = random.randint(150, screen_height - 200)
                self.passed = False

    def draw(self):

        screen.blit(pipe_top_img, (self.x - self.width-8, self.gap_y - self.height-135))
        screen.blit(pipe_bottom_img, (self.x - self.width-8, self.gap_y + self.gap_size-191))

        # THIS IS FOR DEBUGGING PLEASE DON'T TOUCH
        '''collision_top = pygame.Rect(self.x, self.gap_y - self.height, self.width, self.height)
        collision_bottom = pygame.Rect(self.x, self.gap_y + self.gap_size, self.width, self.height)
        pygame.draw.rect(screen, (0, 255, 0), collision_top, 2)
        pygame.draw.rect(screen, (0, 255, 0), collision_bottom, 2)'''

    def check_collision(self, bird):

        buffer = 3
        if bird.x + bird.image.get_width() - buffer > self.x and bird.x + buffer < self.x + self.width:
            if bird.y + buffer < self.gap_y or bird.y + bird.image.get_height() - buffer > self.gap_y + self.gap_size:
                return True
        return False


pipes = [Pipe(screen_width + i * 300, random.randint(5, 400), 200, 4) for i in range(3)]
bird = Bird(x, y)

running = True

clock = pygame.time.Clock()

while running:

    ret, frame = video.read()
    if not ret:
        video.set(cv2.CAP_PROP_POS_FRAMES, 0)
        ret, frame = video.read()

    frame = cv2.resize(frame, (screen_width, screen_height))
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
    screen.blit(frame, (0, 0))

    if pygame.time.get_ticks() - music_start_time >= 39000:
        pygame.mixer.music.stop()
        pygame.mixer.music.play()
        music_start_time = pygame.time.get_ticks()

    score_num = score_font.render(f'Score: {score}', True, (255, 255, 0))

    if not start:
        text = font.render("Press SPACE or UP arrow to start!", True, (255, 255, 0))
        screen.blit(text, (screen_width // 2 - text.get_width() // 2, 150))

    else:
        bird.update()

    bird.draw()

    if not bird.life:
        bird.death()
        continue

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_SPACE, pygame.K_UP):
                bird.jump()
                start = True

    if start and bird.life:

        for pipe in pipes:
            pipe.update()
            pipe.draw()

            if pipe.check_collision(bird):
                bird.life = False

            if not pipe.passed and pipe.x + pipe.width < bird.x:
                pipe.passed = True
                score += 1
    else:
        for pipe in pipes:
            pipe.draw()

    screen.blit(highscore_num, (25, 30))
    screen.blit(score_num, (25, 70))


    pygame.display.flip()
    clock.tick(90)

pygame.quit()
