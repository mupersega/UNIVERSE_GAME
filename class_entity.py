import math
import random

import pygame

import cfg
from class_asteroid import Asteroid
from class_projectile import Projectile


class Entity:
	"""Any mobile object with complex behaviours. Entities/ships will always
	attach themselves to the bay in which they were created."""

	def __init__(self, bay):
		self.screen = bay.screen
		self.game = bay.hangar.station.game
		self.owner = bay.owner
		self.bay = bay
		self.behaviour = 'mine'
		self.image = cfg.ship_image

		self.x, self.y = bay.rect.center[0], bay.rect.center[1]
		self.size = cfg.ent_size
		self.width = self.size
		self.height = self.size

		# Navigation
		self.location = pygame.math.Vector2(bay.rect.center[0], bay.rect.center[1])
		self.trajectory = pygame.math.Vector2(1, 1)

		self.normal_vel = 1  # default 0.7
		self.vel = self.normal_vel
		self.approach_velocity = False
		self.normal_agility = 1
		self.agility = self.normal_agility
		self.angle = 0

		self.miner_lvl = 40
		self.weapons_lvl = 0
		self.thrusters_lvl = 20
		self.hold_lvl = 0
		self.max_miner_lvl = 50
		self.max_weapons_lvl = 30
		self.max_hold_lvl = 30
		self.max_thrusters_lvl = 30
		self.hold_capacity = 10

		self.rect = pygame.Rect(self.location.x, self.location.y, self.size, self.size)
		self.rgb = cfg.ent_rgb
		self.interactable_distance = cfg.ent_interactable_distance
		self.arrived_distance = cfg.ent_arrived_distance

		self.on_screen = True
		self.returning_to_base = False

		self.target = self.bay
		self.target_queue = []
		self.ores = [0, 0, 0]
		# print(self.ores)

		self.owner.entities.append(self)

		# self.choose_start_bay()
		cfg.update_rect(self)

	def update_current_target(self):
		# if no target make current target the next target in queue.
		if not self.target:
			# no current target? make next in queue the current target
			if self.target_queue:
				self.target = self.target_queue.pop(0)
				return
			# no queue targets? Return to base (append return targets to queue)
			else:
				self.return_to_base()

		if cfg.on_screen_check(self.target):
			# update to next target if in stop_distance of current, if none then return
			# print(self.target_queue)
			if len(self.target_queue) > 0:
				dist = cfg.distance_to_target(self)
				if dist <= self.target.arrived_distance:
					self.target = self.target_queue.pop(0)
					# set to approach velocity if target has an approach_velocity
					if self.target.approach_velocity:
						self.vel = self.target.approach_velocity
					else:
						self.vel = self.normal_vel
		else:
			if self.behaviour == "mine":
				new_asteroid = self.find_asteroid()
				if new_asteroid is not None and new_asteroid.on_screen:
					self.target = new_asteroid
			else:
				self.return_to_base()

	def move(self):
		# if not in arrived distance of target, turn and move toward target
		mod = 1
		dist = cfg.distance_to_target(self)

		if dist < 30:
			mod = dist / 40
		if dist > self.target.arrived_distance:
			self.update_location(mod)
		self.angle = cfg.angle_to_target(self)

	def update_location(self, mod):
		proposed_trajectory = pygame.math.Vector2(self.location - self.target.location)
		self.trajectory = proposed_trajectory.normalize()
		self.location -= self.trajectory * self.vel * mod
		self.rect.center = self.location
		self.x = self.location[0]
		self.y = self.location[1]

	def set_behaviour(self, behaviour):
		self.behaviour = behaviour
		if self.behaviour == "mine":
			self.find_asteroid()
		if self.behaviour == "stay":
			self.return_to_base()

	def interact(self):
		if not self.target:
			return
		t = self.target
		dist = cfg.distance_to_target(self)
		# if the target is a dead asteroid
		if isinstance(t, Asteroid) and t.size <= 0:\
			# find another asteroid
			self.target = self.find_asteroid()
			# if can not find a new asteroid: return to base
			if not self.target:
				self.return_to_base()
			return
		if dist <= t.interactable_distance:
			# Control interactions depending on the kind of target.
			# If target is an asteroid, then mine it until hold is full.
			if isinstance(t, Asteroid):
				if cfg.hold_at_capacity(self):
					self.return_to_base()
					return
				t.mine(self)
			# If target is home bay, return to bay and unload.
			if t is self.bay:
				if cfg.hold_empty(self):
					if len(self.target_queue) < 1:
						self.returning_to_base = False
						if self.behaviour == 'mine':
							new_target = self.find_asteroid()
							if new_target is not None:
								self.undock()
								self.target_queue.append(new_target)
						elif self.behaviour == 'stay':
							return
				else:
					t.unload(self)

	def undock(self):
		self.target_queue.append(self.bay.depart_location)
		self.target_queue.append(self.bay.hangar.depart_location)
		self.target_queue.append(self.bay.hangar.station.depart_location)

	def return_to_base(self):
		if self.target != self.bay:
			self.target_queue.clear()
			self.returning_to_base = True
			self.target = self.bay.hangar.station.approach_location
			self.target_queue.append(self.bay.hangar.approach_location)
			self.target_queue.append(self.bay.approach_location)
			self.target_queue.append(self.bay)

	def shoot(self):
		if self.target:
			new_projectile = Projectile(self, 1, self.target)
			self.game.projectiles.append(new_projectile)

	def in_range(self, target, range):
		if cfg.distance_to_target(target) <= range:
			return True

	def find_asteroid(self):
		choices = []
		for sun in self.game.suns:
			for planet in sun.planets:
				if planet.on_screen:
					for asteroid in planet.asteroids:
						if asteroid.on_screen:
							choices.append(asteroid)

		if choices:
			return random.choice(choices)

	def draw(self):
		draw_image = pygame.transform.rotate(self.image, self.angle)
		self.screen.blit(draw_image, self.rect)
		# pygame.draw.rect(self.screen, self.rgb, self.rect)

	def draw_beam(self, origin, target, colour=None):
		if colour is None:
			colour = [250, 250, 250]
		ox, oy = origin.x, origin.y
		tx, ty = target.x, target.y
		pygame.draw.line(self.screen, colour, (ox, oy), (tx, ty), 1)

	def draw_explosion(self, target):
		tx, ty = int(target.x), int(target.y)
		variance = [-4, -2, 2, 4]
		for _ in range(random.randint(20, 50)):
			pygame.draw.circle(self.screen, [255, 255, 255], (tx + random.choice(
				variance), ty + random.choice(variance)), random.randint(1, 5))
			pygame.draw.circle(self.screen, [0, 0, 0], (tx + random.choice(
				variance), ty + random.choice(variance)), random.randint(1, 5))
			pygame.draw.circle(self.screen, [255, 255, 255], (tx + random.choice(
				variance), ty + random.choice(variance)), random.randint(1, 5))

	def loop(self):
		self.update_current_target()
		self.move()
		self.interact()
		self.draw()
