import pygame
import math

import cfg
from class_entity import Entity
from class_location import Location
# from class_warehouse import Warehouse


class Bay:
	"""Bay object wherein players will store vehicles and land current ship."""
	def __init__(self, hangar):
		self.screen = hangar.station.game.screen
		self.hangar = hangar
		self.owner = hangar.owner
		self.kind = 'bay'
		self.index = 1
		self.on_screen = True

		self.x = 1
		self.y = 1
		self.location = pygame.math.Vector2(self.x, self.y)
		self.width = cfg.facility_w
		self.height = cfg.facility_h
		self.diameter = 10
		self.approach_velocity = 1
		self.approach_angle = .9

		# Auto commands
		self.auto = False
		self.auto_upgrade = None

		# Bars on bays correspond to [w = miner, n = weapons, e = thrusters, s = hold]
		self.bar_lengths = [0, 0, 0, 0]
		self.bar_offsets = [0, 0, 0, 0]
		self.bar_coords = [[[0,0],[0,0]], [[0,0],[0,0]], [[0,0],[0,0]], [[0,0],[0,0]]]

		self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
		self.rgb = cfg.bay_colour
		self.arrived_distance = cfg.bay_arrived_distance
		self.interactable_distance = cfg.bay_interactable_distance
		self.approach_velocity = 1

		self.approach_location = Location((self.rect.right, self.rect.top + 2), 1, False)
		self.depart_location = Location((self.rect.right, self.rect.bottom - 2), 1, False)

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
		for i, t in enumerate(actor.ores.copy()):
			qty = t
			for _ in range(qty):
				for h in actor.owner.hangars:
					for f in h.facilities:
						if f.kind == 'warehouse' and sum(f.ores) < f.hold_capacity:
							actor.ores[i] -= 1
							f.ores[i] += 1
							break
		self.owner.pause_autos = False

	def update_vector(self):
		self.location = (self.x + self.width * 0.5, self.y + self.width * 0.5)

	def update_locations(self):
		self.approach_location = Location((self.rect.right, self.rect.top + 4), 1, False)
		self.depart_location = Location((self.rect.right, self.rect.bottom - 4), 1, False)

	def update_bar_lengths(self):
		h = self.height - 2
		occ = self.occupant

		# WEST BAR
		w_bl = cfg.find_bar_length(occ.miner_lvl, occ.max_miner_lvl, h)
		w_offset = (h - w_bl) / 2
		west_coords = [[self.rect.left + 1, self.rect.top + w_offset + 1],
						[self.rect.left + 1, self.rect.bottom - w_offset - 1]]

		# NORTH BAR
		n_bl = cfg.find_bar_length(occ.weapons_lvl, occ.max_weapons_lvl, h)
		n_offset = (h - n_bl) / 2
		north_coords = [[self.rect.left + n_offset + 1, self.rect.top + 1],
						[self.rect.right - n_offset - 1, self.rect.top + 1]]

		# EAST BAR
		e_bl = cfg.find_bar_length(occ.thrusters_lvl, occ.max_thrusters_lvl, h)
		e_offset = (h - e_bl) / 2
		east_coords = [[self.rect.right - 1, self.rect.top + e_offset + 1],
						[self.rect.right - 1, self.rect.bottom - e_offset - 1]]

		# SOUTH BAR
		s_bl = cfg.find_bar_length(occ.hold_lvl, occ.max_hold_lvl, h)
		s_offset = (h - s_bl) / 2
		south_coords = [[self.rect.left + s_offset + 1, self.rect.bottom - 1],
						[self.rect.right - s_offset - 1, self.rect.bottom - 1]]

		self.bar_coords = [west_coords, north_coords, east_coords, south_coords]

	def draw(self):
		# Draw bay outline
		pygame.draw.circle(self.screen, cfg.st_colour, self.rect.center, cfg.facility_h / 3, width=2)
		# Draw Attribute bars
		for i in range(4):
			pygame.draw.line(self.screen, cfg.bay_bar_colours[i], self.bar_coords[i][0], self.bar_coords[i][1], width=2)

	def loop(self):
		self.draw()
