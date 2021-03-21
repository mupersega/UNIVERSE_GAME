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
		self.draw_bools = [False, False, False, False]
		self.vel = 0.001
		self.trajectory = None

		self.prepare_projectile_bearing()
		self.prepare_trajectory()

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
		self.draw_bools[bearing] = True


	def prepare_trajectory(self):
		self.trajectory = pygame.math.Vector2((self.target.x - self.x, self.target.y - self.y)).normalize()

	def move(self):
		if cfg.on_screen_check(self):
			self.x += self.trajectory[0] * self.vel
			self.y += self.trajectory[1] * self.vel
			self.vel += self.vel ** .01
		else:
			if self in self.game.projectiles:
				self.game.projectiles.remove(self)

	def draw(self):
		pygame.draw.circle(self.screen, [0, 0, 200], (self.x, self.y), 5, draw_top_left=self.draw_bools[0],
						   draw_top_right=self.draw_bools[1],
						   draw_bottom_left=self.draw_bools[2],
						   draw_bottom_right=self.draw_bools[3]
						   )

	def loop(self):
		self.move()
		self.draw()
