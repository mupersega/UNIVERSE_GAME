import pygame
from utility_classes import cfg
import random

from environment_classes.class_explosion import Explosion


class Maul:
	"""The maul ammunition type will move in a direction at a high rate of fire, it has a low range and will not alter
	its trajectory. It will have a life span and thus does not require removal upon leaving the screen."""
	def __init__(self, start_loc, trajectory, target, game, shooter):
		self.game = game
		self.location = pygame.Vector2(start_loc)
		self.speed = 10
		self.velocity = pygame.Vector2(trajectory) * self.speed
		self.shooter = shooter
		self.damage = 1
		self.life = random.randint(40, 60)
		self.rect = pygame.Rect(self.location.x, self.location.y, 15, 15)
		self.rgb = random.choice([
				cfg.col.dark_rubine,
				cfg.col.light_rubine,
				cfg.col.red
			])
		self.dim = 1
		# self.rgb = cfg.col.red
		# pygame.draw.circle(self.game.screen, [250, 240, 255], self.location, random.randint(1, 4))
		self.game.explosions.append(Explosion(self.game, start_loc, 3, [255, 255, 255]))

	def move(self):
		self.location -= self.velocity
		self.update_rect()
		self.life -= 1
		self.velocity *= 0.998

	def kill(self):
		if self.life < 1 and self in self.game.projectiles:
			self.game.projectiles.remove(self)

	def check_collision(self):
		nearby_hits = []
		self.game.hostile_quadtree.query(self.rect, nearby_hits)
		for i in nearby_hits:
			if pygame.Rect.colliderect(self.rect, i.rect):
				i.location -= self.velocity
				self.game.explosions.append(Explosion(self.game, self.location, 5, self.rgb, self.velocity))
				i.life -= self.damage
				i.last_hit = self.shooter
				self.life = 0
				self.kill()

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
		pygame.draw.circle(self.game.screen, self.rgb, self.rect.center, self.dim)
		# pygame.draw.rect(self.game.screen, self.rgb, (self.rect.center, (1, 1)))

	def update_rect(self):
		self.rect.center = self.location

	def loop(self):
		self.kill()
		self.check_collision()
		self.move()
		self.draw()