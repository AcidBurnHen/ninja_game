import os
import sys
import math
import random
import pygame
from modules.entities import Player, Enemy
from modules.tilemap import Tilemap
from modules.clouds import Clouds
from modules.animations import Animation
from modules.particles import Particle
from modules.sparks import Spark
from utils import load_image, load_images


class Game:
    def __init__(self):
        pygame.init()

        pygame.display.set_caption("Ninja G4M3")
        self.screen = pygame.display.set_mode((640, 480))

        self.display = pygame.Surface((320, 240), pygame.SRCALPHA)
        self.display_2 = pygame.Surface((320, 240))

        self.clock = pygame.time.Clock()

        self.movement = [False, False]

        self.assets = {
            "decor": load_images("tiles/decor"),
            "grass": load_images("tiles/grass"),
            "large_decor": load_images("tiles/large_decor"),
            "stone": load_images("tiles/stone"),
            "clouds": load_images("clouds"),
            "player": load_image("entities/player.png"),
            "background": load_image("background.png"),
            "enemy/idle": Animation(load_images("entities/enemy/idle"), img_dur=6),
            "enemy/run": Animation(load_images("entities/enemy/run"), img_dur=4),
            "player/idle": Animation(load_images("entities/player/idle"), img_dur=6),
            "player/run": Animation(load_images("entities/player/run"), img_dur=4),
            "player/jump": Animation(load_images("entities/player/jump")),
            "player/slide": Animation(load_images("entities/player/slide")),
            "player/wall_slide": Animation(load_images("entities/player/wall_slide")),
            "particle/leaf": Animation(load_images("particles/leaf"), img_dur=20, loop=False),
            "particle/particle": Animation(load_images("particles/particle"), img_dur=6, loop=False),
            "gun": load_image("gun.png"),
            "projectile": load_image("projectile.png"),
        }

        self.clouds = Clouds(self.assets["clouds"], count=16)

        # print(self.assets)

        self.player = Player(game=self, pos=(50, 50), size=(8, 15))

        self.tilemap = Tilemap(self, tile_size=16)

        self.level = 0
        self.load_level(self.level)

        self.screenshake = 0
        self.max_levels = len(os.listdir("data/maps")) - 1

    def load_level(self, map_id):
        self.tilemap.load("data/maps/" + str(map_id) + ".json")
        # self.tilemap.load("map.json")
        self.leaf_spawners = []
        for tree in self.tilemap.extract([("large_decor", 2)], keep=True):
            self.leaf_spawners.append(pygame.Rect(4 + tree["pos"][0], 4 + tree["pos"][1], 23, 13))

        self.enemies = []
        for spawner in self.tilemap.extract([("spawners", 0), ("spawners", 1)]):
            if spawner["variant"] == 0:
                self.player.pos = spawner["pos"]
                self.player.air_time = 0
            else:
                self.enemies.append(Enemy(self, spawner["pos"], (8, 15)))

        # [[x, y], direction, timer]
        self.projectiles = []
        self.particles = []
        self.sparks = []

        self.scroll = [0, 0]
        self.dead = 0
        self.transition = -30

    def run(self):
        while True:
            self.display.fill((0, 0, 0, 0))
            self.display_2.blit(self.assets["background"], (0, 0))

            self.screenshake = max(0, self.screenshake - 1)

            if not len(self.enemies):
                self.transition += 1
                if self.transition > 30:
                    self.level = min(self.max_levels, self.level + 1)
                    self.load_level(self.level)
            if self.transition < 0:
                self.transition += 1

            if self.dead:
                self.dead += 1
                if self.dead == 10:
                    self.transition = min(30, self.transition + 1)
                if self.dead > 40:
                    # Reset player velocity after death
                    self.player.velocity = [0, 0]
                    self.load_level(self.level)

            # Calculate camera position
            self.scroll[0] += (self.player.rect().centerx - self.display.get_width() / 2 - self.scroll[0]) / 30

            self.scroll[1] += (self.player.rect().centery - self.display.get_height() / 2 - self.scroll[1]) / 30

            render_scroll = (int(self.scroll[0]), int(self.scroll[1]))

            # Spawn particles
            for rect in self.leaf_spawners:
                if random.random() * 49999 < rect.width * rect.height:
                    pos = (
                        rect.x + random.random() * rect.width,
                        rect.y + random.random() * rect.height,
                    )
                    self.particles.append(
                        Particle(
                            self,
                            "leaf",
                            pos,
                            velocity=[
                                random.uniform(0.1, 0.4),
                                random.uniform(0.2, 0.4),
                            ],
                            frame=random.randint(0, 20),
                        )
                    )

            # Insert clouds
            self.clouds.update()
            self.clouds.render(self.display, offset=render_scroll)

            # Render tiles
            self.tilemap.render(self.display, offset=render_scroll)

            # Render enemies
            for enemy in self.enemies.copy():
                kill = enemy.update(self.tilemap, (0, 0))
                enemy.render(self.display, offset=render_scroll)
                if kill:
                    self.enemies.remove(enemy)

            # Render player
            if not self.dead:
                self.player.update(self.tilemap, (self.movement[1] - self.movement[0], 0))
                self.player.render(self.display, offset=render_scroll)

            # Projectiles
            for projectile in self.projectiles.copy():
                projectile[0][0] += projectile[1]
                projectile[2] += 1
                img = self.assets["projectile"]
                self.display.blit(
                    img,
                    (
                        projectile[0][0] - img.get_width() / 2 - render_scroll[0],
                        projectile[0][1] - img.get_height() / 2 - render_scroll[1],
                    ),
                )
                if self.tilemap.solid_check(projectile[0]) or projectile[2] > 360:
                    for i in range(4):
                        self.sparks.append(
                            Spark(
                                self.projectiles[0][0],
                                random.random() - 0.5 + (math.pi if projectile[1] > 0 else 0),
                                2 + random.random(),
                            )
                        )

                    self.projectiles.remove(projectile)
                elif abs(self.player.dashing) < 50 and self.player.rect().collidepoint(projectile[0]):
                    self.projectiles.remove(projectile)
                    self.dead += 1
                    self.screenshake = max(16, self.screenshake)
                    for i in range(30):
                        angle = random.random() * math.pi * 2
                        speed = random.random() * 5
                        self.sparks.append(Spark(self.player.rect().center, angle, 2 + random.random()))
                        self.particles.append(
                            Particle(
                                self,
                                "particle",
                                self.player.rect().center,
                                velocity=[math.cos(angle + math.pi) * speed - 0.5, math.sin(angle + math.pi) * speed * 0.5],
                                frame=random.randint(0, 7),
                            )
                        )

            # Sparks
            for spark in self.sparks.copy():
                kill = spark.update()
                spark.render(self.display, offset=render_scroll)
                if kill:
                    self.sparks.remove(spark)

            display_mask = pygame.mask.from_surface(self.display)
            display_sillhouette = display_mask.to_surface(setcolor=(0, 0, 0, 180), unsetcolor=(0, 0, 0, 0))
            for offset in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                self.display_2.blit(display_sillhouette, offset)

            # Manage particles and remove killed ones
            for particle in self.particles.copy():
                kill = particle.update()
                particle.render(self.display, offset=render_scroll)
                if particle.type == "leaf":
                    particle.pos[0] += math.sin(particle.animation.frame * 0.035) * 0.35
                if kill:
                    self.particles.remove(particle)

            # Listen to user events
            for event in pygame.event.get():
                # Take care of closing the window
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        self.movement[0] = True
                    elif event.key == pygame.K_RIGHT:
                        self.movement[1] = True
                    elif event.key == pygame.K_UP:
                        self.player.jump()
                    elif event.key in [pygame.K_x, pygame.K_KP_0]:
                        self.player.dash()
                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT:
                        self.movement[0] = False
                    elif event.key == pygame.K_RIGHT:
                        self.movement[1] = False

            if self.transition:
                transition_surf = pygame.Surface(self.display.get_size())
                pygame.draw.circle(
                    transition_surf, (255, 255, 255), (self.display.get_width() // 2, self.display.get_height() // 2), (30 - abs(self.transition)) * 8
                )
                transition_surf.set_colorkey((255, 255, 255))
                self.display.blit(transition_surf, (0, 0))

            self.display_2.blit(self.display, (0, 0))

            screenshake_offset = (random.random() * self.screenshake - self.screenshake / 2, random.random() * self.screenshake - self.screenshake / 2)
            self.screen.blit(pygame.transform.scale(self.display_2, self.screen.get_size()), screenshake_offset)
            pygame.display.update()
            # Force the loop to run at 60 FPS
            self.clock.tick(60)


Game().run()
