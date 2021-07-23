import random

import pygame

from utility_classes import cfg
from environment_classes.class_planet import Planet


class Sun:
	"""Class to manage the sun in the bottom right corner of screen about which
	all planets and thus asteroids rotate."""
	def __init__(self, parent, planets):
		# a sun's parent is a Game object
		self.parent = parent
		self.screen = parent.screen
		self.planet_count = planets
		# self.x = int(cfg.screen_width / 2)
		# self.y = int(cfg.screen_height / 2)
		self.x = cfg.screen_width
		self.y = cfg.screen_height
		self.location = pygame.Vector2(cfg.screen_width / 2, cfg.screen_height)
		self.rgb = cfg.sun_colour
		self.radius = cfg.sun_start_size
		self.max_size = cfg.sun_max_size
		self.arrived_distance = self.radius + cfg.sun_arrived_distance
		self.interactable_distance = self.radius + cfg.sun_interactable_distance
		self.approach_velocity = False
		self.rect = pygame.Rect(self.location, (self.radius * 2, self.radius * 2))
		self.rect.center = self.rect.topleft
		self.damage_taken = 1
		self.life = 1

		self.available_positions = []
		self.planets = []

		self.mask = pygame.transform.smoothscale(cfg.sun_mask_img, self.rect.size)

		self.sun_setup()
		# print(len(self.planets))

	def sun_setup(self):
		# get potential planet placements
		self.set_available_positions()
		# construct planets
		for _ in range(self.planet_count):
			self.new_planet()

	def new_planet(self):
		# get random position and pop from potential available positions
		distance_from_sun = self.available_positions.pop(random.randint(0, len(
			self.available_positions) - 1))
		# construct planet at position
		new_planet = Planet(self, distance_from_sun)
		self.planets.append(new_planet)

	def set_available_positions(self):
		placeable_pixel_range = (
				cfg.screen_height - self.max_size - cfg.sun_exclusion_range)
		increment_size = placeable_pixel_range / cfg.max_planets_per_sun
		for i in range(cfg.max_planets_per_sun):
			self.available_positions.append(
				self.max_size + cfg.sun_exclusion_range + i * increment_size)

	def take_damage(self, amt):
		self.damage_taken += amt

	def resize(self):
		# pulse effect potentially here
		if self.radius > 142:
			self.radius *= .9999
			return
		self.radius = random.randint(145, 150)

	def draw(self):
		pygame.draw.circle(
			self.screen, self.rgb, self.rect.center, self.radius * .6)
		pygame.draw.circle(
			self.screen, [125, 125, 5], self.rect.center, self.radius * .5)
		self.screen.blit(self.mask, self.rect.topleft)

	def loop(self):
		self.resize()
		self.draw()
