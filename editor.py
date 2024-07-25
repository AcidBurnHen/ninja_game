import sys
import pygame
from modules.tilemap import Tilemap
from utils import load_image, load_images

RENDER_SCALE = 2.0


class Editor:
    def __init__(self):
        pygame.init()

        pygame.display.set_caption("Level editor")
        self.screen = pygame.display.set_mode((640, 480))

        self.display = pygame.Surface((320, 240))

        self.clock = pygame.time.Clock()

        self.assets = {
            "decor": load_images("tiles/decor"),
            "grass": load_images("tiles/grass"),
            "large_decor": load_images("tiles/large_decor"),
            "stone": load_images("tiles/stone"),
        }

        self.movement = [False, False, False, False]

        # print(self.assets)

        self.tilemap = Tilemap(self, tile_size=16)
        self.tile_list = list(self.assets)
        self.tile_group = 0
        self.tile_variant = 0

        self.scroll = [0, 0]

        self.clicking = False
        self.right_clicking = False
        self.shift = False

    def run(self):
        while True:
            self.display.fill((0, 0, 0))

            self.scroll[0] += (self.movement[1] - self.movement[0]) * 2
            self.scroll[1] += (self.movement[3] - self.movement[2]) * 2
            render_scroll = (int(self.scroll[0]), int(self.scroll[1]))

            self.tilemap.render(self.display, offset=render_scroll)

            current_tile_image = self.assets[self.tile_list[self.tile_group]][
                self.tile_variant
            ].copy()
            current_tile_image.set_alpha(100)

            mouse_pos = pygame.mouse.get_pos()
            mouse_pos = (mouse_pos[0] / RENDER_SCALE, mouse_pos[1] / RENDER_SCALE)
            tile_pos = (
                (int(mouse_pos[0] + self.scroll[0]) // self.tilemap.tile_size),
                (int(mouse_pos[1] + self.scroll[1]) // self.tilemap.tile_size),
            )

            # Display preview of where current tile could be placed on the grid
            self.display.blit(
                current_tile_image,
                (
                    tile_pos[0] * self.tilemap.tile_size - self.scroll[0],
                    tile_pos[1] * self.tilemap.tile_size - self.scroll[1],
                ),
            )

            tile_loc = str(tile_pos[0]) + ";" + str(tile_pos[1])

            if self.clicking:
                self.tilemap.tilemap[tile_loc] = {
                    "type": self.tile_list[self.tile_group],
                    "variant": self.tile_variant,
                    "pos": tile_pos,
                }
            elif self.right_clicking:
                if tile_loc in self.tilemap.tilemap:
                    del self.tilemap.tilemap[tile_loc]

            self.display.blit(current_tile_image, (5, 5))

            # Listen to user events
            for event in pygame.event.get():
                # Take care of closing the window
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.clicking = True
                    elif event.button == 3:
                        self.right_clicking = True
                    elif self.shift:
                        if event.button == 4:
                            self.tile_variant = (self.tile_variant - 1) % len(
                                self.assets[self.tile_list[self.tile_group]]
                            )
                        elif event.button == 5:
                            self.tile_variant = (self.tile_variant + 1) % len(
                                self.assets[self.tile_list[self.tile_group]]
                            )
                    else:
                        if event.button == 4:
                            self.tile_group = (self.tile_group - 1) % len(
                                self.tile_list
                            )
                            self.tile_variant = 0
                        elif event.button == 5:
                            self.tile_group = (self.tile_group + 1) % len(
                                self.tile_list
                            )
                            self.tile_variant = 0
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        self.clicking = False
                    elif event.button == 3:
                        self.right_clicking = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        self.movement[0] = True
                    elif event.key == pygame.K_RIGHT:
                        self.movement[1] = True
                    elif event.key == pygame.K_UP:
                        self.movement[2] = True
                    elif event.key == pygame.K_DOWN:
                        self.movement[3] = True
                    elif event.key in [pygame.K_LSHIFT, pygame.K_RSHIFT]:
                        self.shift = True
                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT:
                        self.movement[0] = False
                    elif event.key == pygame.K_RIGHT:
                        self.movement[1] = False
                    elif event.key == pygame.K_UP:
                        self.movement[2] = False
                    elif event.key == pygame.K_DOWN:
                        self.movement[3] = False
                    elif event.key in [pygame.K_LSHIFT, pygame.K_RSHIFT]:
                        self.shift = False

            self.screen.blit(
                pygame.transform.scale(self.display, self.screen.get_size()), (0, 0)
            )
            pygame.display.update()
            # Force the loop to run at 60 FPS
            self.clock.tick(60)


Editor().run()
