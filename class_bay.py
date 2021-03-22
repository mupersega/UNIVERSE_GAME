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

		# each bay always comes with a ship at init
		self.owner.bays.append(self)
		self.new_ship()

	def new_ship(self):
		if self.occupant is None:
			ship = Entity(self)
			self.occupant = ship

	def unload(self, actor):
		i = 0
		for t in actor.ores.copy():
			qty = t
			for j in range(qty):
				for h in actor.owner.hangars:
					for f in h.facilities:
						if f.kind == 'warehouse':
							if sum(f.ores) < f.hold_capacity:
								actor.ores[i] -= 1
								f.ores[i] += 1
								break
			i += 1

	def draw(self):
		# Draw bay outline
		pygame.draw.rect(self.screen, self.rgb, self.rect, 2)
		# Draw Attribute bars
		# Miner
		pygame.draw.line(self.screen, cfg.miner_bar_colour, (self.x, self.y), (self.x, self.y + (
				self.occupant.miner_lvl / 10 * self.width)), width=4)


	def loop(self):
		self.draw()
