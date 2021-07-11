import pygame

from utility_classes import cfg


class FreightRatioDisplay:
	"""A single hud element consisting of three bars each representing the
	percentage of that mineral's request ratio. All three bars combine to
	make up one display bar."""
	def __init__(self, game):
		self.game = game
		self.padding = 6
		self.outer_height = 30
		self.outer_width = int(cfg.screen_width * .1)
		self.inner_height = self.outer_height - self.padding
		self.inner_width = self.outer_width - self.padding * 2
		self.rect = pygame.Rect(cfg.screen_width - self.outer_width - 5 - 1, 92, self.outer_width, self.outer_height)
		self.surface = pygame.Surface((self.outer_width, self.outer_height))
		self.bars = [1, 1, 1]
		self.label = cfg.leaderboard_font_bold.render("NEXT HAUL>>", True, cfg.col.p_one)
		self.label_pos = (
			self.rect.left - self.label.get_width() - 2,
			self.rect.bottom - self.label.get_height())

		self.update_bars()
		self.draw_bars_to_surface()

	def update_bars(self):
		fp = self.game.freight_request_priority
		total_req = sum(fp)
		self.bars = [int(i / total_req * self.inner_width) for i in fp]
		# print(self.bars)
		self.draw_bars_to_surface()

	def draw_bars_to_surface(self):
		self.surface.fill(cfg.col.p_five)
		pygame.draw.rect(self.surface, cfg.col.white, ((0, 0), (self.outer_width, self.outer_height)), 1)
		for h, i in enumerate(self.bars):
			pygame.draw.rect(self.surface, cfg.mineral_info[cfg.mineral_name_list[h]]["market_bg_rgb"], (
				(sum(self.bars[0:h]) + self.padding, self.padding), (self.bars[h], self.inner_height - self.padding))
					)
			pygame.draw.rect(self.surface, cfg.mineral_info[cfg.mineral_name_list[h]]["market_rgb"], (
				(sum(self.bars[0:h]) + self.padding, self.padding), (self.bars[h], self.inner_height - self.padding)),
					width=2)

	def draw(self):
		self.game.screen.blit(self.label, self.label_pos)
		self.game.screen.blit(self.surface, self.rect.topleft)

