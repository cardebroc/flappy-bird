import pygame
import pygame as pg
from pygame.locals import *
import random
import neat
import os

DISPLAY_HEIGHT = 1000
DISPLAY_WIDTH = 1500

HEIGHT_UNIT = DISPLAY_HEIGHT / 100
GRAVITY = 0.1 * HEIGHT_UNIT


global generation


class Pipe:
    DISTANCE_TO_HOLE_CENTER = DISPLAY_HEIGHT * 0.1
    PIPE_WIDTH = 90

    def __init__(self, surface: pg.Surface, x, y_hole_center, move_speed=5):
        self.surface = surface

        self.x = x
        self.move_speed = move_speed
        self.top = pg.Rect((x, 0), (self.PIPE_WIDTH, y_hole_center - self.DISTANCE_TO_HOLE_CENTER))
        self.bottom = pg.Rect((x, y_hole_center + self.DISTANCE_TO_HOLE_CENTER),
                              (self.PIPE_WIDTH, DISPLAY_HEIGHT - (y_hole_center + self.DISTANCE_TO_HOLE_CENTER)))

    def move(self):
        self.top.update(self.top.left - self.move_speed, self.top.top, self.PIPE_WIDTH, self.top.height)
        self.bottom.update(self.bottom.left - self.move_speed, self.bottom.top, self.PIPE_WIDTH, self.bottom.height)

    def stop(self):
        self.move_speed = 0

    def draw(self):
        pg.draw.rect(self.surface, (180, 180, 180), self.top)
        pg.draw.rect(self.surface, (180, 180, 180), self.bottom)

    def update(self):
        self.move()
        self.draw()


class Bird:
    FLAP_LIFT = 5

    def __init__(self, x=DISPLAY_WIDTH * 0.1, y=DISPLAY_HEIGHT * 0.5):

        self.x = x
        self.y = y

        self.radius = DISPLAY_HEIGHT * 0.03

        self.score = 0
        self.velocity = 0
        self.rect = pg.Rect(self.x, self.y, DISPLAY_HEIGHT * 0.03, DISPLAY_HEIGHT * 0.03)

        self.is_alive = True

    def flap(self):
        # print('Bird Jump!')
        self.velocity = self.FLAP_LIFT + HEIGHT_UNIT

    def move(self):
        self.y -= self.velocity
        self.rect.update((self.x, self.y, self.rect.width, self.rect.height))

    def draw(self, surface: pg.Surface):
        pg.draw.circle(surface, (255, 0, 0), self.rect.center, radius=self.radius)

    def get_data(self, pipes: list[Pipe]):
        nearest_pipe = sorted(list(filter(lambda pipe: pipe.top.left - self.x > 0, pipes)), key=lambda pipe: pipe.top.left)[0]
        return self.y, nearest_pipe.top.left, nearest_pipe.top.bottom, nearest_pipe. bottom.top

    def die(self):
        self.is_alive = False

    def update(self, surface: pg.Surface):
        if self.is_alive:
            self.score += 1
            self.move()
            self.draw(surface)
            if DISPLAY_HEIGHT - (2 * self.radius) > self.y > 0:
                self.velocity -= GRAVITY
            else:
                self.velocity = 0
                if self.y < DISPLAY_HEIGHT - (2 * self.radius):
                    self.y = DISPLAY_HEIGHT - (2 * self.radius)
                else:
                    self.y = 0


def run_game(genomes, _config):
    # Initialize PyGame
    global generation
    pygame.init()

    screen = pg.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT))
    surface = pg.Surface((DISPLAY_WIDTH, DISPLAY_HEIGHT))
    fps = pg.time.Clock()

    # Initialize Neural Nets
    birds_brains_genes = []

    for genome_id, genome in genomes:
        net = neat.nn.FeedForwardNetwork.create(genome, _config)
        genome.fitness = 0

        birds_brains_genes.append((Bird(), net, genome))

    pipes = [Pipe(surface, DISPLAY_WIDTH, DISPLAY_HEIGHT * 0.5)]

    generation += 1
    running = True
    while running:
        surface.fill((50, 50, 50))

        for event in pygame.event.get():
            if event.type == QUIT:
                running = False

        if DISPLAY_WIDTH - pipes[-1].top.right >= 450:
            pipes.append(Pipe(surface, DISPLAY_WIDTH, (random.random() + 0.1) * (DISPLAY_HEIGHT * 0.8)))

        if pipes[0].top.right < 0:
            del pipes[0]

        # Stuff happens
        for bird, brain, genome in birds_brains_genes:
            output = brain.activate(bird.get_data(pipes))[0]
            if output > 0.5:
                bird.flap()

            bird.update(surface)
            if sum([1 for pip in pipes if bird.rect.colliderect(pip.top) or bird.rect.colliderect(pip.bottom)]) > 0:
                bird.die()

        # if bird.rect.collidelist([rect for pipe in pipes for rect in [pipe.top, pipe.bottom]]) > 0:
        #     print("DEAD")

        for pipe in pipes:
            pipe.update()

        if len([bird for bird, _, _ in birds_brains_genes if bird.is_alive]) == 0:
            total_score = sum([bird.score for bird, _, _ in birds_brains_genes])
            for bird, net, genome in birds_brains_genes:
                genome.fitness = bird.score / total_score
            print('game over')
            break

        font = pg.font.SysFont('lato', 45, bold=True)
        img = font.render(f'Generation: {str(generation)}', True, (0, 0, 255))

        screen.blit(surface, (0, 0))
        # screen.blit(img, (DISPLAY_WIDTH * 0.5, 0))
        pygame.display.update()
        fps.tick(60)


if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config.txt')

    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_path)

    # Create the population, which is the top-level object for a NEAT run.
    p = neat.Population(config)

    # Add a stdout reporter to show progress in the terminal.
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    p.add_reporter(neat.Checkpointer(5))

    # Run for up to 300 generations.
    winner = p.run(run_game, 100)
