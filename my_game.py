import pygame
import random
from enum import Enum
from os import path


img_dir = path.join(path.dirname(__file__), 'img')
snd_dir = path.join(path.dirname(__file__), 'snd')

WIDTH = 600
HEIGHT = 450
FPS = 60
TIME_PER_STEP = 1100
WOLF_POSITION = (200, 100)

WHITE = (255, 255, 255)
RED = (255, 0, 0)

pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("НУ, ПОГОДИ!")
font_name = pygame.font.match_font('times new roman')
clock = pygame.time.Clock()
background = pygame.image.load(path.join(img_dir, "start.png")).convert()
background_rect = background.get_rect()
background_end = pygame.image.load(path.join(img_dir, "game_over.png")).convert()
background_end_rect = background_end.get_rect()


def draw_text(surf, text, size, x, y, color=WHITE):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)


def start_screen():
    screen.blit(background, background_rect)
    draw_text(screen, "Нажмите любую клавишу для начала игры ", 25, WIDTH / 2, HEIGHT * 9 / 10, RED)
    pygame.display.flip()
    waiting = True
    while waiting:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYUP:
                waiting = False


def end_screen():
    screen.blit(background_end, background_end_rect)
    pygame.display.flip()
    waiting = True
    while waiting:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                waiting = False
            if event.type == pygame.KEYUP:
                waiting = False


def catch_egg(egg, wolf_is_left, hands_is_up):
    if egg.egg_location == EggLocation.LEFT_UP:
        return wolf_is_left and hands_is_up
    elif egg.egg_location == EggLocation.LEFT_DOWN:
        return wolf_is_left and not hands_is_up
    elif egg.egg_location == EggLocation.RIGHT_UP:
        return not wolf_is_left and hands_is_up
    else:
        return not wolf_is_left and not hands_is_up


class Wolf(pygame.sprite.Sprite):
    def __init__(self, wolf_position):
        pygame.sprite.Sprite.__init__(self)
        self.wolf_left = pygame.image.load('img/wolf_left.png')
        self.wolf_right = pygame.image.load('img/wolf_right.png')
        self.hand_down_left = pygame.image.load('img/hands/hand_down_left.png')
        self.hand_down_right = pygame.image.load('img/hands/hand_down_right.png')
        self.hand_up_left = pygame.image.load('img/hands/hand_up_left.png')
        self.hand_up_right = pygame.image.load('img/hands/hand_up_right.png')
        self.shield = 100
        self.wolf_position = wolf_position
        self.hands_position = (0, 0)

    def draw(self, screen_wolf, left, up):
        if left:
            screen_wolf.blit(self.wolf_left, self.wolf_position)
            if up:
                screen_wolf.blit(self.hand_up_left, self.hands_position)
            else:
                screen_wolf.blit(self.hand_down_left, self.hands_position)
        else:
            screen_wolf.blit(self.wolf_right, self.wolf_position)
            if up:
                screen_wolf.blit(self.hand_up_right, self.hands_position)
            else:
                screen_wolf.blit(self.hand_down_right, self.hands_position)


LEFT_UP_POSITIONS = [(60, 120), (75, 130), (90, 140), (115, 150), (135, 165)]
LEFT_DOWN_POSITIONS = [(60, 260), (75, 265), (90, 275), (110, 285), (125, 295)]
RIGHT_UP_POSITIONS = [(520, 120), (510, 125), (495, 135), (475, 150), (455, 165)]
RIGHT_DOWN_POSITIONS = [(520, 260), (510, 265), (495, 270), (475, 285), (455, 295)]
EGG_POSITIONS = [LEFT_UP_POSITIONS, LEFT_DOWN_POSITIONS, RIGHT_UP_POSITIONS, RIGHT_DOWN_POSITIONS]


class EggLocation(Enum):
    LEFT_UP = 0
    LEFT_DOWN = 1
    RIGHT_UP = 2
    RIGHT_DOWN = 3


class Egg(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('img/egg.png')
        self.egg_location = EggLocation(random.randint(0, len(EGG_POSITIONS)-1))
        self.positions = EGG_POSITIONS[self.egg_location.value]
        self.index = 0
        egg_sound.play()

    def update(self):
        self.index += 1
        return self.index >= len(self.positions)

    def draw(self, screen_egg):
        draw_index = self.index
        if draw_index >= len(self.positions):
            draw_index = len(self.positions)-1
        screen_egg.blit(self.image, self.positions[draw_index])


wolf = Wolf(WOLF_POSITION)
wolf_is_left = True
hands_is_up = True
background_1 = pygame.image.load("img/chicken_house.png")
background_2 = pygame.image.load("img/chickens.png")
egg_sound = pygame.mixer.Sound(path.join(snd_dir, 'sounds_move_egg.wav'))
pygame.mixer.music.set_volume(0.3)


eggs = []
time = 0
timer = pygame.time.Clock()
score = 0

start = True
running = True

while running:
    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_LEFT:
            wolf_is_left = True
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RIGHT:
            wolf_is_left = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_UP:
            hands_is_up = True
        if event.type == pygame.KEYDOWN and event.key == pygame.K_DOWN:
            hands_is_up = False
    if running:
        time += timer.get_time()
    if time > TIME_PER_STEP:
        time = 0
        shift = False
        for egg in eggs:
            should_catch = egg.update()
            if should_catch:
                if catch_egg(egg, wolf_is_left, hands_is_up):
                    score = score + 1
                    egg_sound = pygame.mixer.Sound(path.join(snd_dir, 'sounds_catch.wav'))
                    shift = True
                else:
                    running = False
        if shift:
            eggs.pop(0)
        eggs.append(Egg())

    for egg in eggs:
        egg.draw(screen)

    pygame.display.update()

    if running:
        timer.tick(60)

    if start:
        start_screen()
        start = False
        score = 0

    if running is False:
        game_over = True
        if game_over:
            end_screen()
            game_over = False

    screen.blit(background_1, (0, 0))
    screen.blit(background_2, (0, 0))
    wolf.draw(screen, wolf_is_left, hands_is_up)
    draw_text(screen, str(score), 25, WIDTH / 1.3, 10)
    pygame.display.flip()

pygame.quit()