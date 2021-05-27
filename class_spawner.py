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
		self.location = pygame.math.Vector2(random.randint(600, 1920), random.randint(400, 1080))
		self.acceleration = pygame.math.Vector2(0, 0)
		self.rect = pygame.Rect(self.location[0], self.location[1], 16, 16)
		self.hold = 0
		self.spawn_threshold = 5
		self.level = 1

		self.setup()

	def spawn_roamer(self):
		new_roamer = Roamer(self.game, self)
		self.game.hostiles.append(new_roamer)

	def setup(self):
		for _ in range(15):
			self.spawn_roamer()

	def check_spawn(self):
		# where 10 is dust required for new "sated".
		if self.hold > 0 and self.hold / 10 > self.spawn_threshold:
			for _ in range(int(self.hold / 10)):
				self.spawn_roamer()
			self.hold = 0

	def draw(self):
		pygame.draw.rect(self.screen, [200, 140, 20], self.rect)
		pygame.draw.circle(self.screen, [20, 140, 200], self.rect.center, 10, width=(int(self.hold / self.spawn_threshold)))

	def loop(self):
		self.check_spawn()
		self.draw()
