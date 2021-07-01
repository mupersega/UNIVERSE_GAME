import pygame
from utility_classes import cfg
import operator


# noinspection DuplicatedCode
class Leaderboard:
	def __init__(self, game):
		self.game = game
		self.screen = game.screen

		self.row_height = 25
		self.overall_width = cfg.screen_width * .2
		self.subdivisions = 12
		self.subdivision_width = self.overall_width / self.subdivisions
		self.col_sub_widths = [8, 4]  # Sum of element will ideally equal self.subdivisions.
		self.col_px_widths = [i * self.subdivision_width for i in self.col_sub_widths]
		self.col_x = [sum(self.col_px_widths[0:i]) for i in range(len(self.col_sub_widths))]

		self.top_left = pygame.Vector2(cfg.screen_width - self.overall_width - 5, 88)
		self.surface = pygame.Surface((self.overall_width, (len(self.game.players) + 1) * self.row_height))

		self.headers = [
			cfg.leaderboard_font.render(str("PLAYER"), True, cfg.col.white),
			cfg.leaderboard_font.render(str("KILLS"), True, cfg.col.white)
		]

	def order_players(self, attr):
		# Set leader position of player classes by a particular passed class attribute
		for i, j in enumerate(sorted(self.game.players, key=operator.attrgetter(attr), reverse=True)):
			j.leaderboard_position = i + 1
		# print(f"{j.name} is in position {j.leaderboard_position}")

	def return_ordered_players(self, attr, descending: bool):
		# Descending must be a bool, if True: List returned will be objects with highest to lowest of attr.
		return sorted(self.game.players, key=operator.attrgetter(attr), reverse=descending)

	def blit_headers(self):
		# Alignment and padding information.
		x_aligns = ["right", "centre"]
		y_aligns = ["middle", "middle"]
		pads = [5, 5]
		for h, i in enumerate(self.headers):
			y = 0
			x = self.col_x[h]
			col_bg_rgb = [cfg.col.p_three, cfg.col.p_four]
			# Draw background rects to surface.
			pygame.draw.rect(self.surface, col_bg_rgb[h], (x, y, self.col_px_widths[h], self.row_height))
			pygame.draw.rect(self.surface, cfg.col.p_two, (x, y, self.col_px_widths[h], self.row_height), 2)
			# Blit text to surface.
			self.surface.blit(i, (
				x + cfg.return_x_align_offset(x_aligns[h], x, self.col_px_widths[h], i.get_width(), pads[h]), (
						y + cfg.return_y_align_offset(y_aligns[h], y, self.row_height, i.get_height(), pads[h])))
							)

	def blit_player_rows(self):
		# For every player, blit their row to leaderboard.
		for p in self.game.players:
			# Render/prepare cells.
			cells = [
				p.name_plate,
				cfg.leaderboard_font.render(str(p.kills), True, cfg.col.white),
			]
			# Alignment and padding information.
			x_aligns = ["right", "centre"]
			y_aligns = ["middle", "middle"]
			pads = [5, 5]
			col_bg_rgb = [cfg.col.p_five, cfg.col.p_six]
			# Blit every cell to row.
			for h, i in enumerate(cells):
				y = p.leaderboard_position * self.row_height
				x = self.col_x[h]
				# Draw background rects to surface.
				pygame.draw.rect(self.surface, col_bg_rgb[h], (x, y, self.col_px_widths[h], self.row_height))
				pygame.draw.rect(self.surface, cfg.static_outline, (x, y, self.col_px_widths[h], self.row_height), 1)
				# Blit text to surface.
				self.surface.blit(i, (
					x + cfg.return_x_align_offset(x_aligns[h], x, self.col_px_widths[h], i.get_width(), pads[h]), (
							y + cfg.return_y_align_offset(y_aligns[h], y, self.row_height, i.get_height(), pads[h])))
								)

	def blit_to_board(self):
		# Resize surface.
		self.surface = pygame.Surface((self.overall_width, (len(self.game.players) + 1) * self.row_height))
		# Clear surface.
		self.surface.fill([0, 0, 0])
		# Blit things.
		self.blit_player_rows()
		self.blit_headers()

		self.game.market.update_top_left()

	def update(self):
		self.order_players("kills")
		self.blit_to_board()

	def draw(self):
		self.screen.blit(self.surface, self.top_left)
