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
		self.location = pygame.math.Vector2(random.randint(1910, 1920), random.randint(0, 1080))
		self.acceleration = pygame.math.Vector2(0, 0)
		self.rect = pygame.Rect(self.location[0], self.location[1], 16, 16)
		self.hold = 0
		self.spawn_threshold = 4

		self.roamers = []

		self.setup()

	def spawn_roamer(self):
		new_roamer = Roamer(self.game, self)
		self.roamers.append(new_roamer)

	def setup(self):
		for i in range(50):
			self.spawn_roamer()

	def check_spawn(self):
		if self.hold > 0 and self.hold / 10 > self.spawn_threshold:
			for i in range(int(self.hold / 10)):
				self.spawn_roamer()
			self.hold = 0

	def draw(self):
		pygame.draw.rect(self.screen, [200, 140, 20], self.rect)
		pygame.draw.circle(self.screen, [20, 140, 200], self.rect.center, 10, width=(int(self.hold / self.spawn_threshold)))

	def loop(self):
		self.check_spawn()
		self.draw()
