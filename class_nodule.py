import pygame
import random
import cfg

from class_roamer import Roamer
from class_explosion import Explosion


class Nodule:
	"""Implement nodule class to induce hostile entity creation."""
	def __init__(self, game, location, parent):
		self.game = game
		self.location = pygame.Vector2(location)
		self.parent = parent
		self.active = False
		self.rect = pygame.Rect(
			self.location.x - cfg.nodule_w / 2,
			self.location.y - cfg.nodule_h / 2, cfg.nodule_w, cfg.nodule_h)
		self.last_hit = 1


class CircleNodule(Nodule):
	def __init__(self, game, location, parent):
		super().__init__(game, location, parent)

	def spawn(self):
		self.game.hostiles.append(Roamer(self.game, self.parent, self.rect.center))
		# pygame.draw.circle(self.game.screen, cfg.col.bone, self.rect.center, self.rect.w + 2)

	def draw(self):
		pygame.draw.circle(self.game.screen, cfg.col.bone, self.rect.center, self.rect.w)

