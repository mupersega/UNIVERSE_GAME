import pygame

import cfg


class Warehouse:
	"""Warehouse object wherein resources will be stored. Can have multiple."""
	def __init__(self, hangar):
		self.screen = hangar.station.game.screen
		self.on_screen = True
		self.hangar = hangar
		self.owner = hangar.owner
		self.kind = 'warehouse'
		self.index = 1

		self.x = 0
		self.y = 0
		self.width = cfg.facility_w
		self.height = cfg.facility_h
		self.location = pygame.math.Vector2()

		self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
		self.rgb = cfg.wh_colour
		self.polarity = 1
		self.arrived_distance = cfg.wh_arrived_distance
		self.interactable_dist = cfg.wh_interactable_distance
		self.approach_velocity = False

		# Auto Commands
		self.auto = False
		self.auto_upgrade = None

		# self.hold = []
		self.hold_lvl = 1
		self.hold_capacity = 200
		self.ores = [0, 200, 0]
		self.bar_w = cfg.facility_w - 2
		self.hangar_space = cfg.facility_h - cfg.y_pad * 2
		self.occupant = None

		self.capacity_glow = [100, 0, 100]

	def draw(self):
		# base background
		pygame.draw.rect(self.screen, self.rgb, self.rect)
		# # draw bars
		next_y = 0
		i = 0
		for j in self.ores:
			if j > 0:
				x = self.x + 2
				h = int(self.hangar_space * (j / (self.hold_capacity)))
				y = self.rect.bottom - next_y - h - 2
				w = self.bar_w
				next_y += h
				# print(h, y)
				rgb = cfg.warehouse_colours[cfg.mineral_list[i]]["rgb"]
				pygame.draw.rect(self.screen, rgb, (x, y, w, h))
			i += 1
			if cfg.hold_at_capacity(self):
				pygame.draw.rect(self.screen, [200, 30, 30], self.rect, 2)
		# 	else:
		# 		pass
		# 		# if self.capacity_glow[1] >= 100:
		# 		# 	self.glow = -1
				# if self.capacity_glow[1] <= 10:
				# 	self.glow = 1
				# self.capacity_glow[1] += self.glow
				# pygame.draw.rect(self.screen, self.capacity_glow, self.rect, 2)

	def update_vector(self):
		self.location = (self.x, self.y)

	def loop(self):
		self.draw()
