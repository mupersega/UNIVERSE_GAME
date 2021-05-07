import pygame
import cfg
import random
import numpy as np

from class_explosion import Explosion

class Bolt:
	"""The bolt ammunition type is the 'missile' class, it is assigned a target on init and will move towards it. It is
	the ammo type that has the most physics applied to it. It will adopt an initial velocity vector derived from the
	turrets barrel direction."""
	def __init__(self, start_loc, trajectory, target, game):
		self.game = game
		self.target = target
		self.location = pygame.Vector2(start_loc - trajectory * 10)
		# self.launch_velocity = pygame.Vector2(trajectory)
		self.thrust = pygame.Vector2(0, 0)
		self.velocity = pygame.Vector2(0, 0)
		self.acceleration = pygame.Vector2(0, 0)
		self.wobble = pygame.Vector2(0, 0)
		self.rect = pygame.Rect(self.location.x, self.location.y, 10, 10)
		pygame.draw.circle(self.game.screen, [250, 240, 255], self.location, random.randint(1, 4))
		self.trail = [pygame.Vector2(self.location), pygame.Vector2(self.location)]
		self.trail_2 = [pygame.Vector2(self.location), pygame.Vector2(self.location)]
		self.trail_3 = [pygame.Vector2(self.location), pygame.Vector2(self.location)]

		self.life = random.randint(60, 80) * 5
		self.game.explosions.append(Explosion(self.game, start_loc, 4))

	def apply_force(self, force):
		self.acceleration += force

	def update(self):
		d = self.location.distance_to(self.target.location)
		self.wobble = (random.uniform(-1, 1), random.uniform(-1, 1))
		self.thrust = (self.location - self.target.location).normalize()
		# self.push = (self.target.location - self.location).normalize() / d
		# self.push = (self.target.location - self.location).normalize()

	def move(self):
		self.update()
		# self.apply_force(self.push)
		self.apply_force(self.thrust)
		self.apply_force(self.wobble)
		self.velocity += self.acceleration
		self.velocity *= .94
		self.location -= self.velocity * .6
		self.acceleration *= 0
		self.life -= 1
		if self.life % 6 == 0:
			self.trail.append(
				[self.location.x + random.randrange(-10, 10), self.location.y + random.randrange(-10, 10)])
			if self.life % 12 == 0:
				self.trail_2.append(
					[self.location.x + random.randrange(-30, 30), self.location.y + random.randrange(-30, 30)])
				if self.life % 18 == 0:
					self.trail_3.append(
						[self.location.x + random.randrange(-40, 40), self.location.y + random.randrange(-40, 40)])

	def kill(self):
		if self.target.life <= 0:
			self.life *= .95
		if self.life < 1:
			if self in self.game.projectiles:
				self.game.projectiles.remove(self)

	def check_collision(self):
		nearby_hits = []
		self.game.main_quadtree.query(self.rect, nearby_hits)
		for i in nearby_hits:
			if pygame.Rect.colliderect(self.rect, i.rect):
				self.trail.append(
					[self.location.x + random.randrange(-10, 10), self.location.y + random.randrange(-10, 10)])
				self.trail_2.append(
					[self.location.x + random.randrange(-10, 10), self.location.y + random.randrange(-10, 10)])
				self.trail_3.append(
					[self.location.x + random.randrange(-10, 10), self.location.y + random.randrange(-10, 10)])
				pygame.draw.lines(self.game.screen, [0, 0, 200], closed=False, points=self.trail)
				pygame.draw.lines(self.game.screen, [130, 0, 140], closed=False, points=self.trail_2, width=2)
				pygame.draw.lines(self.game.screen, [130, 130, 240], closed=False, points=self.trail_3, width=3)
				# pygame.draw.line(self.game.screen, [220, 220, 220], self.trail[0], self.location, width=3)
				i.location -= self.velocity.normalize() * 1
				i.life -= 20
				self.life -= 20
		# for i in self.game.spawners:
		# 	for j in i.roamers:
		# 		if pygame.Rect.colliderect(self.rect, j.rect):
		# 			self.poly_explosion()
		# 			j.life -= 1
		# 			self.life = 0
		# 			self.kill()

	def poly_explosion(self):
		pc = random.choice(cfg.bolt_coord_array)
		pygame.draw.polygon(self.game.screen, [255, 0, 0], [
			self.location + pc[0],
			self.location + pc[1],
			self.location + pc[2],
			self.location + pc[3],
		])
		pc = random.choice(cfg.bolt_coord_array)
		pygame.draw.polygon(self.game.screen, [255, 200, 255], [
			self.location + pc[0],
			self.location + pc[1],
			self.location + pc[2],
			self.location + pc[3],
		])

	def apply_damage(self, hit_object):
		pass

	def draw(self):
		pc = random.choice(cfg.bolt_coord_array)
		pygame.draw.lines(self.game.screen, [0, 0, 255], closed=False, points=(
			self.location + pc[0],
			self.location + pc[1],
			self.location + pc[2],
			self.location + pc[3],
		), width=2)
		pc = random.choice(cfg.bolt_coord_array)
		pygame.draw.lines(self.game.screen, [200, 0, 255], closed=False, points=(
			self.location + pc[0],
			self.location + pc[1],
			self.location + pc[2],
			self.location + pc[3],
		))

	def update_rect(self):
		self.rect.topleft = self.location

	def loop(self):
		self.kill()
		self.check_collision()
		self.move()
		self.update_rect()
		self.draw()