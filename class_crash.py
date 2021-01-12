import random
import math
import pygame
import cfg
from class_asteroid import Asteroid
from class_location import Location


class Crash:
	"""Animation event that spawns asteroids after hitting target planet."""
	def __init__(self, planet, size):
		# the parent of a Crash object is the planet it will hit
		self.planet = planet
		self.screen = planet.screen
		self.target = planet
		self.size = size
		self.x, self.y = 0, 0
		self.primary_type = random.choice(cfg.mineral_list)
		self.secondary_type = random.choice(cfg.mineral_list)
		self.rgb = cfg.set_composition(self.primary_type, self.secondary_type)

		self.width, self.height = size, size
		self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
		self.vel = 4
		self.agility = .4
		self.life = 0

		self.set_crash_spawn_position()
		self.start_location = Location([self.x, self.y])
		self.angle = cfg.angle_to_target(self)

		self.expended = False

	def set_crash_spawn_position(self):
		method = random.randint(0, 1)
		if method == 0:
			x = random.choice([-100, cfg.screen_width + 100])
			y = random.randint(-100, cfg.screen_height + 100)
		elif method == 1:
			x = random.randint(-100, cfg.screen_width + 100)
			y = random.choice([-100, cfg.screen_height + 100])
		self.x = x
		self.y = y

	def move(self):
		if self.life > 100:
			self.life += .001
			self.explode()
		# if not in arrived distance of target, turn and move toward target
		if cfg.distance_to_target(self) > (
			self.target.size + self.target.arrived_distance):
			self.angle = cfg.angle_to_target(self) * self.agility
			self.x += math.cos(self.angle) * self.vel
			self.y -= math.sin(self.angle) * self.vel
			cfg.update_rect(self)
		else:
			self.expended = True
			self.explode()
		cfg.update_rect(self)

	def explode(self):
		mass = self.width * self.height
		expended = 0
		for i in range(mass):
			size = random.randint(1, self.width)
			new_asteroid = Asteroid(self.planet, self, size)
			self.planet.asteroids.append(new_asteroid)
			expended += size
			if expended >= mass:
				self.expended = True
				self.target = None
				break

	def loop(self):
		if self.expended:
			self.planet.crashes.remove(self)
		else:
			self.move()
			self.draw()

	def draw(self):
		pygame.draw.rect(self.screen, self.rgb, (
			self.x, self.y, self.size, self.size))
