import math
import random

import pygame

import cfg

class Roamer:
	"""Class to manage roaming hostiles which move around and attack miners."""
	def __init__(self, game, spawner):
		self.game = game
		self.screen = game.screen
		self.spawner = spawner
		self.image = cfg.starsated_image
		self.target_loc = pygame.math.Vector2(0, 0)
		self.location = pygame.math.Vector2(spawner.rect.center)
		self.acceleration = pygame.math.Vector2(0, 0)
		self.last_loc = pygame.math.Vector2(spawner.rect.center)
		self.ang_vec = pygame.math.Vector2(0, 0)
		self.velocity = 1
		self.top_speed = 1.5
		self.hold = 0
		self.rect = pygame.Rect(0, 0, 10, 10)
		self.angle = 3
		self.set_new_roam_location()

	def draw(self):
		pygame.draw.circle(self.screen, [255, 255, 255], self.target_loc, 1)
		draw_image = pygame.transform.rotate(self.image, self.angle)
		self.screen.blit(draw_image, (self.location[0] - 5, self.location[1] - 5))

	def feed(self):
		self.hold += 0

	def roam(self):
		# print(self.location.distance_to(self.target_loc))
		if self.hold > 1:
			self.target_loc = pygame.math.Vector2(self.spawner.location)
			if self.location.distance_to(self.target_loc) < 3:
				self.spawner.hold += self.hold
				self.hold = 0
		if self.location.distance_to(self.target_loc) < 3 and self.hold < 2:
			self.set_new_roam_location()
			self.feed()
			print(self.hold)

	def rotate(self):
		self.ang_vec = self.location - self.target_loc
		rads = math.atan2(self.ang_vec[0], self.ang_vec[1])
		deg = math.degrees(rads)
		self.angle = deg

	def assign_new_spawner(self):
		self.spawner = random.choice(self.game.spawners)

	def set_new_roam_location(self):
		w, h = cfg.screen_width / 4, cfg.screen_height / 4
		x_reg = random.choice([0, 1, 1, 2, 2, 2, 3, 3, 3, 3])
		y_reg = random.choice([0, 1, 1, 2, 2, 2, 3, 3, 3, 3])
		x = random.randint(0 + 10, w - 10)
		y = random.randint(0 + 10, h - 10)
		print(x_reg, x)
		self.target_loc[0] = x + (x_reg * w)
		self.target_loc[1] = y + (y_reg * h)
		self.last_loc = pygame.math.Vector2(self.location)

	def move(self):
		mod_range = 50
		dist_from = self.location.distance_to(self.last_loc)
		dist_to = self.location.distance_to(self.target_loc)
		if dist_from < mod_range:
			self.velocity = self.top_speed * (dist_from + 1) / mod_range
		elif dist_to < mod_range:
			self.velocity = dist_to * self.top_speed / mod_range
		self.acceleration = self.location - self.target_loc
		self.location -= self.acceleration.normalize() * self.velocity

	def loop(self):
		self.roam()
		self.move()
		self.rotate()
		self.draw()
