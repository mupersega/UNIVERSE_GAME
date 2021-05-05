import pygame
import cfg
import random
import time


class Lance:
	"""The lance ammunition type will be a laser that targets, locks on, charges and then hits for high damage. Its rate
	of fire is low"""
	def __init__(self, start_loc, trajectory, target_object, game):
		self.game = game
		self.location = pygame.Vector2(start_loc)
		self.target = target_object
		self.life = 0.01
		self.rect = pygame.Rect(self.location.x, self.location.y, 5, 5)
		self.rgb = [30, 0, 30]
		pygame.draw.circle(self.game.screen, [250, 240, 255], self.location, random.randint(1, 4))

	def charge(self):
		if self.life < 1:
			self.rgb[1] = int(self.life * 255)
			self.life += self.life * .05
		else:
			self.fire()

	def fire(self):
		pygame.draw.line(self.game.screen, [255, 255, 255], self.location, self.target.rect.center, 5)
		self.poly_explosion()
		self.target.life -= 10
		self.kill()

	def kill(self):
		if self in self.game.projectiles:
			self.game.projectiles.remove(self)

	def poly_explosion(self):
		pc = random.choice(cfg.poly_coord_array)
		tl = self.target.location
		pygame.draw.polygon(self.game.screen, [255, 0, 0], [
			tl + pc[0],
			tl + pc[1],
			tl + pc[2],
			tl + pc[3],
		])
		pc = random.choice(cfg.poly_coord_array)
		pygame.draw.polygon(self.game.screen, [255, 200, 255], [
			tl + pc[0],
			tl + pc[1],
			tl + pc[2],
			tl + pc[3],
		])

	def draw(self):
		pygame.draw.line(self.game.screen, self.rgb, self.location, self.target.rect.topleft, 1)

	def update_rect(self):
		self.rect.topleft = self.location

	def loop(self):
		self.charge()
		self.draw()