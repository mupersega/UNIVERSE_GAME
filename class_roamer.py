import math
import random

import pygame

import cfg

from class_explosion import Explosion


class Roamer:
	"""Class to manage roaming hostiles which move around and attack miners."""
	def __init__(self, game, spawner):
		self.game = game
		self.screen = game.screen
		self.spawner = spawner
		# self.image = random.choice([cfg.big_ship_red, cfg.big_ship_teal, cfg.big_ship_red, cfg.big_ship_purple])
		self.image = cfg.starsated_image
		self.target_loc = pygame.math.Vector2(0, 0)
		self.location = pygame.math.Vector2(spawner.rect.center)
		self.hostile_target = None
		self.acceleration = pygame.math.Vector2(1, 1)
		self.bounce_force = pygame.Vector2(1, 1)
		self.last_loc = pygame.math.Vector2(spawner.rect.center)
		self.ang_vec = pygame.math.Vector2(0, 0)
		self.velocity = 1
		self.hunt_velocity = 2
		self.top_speed = 1.5
		self.hold = 0
		self.rect = pygame.Rect(0, 0, 10, 10)
		self.angle = 3
		self.life = 10
		self.hostile = True
		self.set_new_roam_location()

	def draw(self):
		pygame.draw.circle(self.screen, [255, 255, 255], self.target_loc, 1)
		draw_image = pygame.transform.rotate(self.image, self.angle)
		self.screen.blit(draw_image, (self.location[0] - 5, self.location[1] - 5))

	def feed(self):
		self.hold += 1
	
	def find_closest_spawner(self):
		s = self.spawner
		d = self.location.distance_to(s.location)
		for i in self.game.spawners:
			if self.location.distance_to(i.location) < d:
				d = self.location.distance_to(i.location)
				s = i
		return s

	def roam(self):
		# print(self.location.distance_to(self.target_loc))
		if self.hold > 1:
			self.target_loc = pygame.math.Vector2(self.find_closest_spawner().location)
			if self.location.distance_to(self.target_loc) < 3:
				self.spawner.hold += self.hold
				self.hold = 0
		if self.location.distance_to(self.target_loc) < 3 and self.hold < 2:
			self.set_new_roam_location()
			self.feed()
			print(self.hold)

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

	def rotate(self):
		t = self.hostile_target.rect.center if self.hostile else self.target_loc
		self.ang_vec = self.location - t
		rads = math.atan2(self.ang_vec[0], self.ang_vec[1])
		deg = math.degrees(rads)
		self.angle = deg

	def choose_hostile_target(self):
		if self.hostile_target:
			if self.hostile_target.life > 0:
				return
			else:
				self.hostile_target = None
		elif len(self.game.freighters) > 0:
			freighter = random.choice(self.game.freighters.copy())
			self.hostile_target = random.choice([i for i in freighter.full_train if i.life > 0])
		else:
			self.hostile = False

	def set_new_roam_location(self):
		w, h = cfg.screen_width / 4, cfg.screen_height / 4
		x_reg = random.choice([0, 1, 1, 2, 2, 2, 3, 3, 3, 3])
		y_reg = random.choice([0, 1, 1, 2, 2, 2, 3, 3, 3, 3])
		x = random.randint(0 + 10, w - 10)
		y = random.randint(0 + 10, h - 10)
		print(x_reg, x)
		self.target_loc[0] = x + (x_reg * w)
		self.target_loc[1] = y + (y_reg * h)
		self.last_loc = pygame.math.Vector2(self.location)

	def die(self):
		if self.life <= 0:
			self.game.hostiles.remove(self)
			# draw explosion
			new_explosion = Explosion(self.game, self.location, random.randint(5, 15), [255, 255, 255])
			self.game.explosions.append(new_explosion)

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

	def loop(self):
		self.die()
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
