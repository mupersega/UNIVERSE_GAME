import pygame

from static_classes.class_bay import Bay
from static_classes.class_location import Location
from static_classes.class_warehouse import Warehouse
from static_classes.class_turret import Turret
from utility_classes import colours as col, cfg

HANGAR_FONT = pygame.font.SysFont('Comic Sans MS', 30)


class Hangar:
	"""Hangar to manage a collection of facilities at a station index."""
	def __init__(self, station, index):
		# station containing this hangar
		self.station = station
		self.game = self.station.game
		# hangar number will determine all position values
		self.index = index
		self.kind = 'hangar'
		self.owner = None
		# x and y values exist for the top left from which to space facilities.
		self.x = station.rect.right
		self.y = station.y + (cfg.facility_h + cfg.y_pad) * self.index
		self.rect = pygame.Rect(self.x, self.y, cfg.facility_w + cfg.x_pad * 2, cfg.y_pad * 2 + cfg.facility_h)
		self.distance_to_sun = pygame.Vector2(self.x, self.y).distance_to(self.station.game.suns[0].rect.center)
		# warehouses to be inserted and bays appended
		self.facilities = []
		self.turrets = []
		self.approach_location = Location(
			(self.station.approach_location.x, self.rect.top), 1, False)
		self.depart_location = Location(
			(self.station.depart_location.x, self.rect.bottom), 1, False)
		self.approach_velocity = False

		self.myfont = pygame.font.SysFont("Agency FB", cfg.facility_h, bold=True)
		self.label = None

		# for i in range(random.randint(1, 2)):
		for _ in range(0):
			self.new_bay()

		self.set_facilities_pos()
		self.update_label()

	def update_label(self):
		if self.owner:
			self.label = self.myfont.render(
				str(self.owner.name[0:3]).upper(), True, col.p_one)
		else:
			self.label = self.myfont.render(
				(str(self.station.sn) + "." + str(self.index)), True, col.p_four)

	def set_facilities_pos(self):
		bay_count = 1
		wh_count = 1
		turr_count = 1
		for i, facility in enumerate(self.facilities):
			if facility.kind == 'bay':
				facility.index = bay_count
				bay_count += 1
			elif facility.kind == 'turret':
				facility.index = turr_count
				turr_count += 1
			elif facility.kind == 'warehouse':
				facility.index = wh_count
				wh_count += 1
			facility.x = self.station.rect.right + cfg.x_pad + (cfg.facility_w + cfg.x_pad) * i
			facility.y = self.rect.top + cfg.y_pad
			facility.update_vector()
			cfg.update_rect(facility)
			facility.update_locations()
			for facility in self.facilities:
				if facility.kind == "bay":
					facility.update_bar_lengths()

	def new_warehouse(self):
		new_wh = Warehouse(self)
		# insert onto this list to ensure warehouses will be on the left
		self.facilities.insert(0, new_wh)
		self.set_facilities_pos()
		print(f"{self.owner.name} built a warehouse.")

	def new_bay(self):
		new_bay = Bay(self)
		# 'append' so that bays will be on the end of list, thus right side
		self.facilities.append(new_bay)
		self.set_facilities_pos()
		new_bay.update_bar_lengths()
		print(f"{self.owner.name} built a bay.")

	def new_turret(self):
		new_turret = Turret(self)
		# 'append' so that turrets will be on the end of list, thus right side
		self.facilities.append(new_turret)
		self.set_facilities_pos()
		self.turrets.append(new_turret)
		print(f"{self.owner.name} built a turret.")

	def draw(self):
		screen = self.station.game.screen
		x_offset = (self.station.rect.width - self.label.get_width()) / 2
		if self.owner and self.facilities:
			pygame.draw.rect(self.game.screen,[50, 0, 0], self.rect)
			screen.blit(self.label, (self.station.rect.left + x_offset, self.rect.top))
			pygame.draw.line(screen, cfg.st_arm_colour, [self.station.rect.right, self.rect.center[1] - 1],
							 [self.facilities[-1].rect.center[0], self.rect.center[1] - 1], width=4)
		else:
			self.game.screen.blit(cfg.hangar_image, (self.station.rect.left, self.y))
			screen.blit(self.label, (self.station.rect.left + x_offset, self.rect.top))

	def draw_turrets(self):
		for i in self.turrets:
			i.draw_turret()

	def loop(self):
		for i in self.facilities:
			i.loop()

