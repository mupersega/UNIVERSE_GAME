import pygame
import math
import random
import cfg
from class_crash import Crash


class Planet:
	def __init__(self, sun, distance_from_sun):
		self.sun = sun
		self.screen = sun.screen
		self.primary_type = random.choice(cfg.planet_probability)
		self.secondary_type = random.choice(cfg.planet_probability)
		self.on_screen = False
		self.x = 0
		self.y = 0
		self.distance_from_sun = distance_from_sun
		self.rgb = cfg.set_composition(self.primary_type, self.secondary_type)
		self.size = self.set_size()
		self.width, self.height = self.size, self.size
		self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
		self.orbit_step = random.randint(0, 360)
		self.angular_velocity = random.randint(1, 5) / 10000
		self.polarity = random.choice([-1, 1])
		self.interactable_distance = cfg.pl_interactable_distance
		self.arrived_distance = cfg.pl_arrived_distance
		self.approach_velocity = False
		self.belt_width = [random.randint(0, cfg.belt_width_min), random.randint(
			cfg.belt_width_min + 5, cfg.belt_width_max)]
		self.asteroids = []
		self.crashes = []

	def set_size(self):
		# random.randint(10, 36)
		max = cfg.max_planet_size
		min = cfg.min_planet_size
		return random.randint(min, max + 1)

	def orbit(self):
		dist = self.distance_from_sun
		self.orbit_step += self.angular_velocity
		self.x = self.sun.x + math.cos(self.orbit_step) * dist
		self.y = self.sun.y - math.sin(self.orbit_step) * dist
		self.update_rect()

	def spawn_asteroids(self):
		# asteroids spawned is determined on asteroid size.
		asteroid_size = random.randint(cfg.min_crash_size, cfg.max_crash_size)
		new_crash = Crash(self, asteroid_size)
		self.crashes.append(new_crash)

	def update_rect(self):
		x, y = self.x - self.size * .5, self.y - self.size * .5
		self.rect.x = x
		self.rect.y = y

	def draw(self):
		pygame.draw.circle(
			self.screen, self.rgb, (int(self.x), int(self.y)), self.size)

	def loop(self):
		self.on_screen = cfg.on_screen_check(self)
		for i in self.crashes:
			i.loop()
		self.orbit()
		self.draw()
