import pygame
import cfg


class Location:
    """A class dedicated to the storing of a polar location, x und y, ja."""
    def __init__(self, pos, approach_velocity=False, approach_angle=False):
        self.x = pos[0]
        self.y = pos[1]
        self.on_screen = True
        self.rect = pygame.Rect(self.x, self.y, 1, 1)
        self.approach_velocity = approach_velocity
        self.approach_angle = approach_angle

        self.arrived_distance = cfg.loc_arrived_distance
        self.interactable_distance = cfg.loc_interactable_distance
