# https://www.youtube.com/watch?v=GiUGVOqqCKg&list=PLjcN1EyupaQkz5Olxzwvo1OzDNaNLGWoJ&index=1


import pygame
import random


pygame.init()

screen_w = 800
screen_h = 768
screen = pygame.display.set_mode((screen_w, screen_h))
clock = pygame.time.Clock()
fps = 60

# define font
font = pygame.font.SysFont('Bauhaus 93', 60)

# colors
white = (255, 255, 255)

# define game variables
ground_scroll = 0
scroll_speed = 2
flying = False
game_over = False
pipe_gap = 200
pipe_frequency = random.randint(1500, 1800) # milliseconds
last_pipe = pygame.time.get_ticks() - pipe_frequency
score = 0
pass_pipe = False

# load images
bg_image = pygame.image.load('img/bg.png')
ground_image = pygame.image.load('img/ground.png')
btn_image = pygame.image.load('img/restart.png')


def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))


def reset_game():
    pipe_group.empty()
    flappy.rect.x = 100
    flappy.rect.y = int(screen_h / 2)
    score = 0
    return score

class Bird(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()

        self.images = []
        self.index = 0
        self.counter = 0
        for num in range(1, 4):
            img = pygame.image.load(f'img/bird{num}.png')
            self.images.append(img)
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        # lugar onde o retangulo vai aparecer
        self.rect.center = (x, y)
        self.vel = 0
        self.clicked = False

    def update(self):

        # gravidade
        if flying == True:
            self.vel += 0.5
            if self.vel > 8:
                self.vel = 8
            if self.rect.bottom < 600:
                self.rect.y += int(self.vel)
        if game_over == False:
            # pulo
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                self.clicked = True
                self.vel = -10
            if pygame.mouse.get_pressed()[0] == 0:
                self.clicked = False
            
            # handle the animation
            self.counter += 1
            flap_cooldown = 5

            if self.counter > flap_cooldown:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images):
                    self.index = 0
            self.image = self.images[self.index]

            # rotate bird
            self.image = pygame.transform.rotate(self.images[self.index], self.vel * -2)
        else:
            self.image = pygame.transform.rotate(self.images[self.index], -90)

class Pipe(pygame.sprite.Sprite):
    def __init__(self, x, y, position):
        super().__init__()

        self.image = pygame.image.load('img/pipe.png')
        self.rect = self.image.get_rect()
        #position 1 is from the top, -1 from the bottom
        if position == 1:
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect.bottomleft = (x, y - int(pipe_gap / 2))
        if position == -1:
            self.rect.topleft = (x, y + int(pipe_gap / 2))

    def update(self):
        self.rect.x -= scroll_speed
        if self.rect.right < 0:
            self.kill()

class Button:
    def __init__(self, x, y, img):
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def draw(self):

        action = False

        # get mouse position
        pos =  pygame.mouse.get_pos()

        # check if mouse is over the button
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1:
                action = True

        # draw button
        screen.blit(self.image, (self.rect.x, self.rect.y))

        return action


bird_group = pygame.sprite.Group()
flappy = Bird(100, int(screen_h / 2))
bird_group.add(flappy) 

pipe_group = pygame.sprite.Group()

button = Button(screen_w // 2 - 50, screen_h // 2 - 100, btn_image)


running = True

# Game Loop
while running:

    clock.tick(fps)

    # draw background
    screen.blit(bg_image, (0, 0))

    bird_group.draw(screen)
    bird_group.update()
    pipe_group.draw(screen)
    

    # draw the ground
    screen.blit(ground_image, (ground_scroll, 600))

    # check the score
    if len(pipe_group) > 0:
        if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.left\
            and bird_group.sprites()[0].rect.right < pipe_group.sprites()[0].rect.right\
                and pass_pipe == False:
                pass_pipe = True
        if pass_pipe == True:
            if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.right:
                score += 1
                pass_pipe = False

    draw_text(str(score), font, white, int(screen_w / 2), 20)

    # look for collision
    if pygame.sprite.groupcollide(bird_group, pipe_group, False, False) or flappy.rect.top < 0:
        game_over = True


    # verifica se o passaro tocou o solo
    if flappy.rect.bottom >= 600:
        game_over = True
        flying = False

    if game_over == False and flying == True:

        # generate new pipes
        time_now = pygame.time.get_ticks()
        if time_now - last_pipe > pipe_frequency:
            # random generate pipes
            pipe_height = random.randint(-100, 100)

            btm_pipe = Pipe(screen_w, int(screen_h / 2) + pipe_height, -1)
            top_pipe = Pipe(screen_w, int(screen_h / 2) + pipe_height, 1)
            pipe_group.add(btm_pipe)
            pipe_group.add(top_pipe)
            last_pipe = time_now

        # draw and scroll the ground
        ground_scroll -= scroll_speed
        # verifica se o ground_scroll é maior que 35, 35 é o pixel size do pedacinho do ground image que fica pra fora da tela
        # foi usado abs pra deixar o número positivo e facilitar a checagem
        if abs(ground_scroll) > 35:
            ground_scroll = 0
    
        pipe_group.update()
        
    # check for game over and reset
    if game_over == True:
        if button.draw() == True:
            game_over = False
            score = reset_game()


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN and flying == False and game_over == False:
            flying = True

    pygame.display.update()

    
