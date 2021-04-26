import math
import random

import pygame

import cfg

from class_roamer import Roamer


class Spawner:
	"""Class to manage roaming hostiles which move around and attack miners."""
	def __init__(self, game):
		self.game = game
		self.screen = game.screen
		self.location = pygame.math.Vector2(random.randint(300, 800), random.randint(300, 800))
		self.acceleration = pygame.math.Vector2(0, 0)
		self.rect = pygame.Rect(self.location[0], self.location[1], 16, 16)

		self.roamers = []

		self.setup()

	def spawn_roamer(self):
		new_roamer = Roamer(self.game, self)
		self.roamers.append(new_roamer)

	def setup(self):
		for i in range(15):
			self.spawn_roamer()

	def draw(self):
		pygame.draw.rect(self.screen, [200, 140, 20], self.rect)
		pygame.draw.circle(self.screen, [20, 140, 200], self.rect.center, 10, width=4)

	def loop(self):
		self.draw()
