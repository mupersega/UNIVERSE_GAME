import random

import pygame

from utility_classes import cfg
from environment_classes.class_asteroid import Asteroid
from environment_classes.class_explosion import Explosion


class Ship:
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

		self.miner_lvl = 0
		self.weapons_lvl = 0
		self.thrusters_lvl = 0
		self.hold_lvl = 0
		self.max_miner_lvl = 30
		self.max_weapons_lvl = 30
		self.max_hold_lvl = 30
		self.max_thrusters_lvl = 30
		self.hold_capacity = 10

		self.rect = pygame.Rect(self.location.x, self.location.y, self.image.get_width(), self.image.get_height())
		self.rgb = cfg.ent_rgb
		self.interactable_distance = cfg.ent_interactable_distance
		self.arrived_distance = cfg.ent_arrived_distance

		self.on_screen = True
		self.returning_to_base = False

		self.target = self.bay
		self.target_queue = []
		self.ores = [0, 0, 0]

		self.owner.entities.append(self)

		# self.choose_start_bay()
		self.rect.center = self.location
		# cfg.update_rect(self)

	def update_current_target(self):
		# If no target make current target the next target in queue.
		if not self.target:
			# no current target? make next in queue the current target
			if self.target_queue:
				self.target = self.target_queue.pop(0)
				return
			# no queue targets? Return to base (append return targets to queue)
			else:
				self.return_to_base()

		if cfg.on_screen_check_vec(self.target.location):
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
		if isinstance(t, Asteroid) and t.size <= 0:
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
				self.draw_beam(self.target)
				self.check_for_better_asteroid()
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

	def in_range(self, target, range):
		if cfg.distance_to_target(target) <= range:
			return True

	def find_asteroid(self):
		choices = []
		if self.bay.mine_priority:
			mineral_index = cfg.mineral_name_list.index(self.bay.mine_priority)
			[choices.append(asteroid) for asteroid in self.game.sorted_asteroid_lists[mineral_index] if asteroid.on_screen and asteroid.size > 0]
		# If no asteroids available
		if len(choices) == 0 or not self.bay.mine_priority:
			for sun in self.game.suns:
				for planet in sun.planets:
					if planet.on_screen:
						for asteroid in planet.asteroids:
							if asteroid.on_screen:
								choices.append(asteroid)
		if choices:
			return random.choice(choices)

	def check_for_better_asteroid(self):
		"""Check to see if the current asteroid you are mining is a priority if you have a priority set.
		if it is not a prioritized asteroid and there ARE priority asteroids on the field, then change target to
		one of them using the find_asteroid function."""
		# If a priority is set.
		if self.bay.mine_priority:
			mineral_index = cfg.mineral_name_list.index(self.bay.mine_priority)
			# If current target isn't a priority asteroid.
			if self.target not in self.game.sorted_asteroid_lists[mineral_index]:
				# If there is priority asteroid on field.
				if len([asteroid for asteroid in self.game.sorted_asteroid_lists[mineral_index] if asteroid.on_screen]):
					self.target = self.find_asteroid()

	def die(self):
		if self in self.owner.entities.copy():
			self.owner.entities.remove(self)
			self.game.explosions.append(
				Explosion(self.game, self.rect.center, random.randint(5,10), cfg.col.cerulean_frost))

	def draw(self):
		draw_image = pygame.transform.rotate(self.image, self.angle)
		pygame.draw.circle(self.screen, self.bay.prio_rgb, self.rect.center, 3)
		self.screen.blit(draw_image, self.rect)

	def draw_beam(self, target):
		pygame.draw.line(self.screen, self.bay.prio_rgb, self.rect.center, target.rect.center, 1)

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
