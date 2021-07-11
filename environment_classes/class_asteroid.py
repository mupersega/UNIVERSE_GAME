import math
import random

import pygame

from utility_classes import cfg


class Asteroid:
	"""Class to manage an asteroid spawned in a belt."""
	def __init__(self, planet, crash, size):
		self.planet = planet
		self.screen = planet.screen
		self.on_screen = False
		self.primary_type = planet.primary_type
		self.secondary_type = crash.primary_type
		self.rgb = cfg.set_composition(self.primary_type, self.secondary_type)
		self.x = 0
		self.y = 0

		# Navigation Controls
		self.location = pygame.math.Vector2(self.x, self.y)
		self.trajectory = pygame.math.Vector2(0, 0)
		self.size = random.randint(2, 6)
		self.width, self.height = self.size, self.size
		self.orbit_distance = cfg.belt_exclusion_range + random.randint(
			planet.belt_width[0], planet.belt_width[1])
		self.angular_velocity = (random.randint(10, 20) / 1000) * (
			# distance modifier
			1 - (self.orbit_distance / 60)) * (
			# size modifier
			1 - (self.size / cfg.max_crash_size))
		self.orbit_step = random.randint(0, 360)
		self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

		self.interactable_distance = cfg.ast_interactable_distance
		self.arrived_distance = cfg.ast_arrived_distance
		self.approach_velocity = False

		# DEBUGGING
		self.main_rgb = cfg.mineral_info[cfg.mineral_name_list[self.rgb.index(max(self.rgb))]]["market_rgb"]

	def mine(self, actor):
		cfg.draw_beam(self, actor)
		if random.randint(0, 1000) >= (998 - actor.miner_lvl * .5):
			cfg.draw_explosion(self)
			yielded = self.mine_yield()
			self.decay()
			# print(actor.ores)
			actor.ores[yielded] += 1
			print(f"Mined {cfg.mineral_name_list[yielded]}, hold = {sum(actor.ores)}")

	def mine_yield(self):
		rolls = [random.uniform(0, i ** 2) for i in self.rgb]
		return rolls.index(max(rolls))

	def decay(self):
		self.size -= .1
		self.width, self.height = self.size, self.size
		if self.size <= 0 and self in self.planet.asteroids:
			self.planet.asteroids.remove(self)

	def draw(self):
		# pygame.draw.rect(self.game.screen, self.rgb, self.rect)
		# pygame.draw.rect(self.screen, self.rgb, self.rect)
		pygame.draw.rect(self.screen, self.main_rgb, self.rect)

	def orbit(self):
		dist = self.orbit_distance + self.planet.size
		self.orbit_step += self.angular_velocity
		self.x = self.planet.x + math.cos(self.orbit_step) * dist
		self.y = self.planet.y - math.sin(self.orbit_step) * dist
		cfg.update_rect(self)
		self.location = (self.rect.center[0], self.rect.center[1])

	def loop(self):
		self.on_screen = cfg.on_screen_check(self)
		if self.on_screen:
			self.draw()
		self.orbit()
