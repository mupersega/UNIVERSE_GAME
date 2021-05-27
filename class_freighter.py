import pygame
import random
import cfg
import math

from class_explosion import Explosion


class Engine:
	"""Implement an engine object to pull a number of carriages containing resources.
	Carriages will follow the same path but begin further behind the engine. Draw lines between
	engine and carriages to show connection. Carriages can get destroyed."""
	def __init__(self, game, path, number_carriages):
		self.game = game
		self.path = path
		self.screen = game.screen
		self.number_carriages = number_carriages
		self.engine_image = cfg.big_ship_green
		self.full_train = [self]
		self.carriage_lines = []

		self.location = self.path.pop(0)
		self.target_location = self.path.pop(0)
		self.direction = pygame.Vector2((self.location - self.target_location)).normalize()
		self.ang_vec = pygame.Vector2(0, 0)
		self.angle = 1

		self.rect = pygame.Rect(self.location.x, self.location.y, 18, 18)

		self.life = cfg.engine_life
		self.active = True

		self.build_carriages()

	def load_next_location(self):
		if self.location.distance_to(self.target_location) < 2:
			if self.path:
				self.target_location = self.path.pop(0)
			else:
				self.kill()

	def take_damage(self, amt):
		self.life -= amt
		if self.life < 1:
			self.kill()

	def kill(self):
		self.game.explosions.append(Explosion(self.game, self.rect.center, 14, [255, 255, 255]))
		self.active = False
		if self in self.game.freighters.copy():
			self.game.freighters.remove(self)
			for i in self.full_train.copy():
				i.kill()

	def build_carriages(self):
		for _ in range(self.number_carriages):
			self.full_train.append(Carriage(self.full_train[-1]))
		for i in self.full_train:
			self.carriage_lines.append(i.rect.center)

	def update(self):
		self.direction = (self.location - self.target_location).normalize()
		self.location -= self.direction * 1
		self.rect.topleft = self.location

	def update_carriages(self):
		for i in self.carriages:
			i.loop()

	def rotate(self):
		rads = math.atan2(self.direction[0], self.direction[1])
		deg = math.degrees(rads)
		self.angle = deg

	def draw(self):
		pygame.draw.lines(
			self.screen, cfg.col.charcoal, closed=False, points=[i.rect.center for i in self.full_train], width=5)

	def loop(self):
		for i in self.full_train:
			i.update()
			i.draw()
		draw_image = pygame.transform.rotate(self.engine_image, self.angle)
		self.game.screen.blit(draw_image, (self.location[0], self.location[1]))
		self.rotate()
		self.load_next_location()


class Carriage:
	def __init__(self, puller) -> object:
		self.game = puller.game
		self.screen = puller.screen
		self.puller = puller
		self.target_location = pygame.Vector2(puller.location)
		self.location = pygame.Vector2(puller.location.x + 50, puller.location.y + 20)
		self.direction = pygame.Vector2(self.location - self.target_location).normalize()
		self.tow_location = pygame.Vector2(self.location + self.direction * 10)

		self.rect = pygame.Rect(self.location.x, self.location.y, 18, 18)
		self.velocity = random.uniform(.5, 3)
		self.life = cfg.carriage_life
		self.active = True

		self.carrying = random.choice(cfg.planet_probability)

	def update(self):
		if self.rect.colliderect(self.puller.rect):
			return
		self.velocity = self.location.distance_to(self.puller.location) / 15
		self.target_location = self.puller.location
		self.direction = pygame.Vector2(self.location - self.target_location).normalize()
		self.tow_location = pygame.Vector2(self.location + self.direction * -10)
		self.location -= (self.location - self.target_location).normalize() * self.velocity
		self.rect.topleft = self.location

	def take_damage(self, amt):
		self.life -= amt
		if self.life < 1:
			self.kill()

	def kill(self):
		if self.active:
			self.active = False
			self.game.explosions.append(
				Explosion(self.game, self.rect.center, 10, cfg.warehouse_colours[self.carrying]["rgb"]))

	def draw(self):
		if self.active:
			pygame.draw.circle(self.screen, cfg.warehouse_colours[self.carrying]["rgb"], self.rect.center, 10)
		pygame.draw.circle(self.screen, [200, 200, 200], self.rect.center, 10, width=3)

	def loop(self):
		self.update()
		self.draw()
