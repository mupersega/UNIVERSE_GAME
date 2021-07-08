import pygame
import random
from utility_classes import cfg

from entity_classes.hostile import Drone, HunterDrone, Soldier


class Nodule:
	"""Implement nodule class to induce hostile entity creation."""
	def __init__(self, game, location, parent, max_lvl):
		self.game = game
		self.location = pygame.Vector2(location)
		self.base_vec = pygame.Vector2(self.location - parent.rect.center).normalize()
		self.parent = parent

		self.active = False
		self.rect = pygame.Rect(
			self.location.x - cfg.nodule_w / 2,
			self.location.y - cfg.nodule_h / 2, cfg.nodule_w, cfg.nodule_h)

		self.max_lvl = max_lvl
		self.level = random.choice([2])
		self.upgradeable = self.check_max_lvl()
		self.hold = 0
		self.last_hit = 1
		self.glow = 0
		self.life = cfg.nodule_life * self.level

		self.draw_shapes = []
		self.poly_points = []

		self.label = cfg.leaderboard_font.render(f"{self.max_lvl}", True, [255, 255, 255])
		self.setup()

	def setup(self):
		self.poly_points = self.prepare_poly(self.level) if self.level > 2 else None

	def reposition_location(self, location):
		self.location = pygame.Vector2(location)
		self.base_vec = pygame.Vector2(self.location - self.parent.rect.center).normalize()
		self.rect = pygame.Rect(
			self.location.x - cfg.nodule_w / 2,
			self.location.y - cfg.nodule_h / 2, cfg.nodule_w, cfg.nodule_h)
		self.setup()

	def accept_resources(self, amt):
		self.hold += amt
		self.check_level_up()

	def take_damage(self, amt):
		self.life -= amt
		if self.life <= 0:
			self.kill()
			self.parent.take_damage(amt)

	def kill(self):
		if self in self.parent.nodules.copy():
			self.parent.nodules.remove(self)

	def check_level_up(self):
		if self.hold >= self.level * cfg.level_up_cost:
			self.level_up()

	def check_max_lvl(self):
		return self.level < self.max_lvl

	def level_up(self):
		if self.upgradeable:
			self.level += 1
			self.hold = 0
			self.setup()
			self.upgradeable = self.check_max_lvl()
			self.life = cfg.nodule_life * self.level
		else:
			self.parent.accept_resources(self.hold)
			self.hold = 0

	def prepare_poly(self, sides):
		half_diagonal = (1.41 * cfg.nodule_w) / 2
		angle_step = 360 / sides
		self.base_vec = self.base_vec.rotate(20 * sides)
		return [self.location + pygame.Vector2(self.base_vec.rotate(i * angle_step) * half_diagonal) for i in range(sides)]

	def spawn(self):
		self.glow = 25
		if self.level == 2:
			self.game.hostiles.append(Drone(self.game, self.parent, self.rect.center))
		elif self.level == 3:
			self.game.hostiles.append(HunterDrone(self.game, self.parent, self.rect.center))
		elif self.level == 4:
			self.game.hostiles.append(Soldier(self.game, self.parent, self.rect.center))

	def draw(self):
		# self.game.screen.blit(self.label, (self.rect.center))
		if self.level < 3:
			if self.glow > 0:
				pygame.draw.circle(self.game.screen, cfg.col.p_two, self.rect.center, self.rect.w / 2)
				self.glow -= 1
				return
			pygame.draw.circle(self.game.screen, cfg.col.p_three, self.rect.center, self.rect.w / 2)
			# pygame.draw.circle(self.game.screen, cfg.col.bone, self.rect.center, self.rect.w / 2, width=2)
		else:
			if self.glow > 0:
				pygame.draw.polygon(self.game.screen, cfg.col.p_two, self.poly_points)
				self.glow -= 1
				return
			pygame.draw.polygon(self.game.screen, cfg.col.p_three, self.poly_points)
			# pygame.draw.polygon(self.game.screen, cfg.col.bone, self.poly_points, width=2)

