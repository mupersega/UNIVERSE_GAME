import pygame
from utility_classes import cfg
import random

from environment_classes.class_explosion import Explosion


class Bolt:
	"""The bolt ammunition type is the 'missile' class, it is assigned a target on init and will move towards it. It is
	the ammo type that has the most physics applied to it. It will adopt an initial velocity vector derived from the
	turrets barrel direction."""
	def __init__(self, start_loc, trajectory, target, game, shooter):
		self.game = game
		self.target = target
		self.location = pygame.Vector2(start_loc - trajectory * 10)
		self.shooter = shooter
		self.thrust = pygame.Vector2(0, 0)
		self.velocity = pygame.Vector2(0, 0)
		self.acceleration = pygame.Vector2(0, 0)
		self.wobble = pygame.Vector2(0, 0)
		self.rect = pygame.Rect(self.location.x, self.location.y, 10, 10)

		# Trail preparation
		self.num_bolt_trails = 3
		self.bolt_trails = []
		for _ in range(self.num_bolt_trails):
			self.bolt_trails.append([pygame.Vector2(self.location), pygame.Vector2(self.location)])

		self.life = random.randint(60, 80) * 5

		# Muzzle flash
		self.game.explosions.append(Explosion(self.game, start_loc, 4, [255, 255, 255]))

	def apply_force(self, force):
		self.acceleration += force

	def update(self):
		d = self.location.distance_to(self.target.location)
		self.wobble = (random.uniform(-1, 1), random.uniform(-1, 1))
		self.thrust = (self.location - self.target.location).normalize()

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
			self.add_rand_trail_vec(self.bolt_trails[0], 10)
			if self.life % 12 == 0:
				self.add_rand_trail_vec(self.bolt_trails[1], 30)
				if self.life % 18 == 0:
					self.add_rand_trail_vec(self.bolt_trails[2], 50)

	def kill(self):
		if self.target.life <= 0:
			self.life *= .95
		if self.life < 1 and self in self.game.projectiles:
			self.game.projectiles.remove(self)

	def check_collision(self):
		nearby_hits = []
		self.game.hostile_quadtree.query(self.rect, nearby_hits)
		for t in nearby_hits:
			if pygame.Rect.colliderect(self.rect, t.rect):
				self.draw_bolts(t)

	def draw_bolts(self, target):
		# add final vectors to trail so that all bolts meet on location
		for i in range(3):
			self.add_rand_trail_vec(self.bolt_trails[i], 2)

		pygame.draw.lines(self.game.screen, [0, 0, 200], closed=False, points=self.bolt_trails[0])
		pygame.draw.lines(self.game.screen, [180, 0, 200], closed=False, points=self.bolt_trails[1], width=2)
		pygame.draw.lines(self.game.screen, [225, 200, 255], closed=False, points=self.bolt_trails[2], width=3)

		# Hit effects/changes
		# push target
		try:
			target.location -= self.velocity.normalize() * 2
		except ValueError:
			return
		# damage target
		target.life -= 20
		# self decay
		self.life -= 10
		target.last_hit = self.shooter

	def add_rand_trail_vec(self, trail, variance):
		trail.append(
			[self.location.x + random.randrange(-variance, variance), self.location.y + random.randrange(-variance, variance)]
		)

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