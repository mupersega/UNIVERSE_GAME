import math
import random

import pygame

import cfg


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

	def choose_type(self):
		pass

	def mine(self, actor):
		cfg.draw_beam(self, actor)
		if random.randint(0, 1000) >= (997 - actor.miner_lvl):
			cfg.draw_explosion(self)
			yielded = self.mine_yield()
			actor.hold.append(yielded)
			print(f"Mined {yielded}, hold = {len(actor.hold)}")

	def mine_yield(self):
		self.size -= .5
		rolls = []
		for i in self.rgb:
			rolls.append(random.randint(0, i))
		max = 0
		choice = 0
		i = 0
		for j in rolls:
			if j > max:
				max, choice = j, i
				i += 1
		return cfg.mineral_list[choice]

	def set_colour(self):
		i = 0
		for ast in cfg.mineral_list:
			if self.primary_type == ast:
				self.rgb = cfg.mineral_info[ast]["rgb"]
			i += 1

	def draw(self):
		# pygame.draw.rect(self.game.screen, self.rgb, self.rect)
		pygame.draw.rect(self.screen, self.rgb, self.rect)

	def orbit(self):
		dist = self.orbit_distance + self.planet.size
		self.orbit_step += self.angular_velocity
		self.x = self.planet.x + math.cos(self.orbit_step) * dist
		self.y = self.planet.y - math.sin(self.orbit_step) * dist
		cfg.update_rect(self)

	def loop(self):
		self.on_screen = cfg.on_screen_check(self)
		if self.on_screen:
			self.draw()
		self.orbit()
