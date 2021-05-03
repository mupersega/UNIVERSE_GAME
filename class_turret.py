import pygame
import random

import cfg

from class_maul import Maul


class Turret:
	"""Bay object wherein players will store vehicles and land current ship."""

	def __init__(self, hangar):
		self.screen = hangar.station.game.screen
		self.hangar = hangar
		self.game = hangar.station.game
		self.owner = hangar.owner
		self.kind = 'turret'
		self.index = 1
		self.on_screen = True

		self.x = 1
		self.y = 1
		self.location = pygame.math.Vector2(self.x, self.y)
		self.hostile_target = self.choose_a_rand_target()
		self.width = cfg.facility_w
		self.height = cfg.facility_h
		self.diameter = 10
		self.approach_velocity = 1
		self.approach_angle = .9
		self.barrel_point = pygame.math.Vector2(1, 1)

		# Auto commands
		self.auto = False
		self.auto_upgrade = None

		# # Bars on bays correspond to [w = miner, n = weapons, e = thrusters, s = hold]
		# self.bar_lengths = [0, 0, 0, 0]
		# self.bar_offsets = [0, 0, 0, 0]
		# self.bar_coords = [[[0,0],[0,0]], [[0,0],[0,0]], [[0,0],[0,0]], [[0,0],[0,0]]]

		self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
		# self.rgb = cfg.bay_colour
		# self.arrived_distance = cfg.bay_arrived_distance
		# self.interactable_distance = cfg.bay_interactable_distance
		self.approach_velocity = 1

		# Weapons
		self.active = True
		self.active = True
		self.shot_timer = 0
		self.ammo_type = None
		self.max_range = None
		self.ammo_count = 0

		self.owner.turrets.append(self)

	def choose_a_rand_target(self):
		spawner = random.choice(self.game.spawners)
		roamer = random.choice(spawner.roamers)
		return roamer

	def update_vector(self):
		self.location = (pygame.math.Vector2(self.x, self.y))

	def change_ammo(self, ammo):
		self.ammo_type = ammo

	def empty(self, ammo_type):
		pass

	def load(self, ammo_type):
		self.ammo_type = ammo_type
		self.max_range = cfg.ammo_info[ammo_type]["max_range"]

	def in_range(self, target):
		if self.location.distance_to(target.location) < self.weapon_range:
			return True

	def shoot(self):
		if self.hostile_target:
			new_projectile = Maul(self.rect.center - self.barrel_point * 16, self.barrel_point, self.game)
			self.game.projectiles.append(new_projectile)

	def update_locations(self):
		pass

	def turn_turret(self):
		if self.hostile_target:
			difference = pygame.Vector2(self.rect.center - self.hostile_target.location).normalize()
			self.barrel_point += difference * .02
			self.barrel_point = self.barrel_point.normalize()

	def draw(self):
		# Draw base
		pygame.draw.circle(self.screen, cfg.col.bone, self.rect.center, 6)
		pygame.draw.circle(self.screen, cfg.col.charcoal, self.rect.center, 8, 2)
		# pygame.draw.line(self.screen, [200, 20, 20], (self.rect.center), self.hostile_target.location)

	def draw_turret(self):
		if self.active:
			# draw barrel
			pygame.draw.line(self.screen, [255, 0, 0],
							 self.rect.center - self.barrel_point * 5, self.rect.center - self.barrel_point * 15, 5)
			pygame.draw.circle(self.screen, cfg.col.bone, self.rect.center - self.barrel_point * 6, 4)
			pygame.draw.circle(self.screen, [255, 0, 0], self.rect.center - self.barrel_point * 15, 2)
		else:
			pygame.draw.circle(self.screen, [0, 0, 0], self.rect.center, 3)

	def loop(self):
		if random.randint(0, 1000) > 999:
			self.hostile_target = self.choose_a_rand_target()
		if self.active:
			self.turn_turret()
		self.draw()
