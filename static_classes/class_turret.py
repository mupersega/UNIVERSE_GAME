import pygame
import random
import math

from utility_classes import cfg

from projectile_classes.class_maul import Maul
from projectile_classes.class_lance import Lance
from projectile_classes.class_bolt import Bolt
from environment_classes.class_explosion import Explosion


class Turret:
	def __init__(self, hangar):
		self.screen = hangar.station.game.screen
		self.hangar = hangar
		self.game = hangar.station.game
		self.owner = hangar.owner
		self.kind = 'turret'
		self.index = 1
		self.on_screen = True
		self.boosted = False

		self.x = 1
		self.y = 1
		self.location = pygame.math.Vector2(self.x, self.y)
		self.hostile_target = None
		self.width = cfg.facility_w
		self.height = cfg.facility_h
		self.diameter = cfg.facility_w_two_third
		self.approach_velocity = 1
		self.approach_angle = .9
		self.barrel_point = pygame.math.Vector2(-1, 0)

		# Damage information
		self.life = 100

		# Auto commands
		self.auto = False
		self.auto_upgrade = None

		self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
		self.approach_velocity = 1

		# Weapons
		self.level = 1
		self.active = True
		self.turret_rest_pos = pygame.Vector2(1920, self.hangar.rect.y)
		self.ammo_type = random.choice(["lance", "maul", "bolt"])
		self.ammo_type = "maul"
		self.max_range = cfg.ammo_info[self.ammo_type]["max_range"]
		self.barrel_rgb = cfg.ammo_info[self.ammo_type]["barrel_rgb"]
		self.ammo_hold_rgb = cfg.ammo_info[self.ammo_type]["ammo_hold_rgb"]
		self.max_mag = cfg.ammo_info[self.ammo_type]["mag_size"]
		self.shot_timer = 100
		self.heat = 0
		self.ammo_count = cfg.ammo_info[self.ammo_type]["mag_size"]

		self.owner.turrets.append(self)

	def choose_a_rand_target(self):
		hostiles_in_range = []
		self.game.hostile_quadtree.query_radius(self.rect.center, self.max_range, hostiles_in_range)
		if hostiles_in_range:
			return random.choice(hostiles_in_range)

	def update_vector(self):
		self.location = (pygame.math.Vector2(self.x, self.y))

	def change_ammo(self, ammo):
		self.ammo_type = ammo

	def empty(self, ammo_type):
		pass

	def load(self, ammo_type):
		if cfg.resource_check(
				cfg.ammo_info[ammo_type]["reload_resources"], cfg.tally_resources(self.owner)):
			cfg.withdraw_resources(self.owner, cfg.ammo_info[ammo_type]["reload_resources"])
			self.ammo_type = ammo_type
			self.max_range = cfg.ammo_info[self.ammo_type]["max_range"]
			self.barrel_rgb = cfg.ammo_info[self.ammo_type]["barrel_rgb"]
			self.ammo_count = cfg.ammo_info[self.ammo_type]["mag_size"]
			self.max_mag = cfg.ammo_info[self.ammo_type]["mag_size"]
			self.ammo_hold_rgb = cfg.ammo_info[self.ammo_type]["ammo_hold_rgb"]
			self.active = True
		else:
			self.deactivate()

	def shoot(self):
		if not self.hostile_target:
			return
		if self.ammo_count <= 0:
			self.load(self.ammo_type)
			self.shot_timer = cfg.ammo_info[self.ammo_type]["reload_time"]
		if self.heat > 100:
			self.shot_timer = 200
			return
		# MAUL
		# LEVEL EFFECTS - Number of projectiles launched. #
		if self.shot_timer <= 0 and self.ammo_type == "maul":
			self.barrel_point += (random.uniform(-0.1, 0.1), random.uniform(-0.1, 0.1))
			new_projectile = Maul(
				self.rect.center - self.barrel_point * 16, self.barrel_point, None, self.game, self.owner)
			for _ in range(self.level):
				self.add_projectile_and_update(new_projectile, 2, 2)
		# LANCE
		# LEVEL EFFECTS - Number of projectiles launched. #
		if self.shot_timer <= 0 and self.ammo_type == "lance":
			self.barrel_point += random.choice(cfg.turret_shake)
			new_projectile = Lance(
				self.rect.center - self.barrel_point * 16, self.barrel_point, self.hostile_target, self.game, self.owner)
			self.add_projectile_and_update(new_projectile, 150, 50)
		# BOLT
		# LEVEL EFFECTS - Extra targets after first. #
		if self.shot_timer <= 0 and self.ammo_type == "bolt":
			self.barrel_point += random.choice(cfg.turret_shake)
			new_projectile = Bolt(
				self.rect.center - self.barrel_point * 16, self.barrel_point, self.hostile_target, self.game, self.owner, self.level)
			self.add_projectile_and_update(new_projectile, 250, 1)

	def add_projectile_and_update(self, new_projectile, shot_time, heat_change):
		self.game.projectiles.append(new_projectile)
		self.shot_timer = shot_time
		self.heat += heat_change
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
		# If turret has a target, turn towards the target.
		ht = self.hostile_target
		if ht:
			difference = pygame.Vector2(
				self.rect.center - ht.location).normalize()
			self.barrel_point += difference * .08
		else:
			self.turret_rest_pos = self.barrel_point.normalize()
			# difference = pygame.Vector2(self.rect.center - self.turret_rest_pos).normalize()

		self.barrel_point = self.barrel_point.normalize()

	def draw(self):
		# Draw base
		# Draw ammo hold (background)
		pygame.draw.rect(self.screen, self.ammo_hold_rgb, (
			self.rect.centerx - 2, self.rect.centery - cfg.facility_h_third, cfg.turret_ammo_bar_w, cfg.facility_h_two_third))
		# Draw ammo bar
		bar_length = math.ceil(self.ammo_count / self.max_mag * cfg.facility_h_two_third)
		pygame.draw.line(self.screen, self.barrel_rgb, [
			self.rect.centerx - 1, self.rect.centery + cfg.facility_h_third - 1], [
			self.rect.centerx - 1, self.rect.centery + cfg.facility_h_third - bar_length], 4)
		pygame.draw.circle(self.screen, cfg.col.medium_grey, self.rect.center, cfg.facility_w_third, 2)
		# Draw weapon range
		# pygame.draw.circle(self.screen, self.barrel_rgb, self.rect.center, self.max_range, 1)

	# if self.hostile_target:
	# pygame.draw.line(self.screen, [50, 5, 5], (self.rect.center), self.hostile_target.location)

	def draw_turret(self):
		if self.active:
			# barrel
			pygame.draw.line(self.screen, self.barrel_rgb,
							 self.rect.center - self.barrel_point * cfg.facility_w_third, self.rect.center - self.barrel_point * cfg.facility_w_two_third, 5)
			# barrel circle
			pygame.draw.circle(self.screen, self.barrel_rgb, self.rect.center - self.barrel_point * cfg.facility_w_third * 2, 2)
		# moving small circle
		pygame.draw.circle(self.screen, cfg.col.white, self.rect.center - self.barrel_point * cfg.facility_w_third, 4)

	def activate(self):
		self.active = True

	def deactivate(self):
		self.active = False

	def take_damage(self, amt):
		self.life -= amt
		if self.life <= 0:
			self.die()

	def die(self):
		if self in self.hangar.facilities.copy():
			self.hangar.facilities.remove(self)
			self.hangar.turrets.remove(self)
			self.hangar.set_facilities_pos()
			self.game.explosions.append(Explosion(self.game, self.rect.center, 20, self.ammo_hold_rgb))

	def loop(self):
		if self.active:
			if self.shot_timer > 0:
				self.shot_timer -= 1
			if self.heat > 0:
				self.heat -= 1
			self.target_checks()
			self.turn_turret()
		self.draw()
