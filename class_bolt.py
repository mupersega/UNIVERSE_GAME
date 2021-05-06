import pygame
import cfg
import random
import numpy as np

class Bolt:
	"""The bolt ammunition type is the 'missile' class, it is assigned a target on init and will move towards it. It is
	the ammo type that has the most physics applied to it. It will adopt an initial velocity vector derived from the
	turrets barrel direction."""
	def __init__(self, start_loc, trajectory, target, game):
		self.game = game
		self.target = target
		self.location = pygame.Vector2(start_loc)
		# self.launch_velocity = pygame.Vector2(trajectory)
		self.thrust = pygame.Vector2(0, 0)
		self.velocity = pygame.Vector2(0, 0)
		self.acceleration = pygame.Vector2(0, 0)
		self.wobble = pygame.Vector2(0, 0)
		self.rect = pygame.Rect(self.location.x, self.location.y, 5, 5)
		pygame.draw.circle(self.game.screen, [250, 240, 255], self.location, random.randint(1, 4))

		self.life = random.randint(60, 80) * 4

	def apply_force(self, force):
		self.acceleration += force

	def update(self):
		# d = self.location.distance_to(self.target.location)
		# self.launch_velocity *= .95
		self.wobble = (random.uniform(-1, 1), random.uniform(-1, 1))
		self.thrust = (self.location - self.target.location).normalize()
		# self.push = (self.target.location - self.location).normalize()

	def move(self):
		self.update()
		# self.apply_force(self.launch_velocity)
		self.apply_force(self.thrust)
		self.apply_force(self.wobble)
		self.velocity += self.acceleration
		self.velocity *= .95
		self.location -= self.velocity * .5
		self.acceleration *= 0
		# self.life -= 1

	def kill(self):
		if self.life < 1:
			if self in self.game.projectiles:
				self.game.projectiles.remove(self)

	def check_collision(self):
		nearby_hits = []
		self.game.main_quadtree.query(self.rect, nearby_hits)
		for i in nearby_hits:
			if pygame.Rect.colliderect(self.rect, i.rect):
				self.poly_explosion()
				i.life -= 1
				self.life = 0
				self.kill()
		# for i in self.game.spawners:
		# 	for j in i.roamers:
		# 		if pygame.Rect.colliderect(self.rect, j.rect):
		# 			self.poly_explosion()
		# 			j.life -= 1
		# 			self.life = 0
		# 			self.kill()

	def poly_explosion(self):
		pc = random.choice(cfg.poly_coord_array)
		pygame.draw.polygon(self.game.screen, [255, 0, 0], [
			self.location + pc[0],
			self.location + pc[1],
			self.location + pc[2],
			self.location + pc[3],
		])
		pc = random.choice(cfg.poly_coord_array)
		pygame.draw.polygon(self.game.screen, [255, 200, 255], [
			self.location + pc[0],
			self.location + pc[1],
			self.location + pc[2],
			self.location + pc[3],
		])

	def apply_damage(self, hit_object):
		pass

	def draw(self):
		pygame.draw.circle(self.game.screen, [0, 0, 250], self.location, 4)
		pygame.draw.line(self.game.screen, [50, 5, 5], (self.rect.center), self.target.location)

	def update_rect(self):
		self.rect.topleft = self.location

	def loop(self):
		self.kill()
		# self.check_collision()
		self.move()
		self.update_rect()
		self.draw()