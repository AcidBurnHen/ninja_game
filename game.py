import sys
import pygame


class Game:
    def __init__(self):
        pygame.init()

        pygame.display.set_caption("Ninja G4M3")
        self.screen = pygame.display.set_mode((640, 480))

        self.clock = pygame.time.Clock()

        self.img = pygame.image.load("data/images/clouds/cloud_1.png")

    def run(self):
        while True:
            self.screen.blit(self.img, (100, 200))

            # Listen to user events
            for event in pygame.event.get():
                # Take care of closing the window
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            pygame.display.update()
            # Force the loop to run at 60 FPS
            self.clock.tick(60)


Game().run()
