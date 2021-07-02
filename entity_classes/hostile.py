import math
import random

import pygame

from utility_classes import cfg

from environment_classes.class_explosion import Explosion


class Hostile:
	"""Class to manage roaming hostiles which move around and attack miners."""
	def __init__(self, game, spawner, location):
		self.game = game
		self.screen = game.screen
		self.spawner = spawner
		# self.image = random.choice([cfg.big_ship_red, cfg.big_ship_teal, cfg.big_ship_red, cfg.big_ship_purple])

		self.target_loc = pygame.math.Vector2(0, 0)
		self.drop_nodule = None
		self.location = pygame.math.Vector2(location)
		self.hostile_target = None
		self.acceleration = pygame.math.Vector2(1, 1)
		self.bounce_force = pygame.Vector2(1, 1)
		self.last_loc = pygame.math.Vector2(spawner.rect.center)
		self.ang_vec = pygame.math.Vector2(0, 0)
		self.velocity = 1.5
		self.hunt_velocity = 3
		self.top_speed = 1.5

		self.angle = 3
		self.hostile = True
		self.last_hit = None

		# pygame.draw.circle(self.screen, [50, 50, 50], self.location, self.perception_range, width=1)
		# if self.hostile_target:
		# 	pygame.draw.line(self.screen, [255, 255, 255], self.location, self.hostile_target.location, 1)

	def find_nearby_random_dropoff(self):
		s = self.spawner
		d = self.location.distance_to(s.location)
		for i in self.game.spawners:
			if self.location.distance_to(i.location) < d:
				d = self.location.distance_to(i.location)
				s = i
		return random.choice(s.nodules)

	def rotate(self):
		t = self.target_loc
		self.ang_vec = self.location - t
		rads = math.atan2(self.ang_vec[0], self.ang_vec[1])
		deg = math.degrees(rads)
		self.angle = deg

	def poly_explosion(self):
		pc = random.choice(cfg.bolt_coord_array)
		ctr = pygame.Vector2(self.hostile_target.rect.center)
		pygame.draw.lines(self.game.screen, [255, 0, 0], closed=False, points=[
			ctr + pc[0],
			ctr + pc[1],
			ctr + pc[2],
			ctr + pc[3],
		])
		pc = random.choice(cfg.bolt_coord_array)
		pygame.draw.polygon(self.game.screen, [255, 200, 230], [
			ctr + pc[0],
			ctr + pc[1],
			ctr + pc[2],
			ctr + pc[3],
		])

	def die(self):
		if self.life <= 0 and self in self.game.hostiles.copy():
			self.game.hostiles.remove(self)
			# draw explosion
			new_explosion = Explosion(self.game, self.location, random.randint(5, 15), [255, 255, 255])
			self.game.explosions.append(new_explosion)
			if self.last_hit:
				self.last_hit.kills += 1
				self.game.leaderboard.update()


