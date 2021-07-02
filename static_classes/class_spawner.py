import math
import random

import pygame

from utility_classes import cfg

from entity_classes.hostile import Drone
from static_classes.class_nodule import Nodule


class Spawner:
	"""Class to manage roaming hostiles which move around and attack miners."""

	def __init__(self, game):
		self.game = game
		self.screen = game.screen
		self.diameter = random.randint(25, 65)
		self.location = pygame.math.Vector2(random.randint(1400, 1920), random.randint(600, 1080))
		# self.target_location = pygame.math.Vector2(random.randint(600, 1920), random.randint(400, 1080))
		self.acceleration = pygame.math.Vector2(0, 0)
		self.rect = pygame.Rect(self.location[0], self.location[1], self.diameter, self.diameter)
		self.hold = 0
		self.spawn_threshold = 5
		self.level = 1

		self.active = False

		self.desired_rotation_speed = .01
		self.rotation_speed = 0
		self.starting_angle = random.randint(0, 360)
		self.angle = self.starting_angle
		self.base_vec = pygame.Vector2(0, self.diameter / 2)
		self.spinner_vec = self.base_vec.rotate(self.angle)
		self.spinner_polarity = 1

		self.max_nodules = int((3.14 * self.diameter) / cfg.nodule_w * .9)
		self.nodules = []

		self.label = cfg.leaderboard_font.render(f"{self.max_nodules}", True, cfg.col.p_one)
		self.setup()

	def spawn_roamer(self, location):
		new_roamer = Drone(self.game, self, location)
		self.game.hostiles.append(new_roamer)

	def prepare_nodules(self, number_of_nodules):
		angle_step = 360 / number_of_nodules
		nodule_locations = [(self.angle + i * angle_step) % 360 for i in range(number_of_nodules)]
		for h, i in enumerate(nodule_locations):
			loc = pygame.Vector2(self.rect.center + self.base_vec.rotate(i))
			# this_max_lvl = [2, 3, 4][h % 3]
			self.nodules.append(Nodule(self.game, loc, self, self.get_next_max_level()))

	def setup(self):
		for _ in range(0):
			self.spawn_roamer(self.location)
		self.prepare_nodules(random.randint(1, math.ceil(self.diameter / 25)))

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

	def accept_resources(self, amt):
		self.hold += amt
		self.check_spawn()

	def get_next_max_level(self):
		return [2, 3, 4][len(self.nodules) % 3]

	def check_spawn(self):
		# where 1000 is dust required for new "sated".
		if self.hold >= 50 and len(self.nodules) < self.max_nodules:
			self.nodules.append(Nodule(self.game, self.nodules[-1].location, self, self.get_next_max_level()))
			self.hold = 0
			self.reposition_nodules()

	def reposition_nodules(self):
		angle_step = 360 / len(self.nodules)
		nodule_angles = [(self.starting_angle + i * angle_step) % 360 for i in range(len(self.nodules))]
		for h, i in enumerate(self.nodules):
			loc = pygame.Vector2(self.rect.center + self.base_vec.rotate(nodule_angles[h]))
			i.reposition_location(loc)

	def draw(self):
		# self.screen.blit(self.label, self.rect.bottomright)
		pygame.draw.circle(self.screen, cfg.col.p_five, self.rect.center, self.diameter / 2, 10)
		pygame.draw.circle(self.screen, cfg.col.p_three, self.rect.center, self.diameter / 2, 1)
		for i in self.nodules:
			i.draw()
		pygame.draw.circle(self.screen, cfg.col.p_one, self.spinner_vec, 9)

	def loop(self):
		self.update_spinner()
		# self.check_spawn()
		self.draw()
