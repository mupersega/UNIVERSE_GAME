import pygame
import cfg
import random


class Explosion:
	"""A class to manage explosion objects consisting of n particles. Particles are managed in arrays in this class, NOT
	as their own instantiated objects."""
	def __init__(self, game, position, size):
		self.game = game
		self.location = position
		self.size = size
		self.particles = []
		self.vecs = []
		self.cycle = 0

		self.create_particles()

	def create_particles(self):
		# set particle sizes
		for i in range(self.size):
			self.particles.append(random.randint(1, self.size))
		# set their magnitudes
		for i in range(self.size):
			self.vecs.append(pygame.Vector2(
				random.uniform(-1, 1)*(self.size-self.particles[i]),
				random.uniform(-1, 1)*(self.size-self.particles[i])
			))

	def draw(self):
		for i in range(self.size):
			pygame.draw.circle(self.game.screen, [255, 255, 255], self.location + (self.vecs[i] * self.cycle), self.particles[1])

	def loop(self):
		if self.cycle > self.size * 5:
			if self in self.game.explosions.copy():
				self.game.explosions.remove(self)
		self.cycle += 1
		if self.cycle % 4 == 0:
			for i in range(self.size):
				self.particles[i] -= 1
		self.draw()