class Drone(Hostile):
	"""Implement an instance of a drone. Drone behavioural priority is as follows:
	1 - Target and destroy freighters,
	2 - Gather stardust and drop it at a random nodule on the nearest spawner."""
	def __init__(self, game, spawner, location):
		super().__init__(game, spawner, location)
		self.hold = 0
		self.image = cfg.starsated_image
		self.rect = pygame.Rect(0, 0, self.image.get_rect().width, self.image.get_rect().height)
		self.life = 10

		self.set_new_roam_location()

	def set_new_roam_location(self):
		# roam_range = 400
		# FULL SCREEN ROAM
		w, h = cfg.screen_width / 4, cfg.screen_height / 4
		x_reg = random.choice([0, 1, 1, 2, 2, 2, 3, 3, 3, 3])
		y_reg = random.choice([0, 1, 1, 2, 2, 2, 3, 3, 3, 3])
		x = random.randint(0 + 10, w - 10)
		y = random.randint(0 + 10, h - 10)
		# print(x_reg, x)
		self.target_loc[0] = x + (x_reg * w)
		self.target_loc[1] = y + (y_reg * h)
		# NEARBY ROAM
		# x_lower = max([0, self.rect.centerx - roam_range])
		# x_upper = min([cfg.screen_width, self.rect.centerx + roam_range])
		# y_lower = max([0, self.rect.centery - roam_range])
		# y_upper = min([cfg.screen_width, self.rect.centery + roam_range])
		# self.target_loc[0] = self.location.x + random.randint(x_lower, x_upper)
		# self.target_loc[1] = self.location.y + random.randint(y_lower, y_upper)
		self.last_loc = pygame.math.Vector2(self.location)

	def roam(self):
		if self.hold > 1:
			if self.drop_nodule:
				if self.location.distance_to(self.target_loc) < 3:
					self.drop_nodule.accept_resources(self.hold)
					self.hold = 0
					self.drop_nodule = None
			else:
				self.drop_nodule = self.find_nearby_random_dropoff()
				self.target_loc = pygame.math.Vector2(self.drop_nodule.location)
		if self.location.distance_to(self.target_loc) < 3 and self.hold < 2:
			self.set_new_roam_location()
			self.feed()

	def feed(self):
		self.hold += 1

	def hunt(self):
		if self.hostile_target:
			if self.rect.colliderect(self.hostile_target.rect):
				self.hostile_target.take_damage(.5)
				self.bounce_force = pygame.Vector2(random.uniform(-4, 4), random.uniform(-4, 4))
				self.poly_explosion()
				return
			self.bounce_force *= 0.95
			self.acceleration = self.location - self.hostile_target.rect.center
			self.location -= self.acceleration.normalize() * self.hunt_velocity + self.bounce_force
			self.rect.topleft = self.location

	def choose_hostile_target(self):
		if self.hostile_target:
			if self.hostile_target.life > 0:
				return
			self.hostile_target = None
			self.velocity = 1
		elif len(self.game.freighters) > 0:
			freighter = random.choice([i for i in self.game.freighters.copy() if cfg.on_screen_check_vec(i.full_train[0].location)])
			try:
				self.hostile_target = random.choice([i for i in freighter.full_train if i.life > 0])
			except:
				self.last_loc = pygame.math.Vector2(self.location)
				return
		else:
			self.hostile = False
			self.hostile_target = None
			self.velocity = 1

	def draw(self):
		pygame.draw.circle(self.screen, [255, 255, 255], self.target_loc, 1)
		draw_image = pygame.transform.rotate(self.image, self.angle)
		self.screen.blit(draw_image, (self.location[0] - 5, self.location[1] - 5))

	def move(self):
		mod_range = 50
		dist_from = self.location.distance_to(self.last_loc)
		dist_to = self.location.distance_to(self.target_loc)
		if dist_from < mod_range:
			self.velocity = self.top_speed * (dist_from + 1) / mod_range
		elif dist_to < mod_range:
			self.velocity = dist_to * self.top_speed / mod_range
		self.acceleration = self.location - self.target_loc
		self.location -= self.acceleration.normalize() * self.velocity
		self.rect.topleft = self.location

	def loop(self):
		self.die()
		self.roam()
		self.move()
		self.rotate()
		self.draw()


