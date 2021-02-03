import math
import random

import numpy as np
import pygame

ship_image = pygame.image.load('mining_ship_1.png')


# CLASS SETTINGS #
# --Game-- #
screen_width = 800
screen_height = 500
fps = 120
universe_primary = "rubine"
universe_secondary = "verdite"
start_stations = 1
start_suns = 1
start_entities = 1

# --Entity-- #
ent_rgb = [250, 200, 100]
ent_interactable_distance = 20
ent_arrived_distance = 2
ent_size = 5
ent_start_capacity = 10
dropoff_speed = 980  # larger number will make drop off slower out of 1000

# --Station-- #
min_hangars_per = 5
max_hangars_per = 20
facility_w = 20
facility_h = 20
max_facilities = 5
# st_colour = [45, 89, 134] # pastel dark blue
st_colour = [102, 102, 153]

st_arrived_distance = 5
st_interactable_distance = 10
station_width = facility_w * 2
default_hangars = 30
lane_width = 9
x_pad = 3
y_pad = 2
st_x_offset = 10 #390 for stream
st_y_offset = 55
station_spacing = station_width + (
	x_pad + facility_w * max_facilities) + lane_width

# --Sun-- #
sun_colour = [245, 245, 245]
sun_interactable_distance = 20
sun_arrived_distance = 10
sun_start_size = 1
sun_max_size = 100
max_planets_per_sun = 9
sun_exclusion_range = 140

# --Planet-- #
planet_probability = [
	"rubine", "rubine", "rubine", "rubine", "rubine",
	"verdite", "verdite", "verdite",
	"ceruliun"
]
pl_interactable_distance = 20
pl_arrived_distance = 15
max_planet_size = 30
min_planet_size = 10
belt_exclusion_range = 10
belt_width_min = 10
belt_width_max = 40

# --Crash-- #
cr_colour = [255, 255, 255]
min_asteroids = 3
max_asteroids = 9
min_crash_size = 1
max_crash_size = 15

# --Asteroid-- #
ast_interactable_distance = 40
ast_arrived_distance = 20

# --Player-- #
player_starting_mupees = 100

# --Hangar-- #
hangar_offset = x_pad
max_facilities = 5
fac_border_width = 2

# --Warehouse-- #
wh_colour = [38, 38, 38]
wh_interactable_distance = 2
wh_arrived_distance = 1
warehouse_colours = {
	"rubine": {"rgb": [255, 51, 51]},
	"verdite": {"rgb": [113, 244, 113]},
	"ceruliun": {"rgb": [102, 102, 255]}
}

# --Bay-- #
bay_colour = [180, 10, 180]
bay_interactable_distance = 3
bay_arrived_distance = 1

# --Location-- #
loc_colour = [255, 0, 255]
loc_interactable_distance = 2
loc_arrived_distance = 2

# --Miscellaneous-- #
composition_rolls = 5
tradables = ["rubine", "verdite", "ceruliun", "mupees"]
mineral_list = ["rubine", "verdite", "ceruliun"]
mineral_info = {
	"rubine": {"rgb": [255, 0, 0]},
	"verdite": {"rgb": [0, 255, 0]},
	"ceruliun": {"rgb": [0, 0, 255]}
}

# the values in these lists correspond to [mupees, rubine, verdite, ceruliun]
upgrade_values = {
	"bay": {
		"miner": [2, 0, 0, 15],
		"hold": [0, 60, 0, 0],
		"thrusters": [0, 60, 0, 0],
	},
	"warehouse": {
		"storage": [0, 0, 0, 0]
	}
}
set_behaviours = {
	"bay": {
		"mine": [5, 0, 0, 0],
		"hunt": [5, 0, 0, 0]
	},
	"warehouse": {
		"shrugs": [0, 0, 0, 0]
	}
}
build_values = {
	"bay": [0, 60, 0, 0],
	"warehouse": [0, 0, 0, 0],
	"ship": [0, 20, 0, 0]
}


def update_rect(self):
	self.rect.x = self.x
	self.rect.y = self.y
	self.rect.width = self.width
	self.rect.height = self.height


