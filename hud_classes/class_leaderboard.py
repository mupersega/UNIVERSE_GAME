import pygame
from utility_classes import cfg
import operator


class Leaderboard:
	def __init__(self, game):
		self.game = game
		self.screen = game.screen
		self.rect = pygame.Rect(cfg.screen_width / 5 * 4, 100, cfg.screen_width / 5, 400)
		self.surface = pygame.Surface((self.rect.width, self.rect.height))
		self.column_one = self.rect.width / 5 * 2
		self.column_two = self.rect.width / 5 * 4
		self.header_player = cfg.leaderboard_font.render(str("PLAYER"), True, cfg.col.white)
		self.header_kills = cfg.leaderboard_font.render(str("KILLS"), True, cfg.col.white)
		self.surface.blit(self.header_player, (0, 0))
		self.surface.blit(self.header_kills, (int(self.column_two), 0))

	def order_players(self, attr):
		# Set leader position of player classes by a particular passed class attribute
		for i, j in enumerate(sorted(self.game.players, key=operator.attrgetter(attr), reverse=True)):
			j.leaderboard_position = i + 1
			# print(f"{j.name} is in position {j.leaderboard_position}")

	def return_ordered_players(self, attr, descending: bool):
		# Descending must be a bool, if True: List returned will be objects with highest to lowest of attr.
		return sorted(self.game.players, key=operator.attrgetter(attr), reverse=descending)

	def blit_to_board(self):
		self.surface.fill([0, 0, 0])
		self.surface.blit(self.header_player, (self.column_two - self.header_player.get_width() - 5, 0))
		self.surface.blit(self.header_kills, (int(self.column_two), 0))
		for i in self.game.players:
			i.kills_plate = cfg.leaderboard_font.render(str(i.kills), True, cfg.col.white)
			y_offset = i.leaderboard_position * 25
			self.surface.blit(i.name_plate, (
					self.column_two - i.name_plate.get_width() - 5,
					0 + y_offset))
			self.surface.blit(i.kills_plate, (
				0 + self.column_two + 5,
				0 + y_offset))

	def update(self):
		self.order_players("kills")
		self.blit_to_board()

	def draw(self):
		self.screen.blit(self.surface, self.rect.topleft)
		# pygame.draw.rect(self.screen, [30, 30, 30], self.rect, width=1)

