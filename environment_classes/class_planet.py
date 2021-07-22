import math
import random

import pygame

from utility_classes import cfg
from environment_classes.class_crash import Crash


class Planet:
	def __init__(self, sun, distance_from_sun):
		self.sun = sun
		self.screen = sun.screen
		self.primary_type = random.choice(cfg.planet_probability)
		self.secondary_type = random.choice(cfg.planet_probability)
		self.on_screen = False
		self.x = 0
		self.y = 0
		self.location = pygame.Vector2(distance_from_sun, 0)
		self.orbit_distance = distance_from_sun
		self.rgb = cfg.set_composition(self.primary_type, self.secondary_type)
		self.radius = random.randint(cfg.min_planet_size, cfg.max_planet_size)
		self.width, self.height = self.radius, self.radius
		self.rect = pygame.Rect(self.location, (self.width, self.height))
		self.angle = random.randint(0, 360)
		self.angular_velocity = random.uniform(0.005, 0.03)
		self.polarity = random.choice([-1, 1])
		self.interactable_distance = cfg.pl_interactable_distance
		self.arrived_distance = cfg.pl_arrived_distance
		self.approach_velocity = False
		self.belt_width = [random.randint(0, cfg.belt_width_min), random.randint(
			cfg.belt_width_min + 5, cfg.belt_width_max)]

		self.asteroids = []
		self.crashes = []

		self.img_surface = pygame.Surface((self.radius * 2, self.radius * 2))

		self.setup_display_surface()

	def setup_display_surface(self):
		# Draw base colour
		pygame.draw.circle(self.img_surface, self.rgb, (self.radius, self.radius), self.radius)
		# Blit alpha to surface
		self.img_surface.blit(
			pygame.transform.smoothscale(cfg.planet_alpha_img, (self.radius * 2, self.radius * 2)), (0, 0))

	def update_orbit(self):
		self.angle -= self.angular_velocity if self.angle > 0 else - 360
		self.location = self.sun.location + pygame.Vector2(self.orbit_distance, 0).rotate(self.angle)
		self.rect.center = self.location

	def spawn_asteroids(self):
		# asteroids spawned is determined on asteroid size.
		asteroid_size = random.randint(cfg.min_crash_size, cfg.max_crash_size)
		new_crash = Crash(self, asteroid_size)
		self.crashes.append(new_crash)

	def draw(self):
		pygame.draw.circle(
			self.screen, self.rgb, self.rect.center, self.radius)
		image = pygame.transform.rotate(self.img_surface, - self.angle + 180)
		img_size = image.get_size()
		self.screen.blit(image, (
			self.rect.centerx - img_size[0] / 2,
			self.rect.centery - img_size[1] / 2
		))

	def loop(self):
		self.on_screen = cfg.on_screen_check(self)
		for i in self.crashes:
			i.loop()
		self.update_orbit()
		self.draw()