class HunterDrone(Hostile):
	"""Implement an instance of a drone. Drone behavioural priority is as follows:
	1 - Target and destroy freighters,
	2 - Gather stardust and drop it at a random nodule on the nearest spawner."""
	def __init__(self, game, spawner, location):
		super().__init__(game, spawner, location)
		self.hold = 0
		self.image = cfg.hunterdrone_image
		self.rect = pygame.Rect(0, 0, self.image.get_rect().width, self.image.get_rect().height)
		self.life = 50
		self.damage = 5

		self.set_new_roam_location()

	def rotate(self):
		t = self.target_loc
		if self.hostile_target:
			t = self.hostile_target.rect.center
		self.ang_vec = self.location - t
		rads = math.atan2(self.ang_vec[0], self.ang_vec[1])
		deg = math.degrees(rads)
		self.angle = deg

	def set_new_roam_location(self):
		# roam_range = 400
		# FULL SCREEN ROAM
		w, h = cfg.screen_width / 4, cfg.screen_height / 4
		x_reg = random.choice([0, 1, 1, 2, 2, 2, 3, 3, 3, 3])
		y_reg = random.choice([0, 1, 1, 2, 2, 2, 3, 3, 3, 3])
		x = random.randint(0 + 10, w - 10)
		y = random.randint(0 + 10, h - 10)
		# print(x_reg, x)
		self.target_loc[0] = x + (x_reg * w)
		self.target_loc[1] = y + (y_reg * h)
		# NEARBY ROAM
		# x_lower = max([0, self.rect.centerx - roam_range])
		# x_upper = min([cfg.screen_width, self.rect.centerx + roam_range])
		# y_lower = max([0, self.rect.centery - roam_range])
		# y_upper = min([cfg.screen_width, self.rect.centery + roam_range])
		# self.target_loc[0] = self.location.x + random.randint(x_lower, x_upper)
		# self.target_loc[1] = self.location.y + random.randint(y_lower, y_upper)
		self.last_loc = pygame.math.Vector2(self.location)

	def roam(self):
		if self.hold > 1:
			if self.drop_nodule:
				if self.location.distance_to(self.target_loc) < 3:
					self.drop_nodule.accept_resources(self.hold)
					self.hold = 0
					self.drop_nodule = None
			else:
				self.drop_nodule = self.find_nearby_random_dropoff()
				self.target_loc = pygame.math.Vector2(self.drop_nodule.location)
		if self.location.distance_to(self.target_loc) < 3 and self.hold < 2:
			self.set_new_roam_location()
			self.feed()

	def feed(self):
		self.hold += 1

	def hunt(self):
		if self.hostile_target:
			if self.rect.colliderect(self.hostile_target.rect):
				self.hostile_target.take_damage(self.damage)
				self.bounce_force = pygame.Vector2(random.uniform(-4, 4), random.uniform(-4, 4))
				self.poly_explosion()
				return
			self.bounce_force *= 0.95
			self.acceleration = self.location - self.hostile_target.rect.center
			self.location -= self.acceleration.normalize() * self.hunt_velocity + self.bounce_force
			self.rect.topleft = self.location

	def choose_hostile_target(self):
		if self.hostile_target:
			if self.hostile_target.life > 0:
				return
			self.hostile_target = None
			self.velocity = 1
		elif len(self.game.freighters) > 0:
			freighter = random.choice([i for i in self.game.freighters.copy() if cfg.on_screen_check_vec(i.full_train[0].location)])
			try:
				self.hostile_target = random.choice([i for i in freighter.full_train if i.life > 0])
			except:
				self.last_loc = pygame.math.Vector2(self.location)
				return
		else:
			self.hostile = False
			self.hostile_target = None
			self.velocity = 1

	def draw(self):
		pygame.draw.circle(self.screen, [255, 255, 255], self.target_loc, 1)
		draw_image = pygame.transform.rotate(self.image, self.angle)
		self.screen.blit(draw_image, (self.location[0] - 5, self.location[1] - 5))

	def move(self):
		mod_range = 50
		dist_from = self.location.distance_to(self.last_loc)
		dist_to = self.location.distance_to(self.target_loc)
		if dist_from < mod_range:
			self.velocity = self.top_speed * (dist_from + 1) / mod_range
		elif dist_to < mod_range:
			self.velocity = dist_to * self.top_speed / mod_range
		self.acceleration = self.location - self.target_loc
		self.location -= self.acceleration.normalize() * self.velocity
		self.rect.topleft = self.location

	def loop(self):
		self.die()
		if len([i for i in self.game.freighters if cfg.on_screen_check_vec(i.full_train[0].location)]) > 0:
			self.hostile = True
		else:
			self.hostile = False
			self.hostile_target = False

		if self.hostile:
			self.choose_hostile_target()
			if self.hostile_target:
				self.hunt()
				self.rotate()
		else:
			self.roam()
			self.move()
			self.rotate()
		self.draw()


