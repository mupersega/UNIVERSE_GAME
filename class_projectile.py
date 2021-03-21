import math
import random

import pygame

import cfg


class Projectile:
	"""The Projectile class manages objects that move, gathering velocity, towards a target. If they collide, damage
	will be dealt to the target entity. The drawing of the projectile has hitherto unique dynamism; Only the quarter of
	the circle will be drawn that is closest to the target, which quarter will be ascertained upon instantiation."""
	def __init__(self, parent, lvl, target):
		self.x = parent.x
		self.y = parent.y
		self.parent = parent
		self.target = target
		self.lvl = lvl
		self.game = parent.game
		self.screen = parent.screen
		self.draw_bearing_arg = self.prepare_projectile_bearing()
		self.vel = .02

	def prepare_projectile_bearing(self):
		# Check the target's location to ascertain which quarter of the circle should be drawn.
		# Bearing are represented as integers as follows 0 = NW, 1 = NE, SW = 2, SE = 3
		bearing = 0
		south = False
		east = False
		if self.target.x > self.x:
			east = True
		if self.target.y > self.y:
			south = True
		if south:
			bearing += 2
		if east:
			bearing += 1
		return cfg.bearing_conversions[bearing]

	def move(self):


	def draw(self):
		pygame.draw.circle(self.screen, ([0, 0, 200]), (self.x, self.y), 5, self.draw_bearing_arg)