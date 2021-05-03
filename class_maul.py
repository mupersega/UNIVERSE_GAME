import pygame
import random


class Maul:
	"""The maul ammunition type will move in a direction at a high rate of fire, it has a low range and will not alter
	its trajectory. It will have a life span and thus does not require removal upon leaving the screen."""
	def __init__(self, start_loc, trajectory, game):
		self.game = game
		self.location = pygame.Vector2(start_loc)
		self.trajectory = trajectory
		self.acceleration = pygame.Vector2(0, 0)
		self.velocity = 5
		self.life = 300
		self.rect = pygame.Rect(self.location.x, self.location.y, 5, 5)

	def move(self):
		self.location -= self.trajectory * self.velocity
		self.update_rect()
		self.life -= 1
		self.velocity -= self.velocity * .0005

	def kill(self):
		if self.life < 1:
			self.game.projectiles.remove(self)

	def check_collision(self):
		pass

	def apply_damage(self, hit_object):
		pass

	def draw(self):
		pygame.draw.ellipse(self.game.screen, [0, 255, 0], self.rect)

	def update_rect(self):
		self.rect.topleft = self.location

	def loop(self):
		self.kill()
		self.check_collision()
		self.move()
		self.draw()