import pygame
from utility_classes import cfg
import time

from hud_classes.class_bar import Bar


class PhaseCountDownDisplay:
	def __init__(self, game):
		self.game = game
		self.screen = game.screen
		self.rect = pygame.Rect(cfg.screen_width - 305, 50, 300, 40)
		self.text_rect = pygame.Rect(cfg.screen_width - 245, 55, 90, 40)
		self.surface = pygame.Surface((200, 50))
		self.progress_bar = Bar(self.screen, cfg.col.p_one, cfg.col.p_three, cfg.col.p_five, self.rect, outline=cfg.col.white)
		self.font = cfg.bauhaus
		self.time_label = self.font.render(
			f"{self.game.phase_display_text} phase, time remaining" + "{}:{:02d}".format(*divmod(0, 60)), True, cfg.col.white)
		# self.phase_label = self.font.render(f"{self.game.current_phase}", True, cfg.col.bone)

	def update(self):
		secs = self.game.next_phase - time.time()
		self.time_label = self.font.render(
			f"{self.game.phase_display_text} " + "{}:{:02d}".format(*divmod(int(secs), 60)), True, cfg.col.white)
		if self.game.gather_phase:
			self.progress_bar.progress = 1 - secs / cfg.gather_phase_time
		else:
			self.progress_bar.progress = 1 - secs / cfg.combat_phase_time

	def draw(self):
		self.screen.blit(self.game.round_label, (self.rect.left - self.game.round_label_rect.width - 10, self.text_rect.top))
		self.screen.blit(self.time_label, (self.text_rect.topleft))

	def loop(self):
		self.update()
		self.progress_bar.draw()
		self.draw()

