import pygame

from utility_classes import cfg


class Bar:
	def __init__(self, screen, start_rgb, mid_rgb, end_rgb, target_rect, outline=None):
		self.screen = screen
		self.tr = target_rect
		self.start_rgb = start_rgb
		self.mid_rgb = mid_rgb
		self.end_rgb = end_rgb
		self.outline = outline
		self.progress = 0
		self.surface = pygame.Surface((3, 2))
		pygame.draw.line(self.surface, self.start_rgb, (0, 0), (0, 1))
		pygame.draw.line(self.surface, self.mid_rgb, (1, 0), (1, 1))
		pygame.draw.line(self.surface, self.end_rgb, (2, 0), (2, 1))
		self.surface = pygame.transform.smoothscale(self.surface, (self.tr.width, self.tr.height))

	def draw(self):
		# draw gradient bar
		self.screen.blit(self.surface, self.tr)
		# progress overlay
		pygame.draw.rect(
			self.screen, [0, 0, 0], (self.tr.left, self.tr.top, self.tr.width * self.progress, self.tr.height))
		pygame.draw.rect(
			self.screen, cfg.col.white, (self.tr.left, self.tr.top, self.tr.width * self.progress, self.tr.height), 1)
		if self.outline:
			pygame.draw.rect(self.screen, self.outline, self.tr, 1)

