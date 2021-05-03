import pygame

import cfg
from class_entity import Entity
# from class_warehouse import Warehouse
from class_projectile import Projectile


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
		self.target = self.game.spawners[0].roamers[0]
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
		self.shot_timer = 0
		self.ammo_type = None
		self.max_range = None
		self.ammo_count = 0

		self.owner.turrets.append(self)

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
		if self.target:
			new_projectile = Projectile(self, 1, self.target)
			self.game.projectiles.append(new_projectile)

	def combat(self):
		if self.target:
			if self.in_range(self.target):
				if self.ammo_count > 1:
					self.aim()
					self.shoot()

	def update_locations(self):
		pass

	def turn_turret(self):
		if self.target:
			self.barrel_point = self.rect.center - self.target.location
			self.barrel_point = self.barrel_point.normalize() * 15

	def draw(self):
		x = self.location[0]
		y = self.location[1]
		# Draw base
		pygame.draw.rect(self.screen, cfg.col.pumpkin,
				(x + cfg.x_pad, y + cfg.y_pad, - cfg.facility_w * .5, - cfg.facility_h))
		# draw housing
		pygame.draw.circle(
			self.screen, cfg.col.cerulean_frost, self.rect.center, 10, draw_top_right=True, draw_bottom_right=True)
		pygame.draw.circle(self.screen, cfg.col.cerulean_blue, self.rect.center, 5)
		# draw barrel
		pygame.draw.line(self.screen, cfg.col.bone, self.rect.center, self.rect.center - self.barrel_point, 3)
		# draw ammo

	def loop(self):
		self.turn_turret()
		self.draw()