class Soldier(Hostile):
	"""Implement an instance of a drone. Drone behavioural priority is as follows:
		1 - Target and destroy freighters,
		2 - Target and destroy nearest player's right-most (last in list) facility."""
	def __init__(self, game, spawner, location):
		super().__init__(game, spawner, location)
		self.velocity = pygame.Vector2(0, 0)
		self.hold = 0
		self.image = cfg.soldier_image
		self.rect = pygame.Rect(0, 0, self.image.get_rect().width, self.image.get_rect().height)
		self.life = 200
		self.damage = 10

	def acquire_target(self, attr):
		new_target = None
		if len(self.game.freighters):
			freighter = random.choice(
				[i for i in self.game.freighters.copy() if cfg.on_screen_check_vec(i.full_train[0].location)])
			try:
				return random.choice([i for i in freighter.full_train if i.life > 0])
			except:
				return
		else:
			# do a random roll and if less than or equal to players kill priority then target their right-most facility
			for i in [j for j in self.game.leaderboard.return_ordered_players(attr, True) if j.hangars[0].facilities]:
				if random.randint(0, self.game.max_kill_prio + len(self.game.players) * 1) <= i.kill_priority:
					new_target = i.hangars[0].facilities[-1]
					break
			if new_target:
				return new_target
			return random.choice([i for i in self.game.players if i.hangars[0].facilities]).hangars[0].facilities[-1]

	def move(self):
		# mod_range = 50
		# dist_from = self.location.distance_to(self.last_loc)
		# dist_to = self.location.distance_to(self.target_loc)
		# if dist_from < mod_range:
		# 	self.velocity = self.top_speed * (dist_from + 1) / mod_range
		# elif dist_to < mod_range:
		# 	self.velocity = dist_to * self.top_speed / mod_range
		self.rotate()
		try:
			self.acceleration = pygame.Vector2(
				self.rect.centerx - self.hostile_target.rect.centerx,
				self.rect.centery - self.hostile_target.rect.centery).normalize()
		except ValueError:
			return
		self.velocity += self.acceleration * .1
		self.velocity = self.clamp_norm(self.velocity, 1)
		self.location -= self.velocity
		self.rect.topleft = self.location

	def check_collision(self):
		if self.hostile_target:
			if cfg.distance_to_select_target(self, self.hostile_target) < self.rect.width:
				self.hostile_target.take_damage(2)
				self.velocity -= self.acceleration.rotate(random.randint(-20, 20)) * random.randint(5, 20)
				self.poly_explosion()
				return

	@staticmethod
	def clamp_norm(vec, n_max):
		n = math.sqrt(vec.x ** 2 + vec.y ** 2)
		f = min(n, n_max) / n
		return vec * f

	def rotate(self):
		self.ang_vec = pygame.Vector2(self.rect.center) - self.hostile_target.rect.center
		rads = math.atan2(self.ang_vec[0], self.ang_vec[1])
		deg = math.degrees(rads)
		self.angle = deg

	def draw(self):
		pygame.draw.circle(self.screen, [255, 255, 255], self.target_loc, 1)
		draw_image = pygame.transform.rotate(self.image, self.angle)
		self.screen.blit(draw_image, self.rect.topleft)

	def draw_line_to_target(self):
		pygame.draw.line(self.game.screen, [60, 0, 0], self.rect.center, self.hostile_target.rect.center)

	def loop(self):
		self.die()
		# if current target dead find new target
		if self.hostile_target:
			# move to target
			self.move()
			# self.draw_line_to_target()
			# if in range attack target
			self.check_collision()
			if self.hostile_target.life <= 0 or not cfg.on_screen_check_vec(self.hostile_target.location):
				self.hostile_target = None
				return
		else:
			try:
				self.hostile_target = self.acquire_target("kills")
			except IndexError:
				self.die()
		# draw
		self.draw()

