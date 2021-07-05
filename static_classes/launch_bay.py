import pygame
import random

from utility_classes import cfg
from projectile_classes.starseeker import Starseeker


class LaunchBay:
	"""A static structural class positioned at the bottom of a station from
	which special items and quest builds will spawn/launch."""
	def __init__(self, game, parent):
		self.game = game
		self.parent = parent
		self.rect = pygame.Rect(parent.rect.bottomleft, (parent.width, cfg.facility_h))
		self.image_surface = pygame.Surface(self.rect.size)
		self.launch_glow = pygame.Surface((2, 3))
		self.glow_alpha = 255

		self.make_image_surface()
		self.make_launch_glow_surface()

		self.start_glow_pos = pygame.Vector2(
			self.rect.centerx - self.launch_glow.get_width() * .5,
			self.rect.centery
		)
		self.final_glow_pos = pygame.Vector2(
			self.rect.centerx - self.launch_glow.get_width() * .5,
			self.rect.top - self.launch_glow.get_height()
		)
		self.current_glow_pos = pygame.Vector2(
			self.rect.centerx - self.launch_glow.get_width() * .5,
			self.rect.top - self.launch_glow.get_height()
		)

	def make_image_surface(self):
		img_rect = self.image_surface.get_rect()
		pygame.draw.rect(self.image_surface, cfg.col.p_one, img_rect)
		pygame.draw.rect(self.image_surface, cfg.col.white, img_rect, 1)
		pygame.draw.circle(self.image_surface, [0, 0, 0], img_rect.midbottom, cfg.facility_w_two_third)
		pygame.draw.circle(self.image_surface, cfg.col.white, img_rect.midbottom, cfg.facility_w_two_third, 1)
		self.image_surface.set_colorkey([0, 0, 0])
		
	def make_launch_glow_surface(self):
		pygame.draw.line(self.launch_glow, cfg.col.white, (0, 0), (1, 0))
		pygame.draw.line(self.launch_glow, cfg.col.p_one, (0, 1), (1, 1))
		pygame.draw.line(self.launch_glow, [0, 0, 0], (0, 2), (2, 2))
		self.launch_glow = pygame.transform.smoothscale(
			self.launch_glow, (cfg.facility_w, cfg.facility_h))

	def launch(self, player, item):
		if item.lower() == "starseeker":
			self.launch_starseeker(player)
		if item.lower() == "amp":
			self.launch_amp(player)

	def launch_starseeker(self, player):
		self.game.projectiles.append(Starseeker(
			self.game, player, self.rect.center, pygame.Vector2(
				0, random.uniform(-4, -2)), 0)
		)
		self.current_glow_pos = pygame.Vector2(self.start_glow_pos)

	def launch_amp(self, player):
		pass

	def update_glow_pos(self):
		difference = self.final_glow_pos.y - self.current_glow_pos.y
		if abs(difference) < 1:
			self.current_glow_pos = pygame.Vector2(self.final_glow_pos)
		else:
			self.current_glow_pos.y += difference * .005

	def draw(self):
		self.update_glow_pos()
		self.game.screen.blit(self.launch_glow, self.current_glow_pos)
		self.game.screen.blit(self.image_surface, self.rect.topleft)
