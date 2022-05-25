import pygame
import pygame as pg
from pygame.locals import *

DISPLAY_HEIGHT = 1000
DISPLAY_WIDTH = 1000

HEIGHT_UNIT = DISPLAY_HEIGHT / 100
GRAVITY = 0.1 * HEIGHT_UNIT


class SceneObject:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class Bird(SceneObject):
    FLAP_LIFT = 10

    def __init__(self, surface: pg.Surface, x=DISPLAY_WIDTH * 0.1, y=DISPLAY_HEIGHT * 0.5):
        super().__init__(x, y)
        self.score = 0
        self.velocity = 0
        self.surface = surface
        self.rect = pg.Rect(self.x, self.y, DISPLAY_WIDTH * 0.05, DISPLAY_WIDTH * 0.05)
        self.update()

    def flap(self):
        print('Bird Jump!')
        self.velocity = self.FLAP_LIFT + HEIGHT_UNIT

    def move(self):
        self.y -= self.velocity
        self.rect.update((self.x, self.y, self.rect.width, self.rect.height))

    def draw(self):
        pg.draw.circle(self.surface, (255, 0, 0), self.rect.center, radius=DISPLAY_WIDTH * 0.05)

    def update(self):
        print(self.rect.center)
        self.move()
        self.draw()
        if self.y < DISPLAY_HEIGHT + DISPLAY_WIDTH * 0.05 or self.y < 0:
            self.velocity -= GRAVITY
        else:
            self.velocity = 0
            self.y = DISPLAY_HEIGHT - 2 * DISPLAY_WIDTH * 0.05


def main():
    pygame.init()  # Initialize PyGame

    screen = pg.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT))
    surface = pg.Surface((DISPLAY_WIDTH, DISPLAY_HEIGHT))

    bird = Bird(surface)
    fps = pg.time.Clock()

    running = True
    while running:
        surface.fill((0, 0, 0))

        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                bird.flap()

        bird.update()
        screen.blit(surface, (0, 0))
        pygame.display.update()
        fps.tick(30)


if __name__ == '__main__':
    main()
