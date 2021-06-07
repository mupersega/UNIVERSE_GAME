import math
import random

import pygame

import cfg

from class_roamer import Roamer
from class_nodule import CircleNodule


class Spawner:
	"""Class to manage roaming hostiles which move around and attack miners."""

	def __init__(self, game):
		self.game = game
		self.screen = game.screen
		self.diameter = random.randint(25, 50)
		self.location = pygame.math.Vector2(random.randint(600, 1920), random.randint(400, 1080))
		self.acceleration = pygame.math.Vector2(0, 0)
		self.rect = pygame.Rect(self.location[0], self.location[1], self.diameter, self.diameter)
		self.hold = 0
		self.spawn_threshold = 5
		self.level = 1

		self.active = False

		self.desired_rotation_speed = .01
		self.rotation_speed = 0
		self.angle = random.randint(0, 360)
		self.base_vec = pygame.Vector2(0, self.diameter / 2)
		self.spinner_vec = self.base_vec.rotate(self.angle)
		self.spinner_polarity = 1

		self.nodules = []

		self.setup()

	def spawn_roamer(self, location):
		new_roamer = Roamer(self.game, self, location)
		self.game.hostiles.append(new_roamer)

	def prepare_nodules(self, number_of_nodules):
		angle_step = 360 / number_of_nodules
		nodule_locations = [(self.angle + i * angle_step) % 360 for i in range(number_of_nodules)]
		for i in nodule_locations:
			loc = pygame.Vector2(self.rect.center + self.base_vec.rotate(i))
			self.nodules.append(CircleNodule(self.game, loc, self))

	def setup(self):
		for _ in range(0):
			self.spawn_roamer()
		self.prepare_nodules(random.randint(1, math.ceil(self.diameter / 10)))

	def update_spinner(self):
		# spool up or down
		if self.rotation_speed != self.desired_rotation_speed:
			if self.rotation_speed > self.desired_rotation_speed:
				self.rotation_speed -= 0.002
				self.rotation_speed *= .995
			elif self.rotation_speed < self.desired_rotation_speed:
				self.rotation_speed += 0.001
				self.rotation_speed *= 1.01
		if self.angle > 360:
			self.angle = 0
			self.spinner_polarity *= -1
		self.angle += self.rotation_speed
		if self.rotation_speed > 0:
			self.spinner_vec = pygame.Vector2(self.rect.center + self.base_vec.rotate(self.angle))
		for i in self.nodules:
			if (self.spinner_vec.distance_to(i.rect.center) < 5 and i.last_hit != self.spinner_polarity and len(
					self.game.hostiles) < cfg.max_hostiles):
				i.spawn()
				i.last_hit = self.spinner_polarity

	def check_spawn(self):
		# where 20 is dust required for new "sated".
		if self.hold > 0 and self.hold / 20 > self.spawn_threshold:
			for _ in range(int(self.hold / 20)):
				self.spawn_roamer()
			self.hold = 0

	def draw(self):
		# pygame.draw.rect(self.screen, [200, 140, 20], self.rect)
		pygame.draw.circle(self.screen, cfg.col.charcoal, self.rect.center, self.diameter / 2, 10)
		for i in self.nodules:
			i.draw()
		pygame.draw.circle(self.screen, cfg.col.pumpkin, self.spinner_vec, 9)

	def loop(self):
		self.update_spinner()
		# self.check_spawn()
		self.draw()