def distance_to_target(self):
	# print(self.target)
	t = self.target.rect.center
	x_dist = self.x - t[0]
	y_dist = self.y - t[1]
	return np.abs(math.hypot(x_dist, y_dist))


def angle_to_target(self):
	dx = self.target.rect.center[0]
	dy = self.target.rect.center[1]
	x = self.x - dx
	y = self.y - dy
	return math.degrees(math.atan2(x, y))
	# return math.atan2(x, y)


def turn(self):
	self.angle = angle_to_target(self) * self.agility


def move(self):
	# if not in arrived distance of target, turn and move toward target
	if distance_to_target(self, self.target) > self.target.arrived_distance:
		self.angle = angle_to_target(self, self.target) * self.agility
		self.x += math.cos(self.angle) * self.vel
		self.y -= math.sin(self.angle) * self.vel


def draw_beam(self, actor, colour=None):
	if colour is None:
		colour = [250, 250, 250]
	pygame.draw.line(self.screen, colour, (
		self.rect.center[0], self.rect.center[1]), (
		actor.rect.center[0], actor.rect.center[1]), 1)


def draw_explosion(object):
	tx, ty = int(object.x), int(object.y)
	variance = [-4, -2, 2, 4]
	for i in range(random.randint(20, 50)):
		pygame.draw.circle(object.screen, [255, 255, 255], (tx + random.choice(
			variance), ty + random.choice(variance)), random.randint(1, 5))
		pygame.draw.circle(object.screen, [0, 0, 0], (tx + random.choice(
			variance), ty + random.choice(variance)), random.randint(1, 5))
		pygame.draw.circle(object.screen, [255, 255, 255], (tx + random.choice(
			variance), ty + random.choice(variance)), random.randint(1, 5))


def set_composition(primary, secondary):
	# colour planet from amalgamation of the primary and secondary types
	rolls = composition_rolls
	prep_rgb = [0, 0, 0]
	choices = ["rubine", "verdite", "ceruliun"]
	for i in range(2):
		choices.append(primary)
	for i in range(1):
		choices.append(secondary)
	for i in range(rolls):
		choice = random.choice(choices)
		choice_rgb = mineral_info[choice]["rgb"]
		for i in range(3):
			prep_rgb[i] += choice_rgb[i]
	final_rgb = []
	for i in prep_rgb:
		final_rgb.append(i / rolls)
	return final_rgb


def tally_resources(player):
	total = [0, 0, 0, player.mupees]
	for h in player.hangars:
		for f in h.facilities:
			if f.kind == 'warehouse':
				for i in range(3):
					total[i] += f.ores[i]
	print(total)
	return total


def resource_check(required, available):
	# check ores available[*, *, *, -]
	for i in range(3):
		if required[i] > available[i]:
			print(f"Not enough {mineral_list[i]}")
			return False
	# check mupees available[-, -, -, *]
	if required[3] > available[3]:
		print(f"Not enough Mupees")
		return False
	else:
		return True


def withdraw_resources(player, resources):
	# pull each resource from warehouses, one type at a time
	# this should only ever run if availability of resources is guaranteed
	# extract ores
	for i in range(3):
		withdraw_qty = resources[i]
		while withdraw_qty > 0:
			for h in player.hangars:
				for f in h.facilities:
					if f.kind == 'warehouse':
						ores = f.ore.copy()
						av = ores[i]
						if av > withdraw_qty:
							withdraw_qty = 0
							f.ores[i] = withdraw_qty
						elif av < withdraw_qty:
							withdraw_qty -= av
							f.ores[i] -= f.ores[i]
	# extract mupees
	player.mupees -= resources[3]
	print("Transaction complete")


def hold_at_capacity(self):
	if sum(self.ores) >= self.hold_capacity:
		return True


def hold_empty(self):
	if sum(self.ores) <= 0:
		return True


def on_screen_check(self):
	if self.x < 0:
		return False
	if self.x > screen_width:
		return False
	if self.y < 0:
		return False
	if self.y > screen_height:
		return False
	return True


def transaction(buyer, target, particulars:list):
	count = 0
	# if the target has no room for the resources the transaction is cancelled.
	for i in particulars:
		pass
