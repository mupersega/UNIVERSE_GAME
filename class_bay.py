import pygame

import cfg
from class_entity import Entity
from class_warehouse import Warehouse


class Bay:
	"""Bay object wherein players will store vehicles and land current ship."""
	def __init__(self, hangar):
		self.screen = hangar.station.game.screen
		self.hangar = hangar
		self.owner = hangar.owner
		self.kind = 'bay'
		self.index = 1
		self.on_screen = True

		self.x = 0
		self.y = 0
		self.width = cfg.facility_w
		self.height = cfg.facility_h
		self.approach_velocity = 1
		self.approach_angle = .9

		self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
		self.rgb = cfg.bay_colour
		self.arrived_distance = cfg.bay_arrived_distance
		self.interactable_distance = cfg.bay_interactable_distance
		self.approach_velocity = 1

		# class specific
		self.occupant = None

	def new_ship(self):
		if self.occupant is None:
			ship = Entity(self)
			self.occupant = ship

	def unload(self, actor):
		for facility in self.hangar.facilities:
			if isinstance(facility, Warehouse):
				for i in actor.hold.copy():
					if not cfg.hold_at_capacity(facility):
						facility.hold.append(actor.hold.pop())
						print(actor.hold)
						facility.stock_count()
					else:
						break
				print(len(facility.hold))
				print(facility.ores)

	def draw(self):
		pygame.draw.rect(self.screen, self.rgb, self.rect, 2)

	def loop(self):
		self.draw()
