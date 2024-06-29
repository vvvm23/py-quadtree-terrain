import pygame
from collections import namedtuple
from pygame.locals import *
import numpy as np
from typing import Tuple

import pygame.pixelcopy
import pprint

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
Point = namedtuple('Point', "x y")

class QuadTree:
    def __init__(self, position: Point, size: Point):
        self.position = position
        self.size = size

        self.children = []
        self.value = False

    def __contains__(self, point: Point) -> bool:
        return (self.position.x <= point.x < self.position.x + size.x) and (self.position.y <= point.y < self.position.y + size.y)

    def is_leaf(self) -> bool:
        return len(self.children) == 0

    def get_nested(self, as_str: bool = False):
        if self.is_leaf():
            return f"pos={self.position}, size={self.size}" if as_str else self

        return [c.get_nested(as_str=as_str) for c in self.children]

    def draw_to_window(self, window, color: Tuple[int, int, int], draw_wire: bool = False):
        if self.is_leaf():
            if self.value:
                pygame.draw.rect(
                    window,
                    color=color,
                    rect=[
                        self.position.x, self.position.y,
                        self.position.x + self.size.x, self.position.y + self.size.y
                    ]
                )
            if draw_wire:
                pygame.draw.rect(
                    window,
                    color=(0, 0, 0),
                    rect=[
                        self.position.x, self.position.y,
                        self.position.x + self.size.x, self.position.y + self.size.y
                    ],
                    width=1
                )
            return

        for c in self.children:
            c.draw_to_window(window, color=color, draw_wire=draw_wire)


pygame.init()

SCREEN_SIZE = (1024, 1024)
WORLD_SPACE = (1024, 1024)
QUADTREE_MINSIZE = 1

world = np.ones(WORLD_SPACE, dtype=np.bool)
world[:, :600] = False

def build_initial_quadtree(world: np.array):
    def _recurse_fn(parent: QuadTree):
        if parent.size.x <= QUADTREE_MINSIZE or parent.size.y <= QUADTREE_MINSIZE:
            # forced into leaf node
            # take average as value
            parent.value = np.rint(np.mean(subworld)).astype(bool)
            return

        subworld = world[
            parent.position.x : parent.position.x+parent.size.x,
            parent.position.y : parent.position.y+parent.size.y
        ]

        if np.all(subworld == True) or np.all(subworld == False):
            # leaf node via having all identical elements
            parent.value = subworld[0, 0]
            return

        # else, recurse into four quads
        for i in range(4):
            subsize_x = parent.size.x // 2
            subsize_y = parent.size.y // 2
            child = QuadTree(
                    position=Point(
                        parent.position.x + (i % 2)*subsize_x,
                        parent.position.y + (i // 2)*subsize_y
                    ), 
                size=Point(subsize_x, subsize_y)
            )
            parent.children.append(child)
            _recurse_fn(child)


    parent = QuadTree(Point(0, 0), Point(*WORLD_SPACE))

    _recurse_fn(parent)
    return parent

quadtree = build_initial_quadtree(world)
#pprint.pprint(quadtree.get_nested(as_str=True))
#exit()

def render_texture_from_world(world: np.array):
    full = np.full((*SCREEN_SIZE, 4), (255, 0, 0, 255), dtype=np.uint8)

    return full * world.astype(np.uint8)[:, :, None]

window = pygame.display.set_mode(SCREEN_SIZE)

window.fill((255, 255, 255))

#surface = make_surface_rgba(render_texture_from_world(world))
#window.blit(surface, (0, 0))

quadtree.draw_to_window(window, color=(124, 252, 0), draw_wire=True)

running = True

while running:

    pygame.display.update()

    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_q):
            pygame.quit()
            running = False

