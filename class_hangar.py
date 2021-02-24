import random
import pygame

import cfg
from class_bay import Bay
from class_location import Location
from class_warehouse import Warehouse

pygame.font.init()
HANGAR_FONT = pygame.font.SysFont('Comic Sans MS', 30)


class Hangar:
	"""Hangar to manage a collection of facilities at a station index."""
	def __init__(self, station, index):
		# station containing this hangar
		self.station = station
		# hangar number will determine all position values
		self.index = index
		self.kind = 'hangar'
		self.owner = None
		# x and y values exist for the top left from which to space facilities.
		self.x = station.rect.right + cfg.x_pad
		self.y = station.y + (cfg.facility_h + cfg.y_pad) * self.index + cfg.y_pad
		# warehouses to be inserted and bays appended
		self.facilities = []
		self.approach_location = Location(
			(self.station.dock_location.x, self.y + cfg.facility_h / 2), 1, .9)
		self.approach_velocity = False

		self.myfont = pygame.font.SysFont("Arial", 12)
		self.label = None

		# for i in range(random.randint(1, 1)):
		# for i in range(random.randint(0, 2)):
		# 	self.new_warehouse()

		# for i in range(random.randint(1, 2)):
		for i in range(0):
			self.new_bay()

		self.set_facilities_pos()

	def update_label(self):
		self.label = self.myfont.render(
			str(self.owner.name[0:3]).upper(), 0, (255, 255, 255))

	def set_facilities_pos(self):
		# set pos dependant on index and update rect
		i = 0
		bay_count = 1
		wh_count = 1
		for facility in self.facilities:
			if facility.kind == 'bay':
				facility.index = bay_count
				bay_count += 1
			elif facility.kind == 'warehouse':
				facility.index = wh_count
				wh_count += 1
			facility.x = self.x + (cfg.facility_w + cfg.x_pad) * i
			facility.y = self.y
			cfg.update_rect(facility)
			i += 1

	def new_warehouse(self):
		new_wh = Warehouse(self)
		# insert onto this list to ensure warehouses will be on the left
		self.facilities.insert(0, new_wh)
		self.set_facilities_pos()

	def remove_warehouse(self):
		# find an instance of warehouse and remove it
		for i in self.facilities:
			if isinstance(i, Warehouse):
				self.facilities.remove(i)
				print("warehouse removed")
				break
		self.set_facilities_pos()

	def new_bay(self):
		new_bay = Bay(self)
		# 'append' so that bays will be on the end of list, thus right side
		self.facilities.append(new_bay)
		self.set_facilities_pos()
		print("bay")

	def remove_bay(self):
		# find an instance of bay and remove it
		for i in self.facilities:
			if isinstance(i, Bay):
				self.facilities.remove(i)
				print("bay removed")
				break
		self.set_facilities_pos()

	def draw(self):
		if self.owner:
			self.station.game.screen.blit(self.label, (self.x - 35, self.y))

	def loop(self):
		for i in self.facilities:
			i.loop()
