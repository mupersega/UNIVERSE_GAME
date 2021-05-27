import pygame
import cfg
import time

from class_bar import Bar


class PhaseCountDownDisplay:
	def __init__(self, game):
		self.game = game
		self.screen = game.screen
		self.rect = pygame.Rect(cfg.screen_width - 310, 50, 300, 40)
		self.text_rect = pygame.Rect(cfg.screen_width - 250, 55, 90, 40)
		self.surface = pygame.Surface((200, 50))
		self.progress_bar = Bar(self.screen, [0, 0, 255], [255, 0, 0], self.rect, outline=cfg.col.bone)
		self.font = pygame.font.SysFont("Bauhaus 93", 25)
		self.time_label = self.font.render(
			f"{self.game.phase_display_text} phase, time remaining" + "{}:{:02d}".format(*divmod(0, 60)), True, cfg.col.bone)
		# self.phase_label = self.font.render(f"{self.game.current_phase}", True, cfg.col.bone)

	def update(self):
		secs = self.game.next_phase - time.time()
		self.time_label = self.font.render(
			f"{self.game.phase_display_text} " + "{}:{:02d}".format(*divmod(int(secs), 60)), True, cfg.col.bone)
		if self.game.gather_phase:
			self.progress_bar.progress = 1 - secs / cfg.gather_phase_time
		else:
			self.progress_bar.progress = 1- secs / cfg.combat_phase_time

	def draw(self):
		self.screen.blit(self.time_label, (self.text_rect.topleft))

	def loop(self):
		self.update()
		self.progress_bar.draw()
		self.draw()

