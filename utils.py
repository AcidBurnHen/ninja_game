import os
import pygame

BASE_IMAGE_PATH = "data/images"


def load_image(path):
    img = pygame.image.load(os.path.join(BASE_IMAGE_PATH, path)).convert()
    img.set_colorkey((0, 0, 0))
    return img


def load_images(path):
    images = []
    folder_path = os.path.join(BASE_IMAGE_PATH, path)
    for img_name in sorted(os.listdir(folder_path)):
        img = pygame.image.load(os.path.join(folder_path, img_name)).convert()
        img.set_colorkey((0, 0, 0))
        images.append(img)

    return images
