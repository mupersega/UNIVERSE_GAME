import pygame
import cfg
import operator


class Leaderboard:
	def __init__(self, game):
		self.game = game
		self.screen = game.screen
		self.rect = pygame.Rect(20, 400, 300, 600)
		self.surface = pygame.Surface((self.rect.width, self.rect.height))

	def order_players(self, attr):
		# Set leader position of player classes by a particular passed class attribute
		for i, j in enumerate(sorted(self.game.players, key=operator.attrgetter(attr), reverse=True)):
			j.leaderboard_position = i
			print(f"{j.name} is in position {j.leaderboard_position}")

	def blit_to_board(self):
		self.surface.fill([0, 0, 0])
		for i in self.game.players:
			i.kills_plate = cfg.leaderboard_font.render(str(i.kills), True, cfg.col.bone)
			y_offset = i.leaderboard_position * 25
			self.surface.blit(i.name_plate, (
					self.rect.left,
					self.rect.top + y_offset))
			self.surface.blit(i.kills_plate, (
				self.rect.left + 150,
				self.rect.top + y_offset))

	def update(self):
		self.order_players("kills")
		self.blit_to_board()

	def draw(self):
		self.screen.blit(self.surface, (10, 10))
		pygame.draw.rect(self.screen, [30, 30, 30], self.rect, width=1)

