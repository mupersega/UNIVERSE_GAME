import pygame
import random

import cfg

from class_maul import Maul
from class_lance import Lance
from class_bolt import Bolt


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
		self.hostile_target = None
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
		self.turret_rest_pos = pygame.Vector2(1920, self.hangar.rect.y)
		# self.ammo_type = random.choice(["lance", "maul", "bolt"])
		self.ammo_type = "bolt"
		self.max_range = cfg.ammo_info[self.ammo_type]["max_range"]
		self.barrel_rgb = cfg.ammo_info[self.ammo_type]["barrel_rgb"]
		self.shot_timer = 100
		self.heat = 0
		self.max_mag = 0
		self.ammo_count = 30

		self.owner.turrets.append(self)

	def choose_a_rand_target(self):
		hostiles_in_range = []
		self.game.main_quadtree.query_radius(self.location, self.max_range, hostiles_in_range)
		if hostiles_in_range:
			roamer = random.choice(hostiles_in_range)
			return roamer

	def update_vector(self):
		self.location = (pygame.math.Vector2(self.x, self.y))

	def change_ammo(self, ammo):
		self.ammo_type = ammo

	def empty(self, ammo_type):
		pass

	def load(self, ammo_type):
		self.ammo_type = ammo_type
		self.max_range = cfg.ammo_info[self.ammo_type]["max_range"]
		self.barrel_rgb = cfg.ammo_info[self.ammo_type]["barrel_rgb"]
		self.ammo_count = cfg.ammo_info[self.ammo_type]["mag_size"]
		self.max_mag = cfg.ammo_info[self.ammo_type]["mag_size"]

	def shoot(self):
		if self.hostile_target:
			if self.ammo_count <= 0:
				self.load(self.ammo_type)
			if self.heat > 100:
				self.shot_timer = 200
				return
			# MAUL
			if self.shot_timer <= 0 and self.ammo_type == "maul":
				self.barrel_point += (random.uniform(-0.1, 0.1), random.uniform(-0.1, 0.1))
				new_projectile = Maul(
					self.rect.center - self.barrel_point * 16, self.barrel_point, None, self.game)
				self.game.projectiles.append(new_projectile)
				self.shot_timer = 1
				self.heat += 5
				self.ammo_count -= 1
			# LANCE
			if self.shot_timer <= 0 and self.ammo_type == "lance":
				self.barrel_point += random.choice(cfg.turret_shake)
				new_projectile = Lance(
					self.rect.center - self.barrel_point * 16, self.barrel_point, self.hostile_target, self.game)
				self.game.projectiles.append(new_projectile)
				self.shot_timer = 150
				self.heat += 50
				self.ammo_count -= 1
			# BOLT
			if self.shot_timer <= 0 and self.ammo_type == "bolt":
				self.barrel_point += random.choice(cfg.turret_shake)
				new_projectile = Bolt(
					self.rect.center - self.barrel_point * 16, self.barrel_point, self.hostile_target, self.game)
				self.game.projectiles.append(new_projectile)
				self.shot_timer = 400
				self.heat += 1
				self.ammo_count -= 1

	def update_locations(self):
		pass

	def target_checks(self):
		# check if target is in range and still alive, if not, remove target. If no target, search for new target.
		if self.hostile_target:
			# if target in range
			if self.location.distance_to(self.hostile_target.location) < self.max_range:
				# if target is dead remove it
				if self.hostile_target.life <= 0:
					self.hostile_target = None
					return
				# if target is alive shoot it
				self.shoot()
			else:
				self.hostile_target = None
		else:
			self.hostile_target = self.choose_a_rand_target()

	def turn_turret(self):
		# if turret has a target, turn towards the target.
		if self.hostile_target:
			difference = pygame.Vector2(self.rect.center - self.hostile_target.location).normalize()
			self.barrel_point += difference * .05
			self.barrel_point = self.barrel_point.normalize()
		# if no target, turn turret towards resting position.
		else:
			difference = pygame.Vector2(self.rect.center - self.turret_rest_pos).normalize()
			self.barrel_point += difference * .05
			self.barrel_point = self.barrel_point.normalize()

	def draw(self):
		# Draw base
		# pygame.draw.circle(self.screen, cfg.col.bone, self.rect.center, 6)
		pygame.draw.circle(self.screen, cfg.col.charcoal, self.rect.center, 9, 2)
	# if self.hostile_target:
	# pygame.draw.line(self.screen, [50, 5, 5], (self.rect.center), self.hostile_target.location)

	def draw_turret(self):
		# barrel
		pygame.draw.line(self.screen, self.barrel_rgb,
						 self.rect.center - self.barrel_point * 5, self.rect.center - self.barrel_point * 15, 5)
		# moving small circle
		pygame.draw.circle(self.screen, cfg.col.bone, self.rect.center - self.barrel_point * 8, 4)
		# barrel circle
		pygame.draw.circle(self.screen, self.barrel_rgb, self.rect.center - self.barrel_point * 15, 2)

	def loop(self):
		if self.active:
			if self.shot_timer > 0:
				self.shot_timer -= 1
			if self.heat > 0:
				self.heat -= 1
			self.target_checks()
			self.turn_turret()
		self.draw()
