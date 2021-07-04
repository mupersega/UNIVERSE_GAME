import pygame

from utility_classes import cfg
from static_classes.class_hangar import Hangar
from static_classes.class_location import Location
from static_classes.launch_bay import LaunchBay


class Station:
	"""Station object containing and positioning player bays and hangars."""
	def __init__(self, game, station_number, hangars=cfg.default_hangars):
		# First station needs to init as num 0
		self.game = game
		self.screen = game.screen
		self.on_screen = True
		self.sn = station_number
		self.hangar_count = 8 if self.sn == 0 else abs(8 - self.sn * 2)
		self.kind = 'station'
		self.x = cfg.st_x_offset + self.sn * cfg.station_spacing
		self.y = cfg.st_y_offset
		self.width = cfg.station_width
		self.height = cfg.y_pad + (self.hangar_count * (
				cfg.y_pad + cfg.facility_h))
		self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
		self.rgb = cfg.st_colour
		self.approach_location = Location(
			(self.rect.right + (cfg.facility_w + cfg.x_pad) * (cfg.default_max_facilities + 1.5), self.rect.bottom + cfg.facility_h))
		self.depart_location = Location(
			((self.rect.right + cfg.x_pad) + cfg.facility_w * (cfg.default_max_facilities + 1.3), self.rect.bottom + cfg.facility_h * 2), 1)
		self.approach_velocity = False

		# iterables
		self.launch_bay = LaunchBay(self.game, self)
		self.hangars = []
		self.hold = []

		self.station_setup()

	def station_setup(self):
		# construct i hangars
		for _ in range(self.hangar_count):
			self.new_hangar()

	def new_hangar(self):
		new_hangar = Hangar(self, len(self.hangars))
		self.hangars.append(new_hangar)

	def draw(self):
		pygame.draw.rect(self.screen, self.rgb, self.rect)
		pygame.draw.rect(self.screen, cfg.static_outline, self.rect, 1)

	def loop(self):
		self.launch_bay.draw()
		self.draw()
