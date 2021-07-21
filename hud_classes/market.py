import random
import pygame
import math

from utility_classes import cfg


class Market:
	"""Implement the market class which holds trade objects such that
	players can exchange resources. Also a gui element used for dis-
	playing current available trades represented by trade objects."""

	# # !trade 30 rubine for 5 ceruliun # #

	def __init__(self, game):
		self.game = game

		self.trades = []
		self.total_trades = 0

		self.width = int(cfg.screen_width * .08)
		self.row_height = 25
		self.surface = pygame.Surface((self.width, len(self.trades) * self.row_height))
		self.top_left = pygame.Vector2(
			cfg.screen_width - self.width - 6,
			135 + self.game.leaderboard.row_height * (len(self.game.players) + 1))

	def new_trade(self, trader, offer, ask):
		# Prepare a new code/ID to the trade.
		Trade(self, trader, offer, ask)

	def finalize_trade(self, trader, trade_id):
		for i in self.trades:
			if i.code == trade_id:
				i.payout_trade(trader)

	def clear_player_trade(self, player_name):
		for i in self.trades:
			if i.lister.name == player_name:
				self.clear_trade(i)

	def clear_trade(self, trade):
		trade.lister.distribute_resources([int(i * cfg.cancelled_trade_return) for i in trade.offer_list])
		self.trades.remove(trade)
		self.update_surface()

	def update_surface(self):
		self.surface = pygame.Surface((self.width, len(self.trades) * self.row_height))
		for h, i in enumerate(self.trades):
			self.surface.blit(i.surface, (0, h * self.row_height))

	def update_top_left(self):
		self.top_left = pygame.Vector2(
			cfg.screen_width - self.width - 5,
			135 + self.game.leaderboard.row_height * (len(self.game.players) + 1))

	def draw(self):
		# pygame.draw.rect(self.game.screen, [255, 255, 255], self.surface.get_rect(), width=5)
		self.game.screen.blit(self.surface, self.top_left)


class Trade:
	"""Implement a single trade object detailing the player that
	listed the trade and also its particulars."""

	# # !trade 30 rubine for 5 ceruliun  # list eg. [rubine, 20] # #
	def __init__(self, market, lister, offer: list, ask: list):
		self.market = market
		self.lister = lister
		self.code = str(lister.name)[0:2].lower() + "-" + str(market.total_trades)
		# print(self.code)

		self.offer_list = cfg.return_mineral_list(offer[0], offer[1])
		self.ask_list = cfg.return_mineral_list(ask[0], ask[1])

		self.offer_rgb = cfg.mineral_info[offer[0]]["market_rgb"]
		self.offer_bg_rgb = cfg.mineral_info[offer[0]]["market_bg_rgb"]
		self.ask_rgb = cfg.mineral_info[ask[0]]["market_rgb"]
		self.ask_bg_rgb = cfg.mineral_info[ask[0]]["market_bg_rgb"]

		self.labels = None
		self.surface = None

		self.process_incoming_trade()

	@staticmethod
	def check_resources_available(trader, resource_list):
		return cfg.resource_check(resource_list, cfg.tally_resources(trader))

	def append_trade(self):
		# Clear trade if player already has a trade listed.
		for i in self.market.trades.copy():
			if i.lister is self.lister:
				# Check to see if list is a duplicate, if so don't clear and distribute resources.
				if self.offer_list == i.offer_list and self.ask_list == i.ask_list:
					return
				else:
					self.market.clear_trade(i)
		self.market.trades.append(self)
		cfg.withdraw_resources(self.lister, self.offer_list)
		self.market.total_trades += 1

	def process_incoming_trade(self):
		"""Process new trades, and append if resources are available."""
		if self.check_resources_available(self.lister, self.offer_list):
			self.build_labels()
			self.build_surface()
			self.append_trade()
			self.market.update_surface()
		else:
			print(f"{self.lister.name.upper()} - Resources not available.")

	def payout_trade(self, trader):
		"""Payout offer list to trader if they have the ask_list resources. Withdraw resources from
		trader and clear trade."""
		if self.check_resources_available(trader, self.ask_list):
			trader.distribute_resources(self.offer_list)
			cfg.withdraw_resources(trader, self.ask_list)
			self.market.clear_trade(self)
			self.market.update_surface()

	def build_labels(self):
		self.labels = [
			cfg.market_name.render(str(self.code).upper(), True, cfg.col.p_two),
			cfg.market_numbers.render(str(max(self.offer_list)), True, self.offer_rgb),
			cfg.market_numbers.render(str(max(self.ask_list)), True, self.ask_rgb)
		]

	def build_surface(self):
		# Prep vars.
		total_width, total_height = self.market.width, self.market.row_height
		number_columns = 3
		col_w = int(total_width / number_columns)
		# Prep surface.
		self.surface = pygame.Surface((total_width, total_height))
		self.surface.fill([30, 30, 30])
		# Draw background rects, offer and ask.
		pygame.draw.rect(
			self.surface, self.offer_bg_rgb, (1 * col_w, 0, col_w, total_height))
		pygame.draw.rect(
			self.surface, self.ask_bg_rgb, (2 * col_w, 0, col_w, total_height))
		# Draw rect outlines.
		for i in range(3):
			pygame.draw.rect(
				self.surface, cfg.col.p_three, (i * col_w, 0, col_w, total_height), 1)
		# Blit fonts to surface.
		for h, i in enumerate(self.labels):
			top_left_with_offset = (h * col_w + (col_w - i.get_width()) / 2, 0 + (total_height - i.get_height()) / 2)
			self.surface.blit(i, top_left_with_offset)
