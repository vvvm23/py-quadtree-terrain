import pygame
from pygame.locals import *
import numpy as np

import pygame.pixelcopy

def make_surface_rgba(array):
    """Returns a surface made from a [w, h, 4] numpy array with per-pixel alpha
    """
    shape = array.shape
    if len(shape) != 3 and shape[2] != 4:
        raise ValueError("Array not RGBA")

    # Create a surface the same width and height as array and with
    # per-pixel alpha.
    surface = pygame.Surface(shape[0:2], pygame.SRCALPHA, 32)

    # Copy the rgb part of array to the new surface.
    pygame.pixelcopy.array_to_surface(surface, array[:,:,0:3])

    # Copy the alpha part of array to the surface using a pixels-alpha
    # view of the surface.
    surface_alpha = np.array(surface.get_view('A'), copy=False)
    surface_alpha[:,:] = array[:,:,3]

    return surface

# https://stackoverflow.com/questions/41168396/how-to-create-a-pygame-surface-from-a-numpy-array-of-float32

pygame.init()

SCREEN_SIZE = (1200, 800)
WORLD_SPACE = (1200, 800)

world = np.ones(WORLD_SPACE, dtype=np.bool)
world[:, :400] = False

def render_texture_from_world(world: np.array):
    full = np.full((*SCREEN_SIZE, 4), (255, 0, 0, 255), dtype=np.uint8)

    return full * world.astype(np.uint8)[:, :, None]

window = pygame.display.set_mode(SCREEN_SIZE)

surface = make_surface_rgba(render_texture_from_world(world))

window.fill((255, 255, 255))

#pygame.draw.rect(
#    window, 
#    color=(0, 0, 255), 
#    rect=[100, 100, 400, 400], 
#)

window.blit(surface, (0, 0))

while True:
    pygame.display.update()
