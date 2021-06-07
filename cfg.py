import math
import random

import numpy as np
import pygame

import colours as col

pygame.font.init()

ship_image = pygame.image.load('mining_ship_1.png')
starsated_image = pygame.image.load('starsated.png')
big_ship_teal = pygame.image.load('bigger_ship.png')
big_ship_purple = pygame.image.load('bigger_ship_purple.png')
big_ship_green = pygame.image.load('bigger_ship_green.png')
big_ship_red = pygame.image.load('bigger_ship_red.png')
leaderboard_font = pygame.font.SysFont("Agency FB", 22)
bauhaus = pygame.font.SysFont("Bauhaus 93", 25)


# CLASS SETTINGS #
# --Game-- #
screen_width = 1920
screen_height = 1080
# screen_width = 800
# screen_height = 600
fps = 120
universe_primary = "rubine"
universe_secondary = "verdite"
# st 15 = ent 124
start_stations = 1
start_suns = 1
start_spawners = 3
start_entities = 5
universe_max_asteroids = 300
max_hostiles = 200
asteroid_pop_phase_time = 10
watch_queue_phase_time = 2
force_feed_phase_time = 5
gather_phase_time = 15
combat_phase_time = 60

# --Entity-- #
ent_rgb = [250, 200, 100]
ent_interactable_distance = 20
ent_arrived_distance = 2
ent_size = 5
ent_start_capacity = 10
max_miner_lvl = 50
dropoff_speed = 980  # larger number will make drop off slower out of 1000

# --Station-- #
min_hangars_per = 5
max_hangars_per = 20
facility_w = 20
facility_w_third = int(facility_w * .33)
facility_h = 20
facility_h_third = int(facility_h * .33)
max_facilities = 6
# st_colour = [45, 89, 134] # pastel dark blue
st_colour = col.bone   # [102, 102, 153]
st_arm_colour = col.charcoal   # [75, 75, 100]

st_arrived_distance = 5
st_interactable_distance = 10
station_width = facility_w * 2
default_hangars = 30
lane_width = 15
x_pad = 3
y_pad = 1
st_x_offset = 390 # 390 for stream
st_y_offset = 55
station_spacing = station_width + (
	x_pad * 2 + facility_w * max_facilities) + lane_width

# --Sun-- #
sun_colour = [245, 245, 245]
sun_interactable_distance = 20
sun_arrived_distance = 10
sun_start_size = 1
sun_max_size = 100
max_planets_per_sun = 8
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
wh_colour = [89, 89, 89]
wh_starting_resources = [100, 0, 100]
wh_interactable_distance = 2
wh_arrived_distance = 1
# warehouse_colours = {
# 	"rubine": {"rgb": [255, 51, 51]},
# 	"verdite": {"rgb": [40, 200, 40]},
# 	"ceruliun": {"rgb": [40, 40, 255]}
# }
warehouse_colours = {
	"rubine": {"rgb": [255, 0, 0]},
	"verdite": {"rgb": [0, 255, 0]},
	"ceruliun": {"rgb": [0, 0, 255]}
}

# --Bay-- #
bay_colour = [180, 10, 180]
bay_interactable_distance = 3
bay_arrived_distance = 1
bay_bar_colours = [[229, 140, 138], [64, 89, 173], [104, 241, 170], [255, 200, 0]]

# --Turret-- #
turret_colour = col.cerulean_frost
turret_interactable_distance = 3
turret_arrived_distance = 1
# bars correspond to w, n, e, s
turret_bar_colours = [[229, 140, 138], [64, 89, 173], [104, 241, 170], [255, 200, 0]]
ammo_info = {
	"maul": {
		"min_range": 0,
		"max_range": 400,
		"barrel_rgb": [250, 0, 0],
		"mag_size": 200,
		"reload_time": 100,
		"reload_resources": [10, 0, 0],
		"ammo_hold_rgb": [100, 0, 0]
	},
	"lance": {
		"min_range": 0,
		"max_range": 750,
		"barrel_rgb": [0, 250, 0],
		"mag_size": 15,
		"reload_time": 500,
		"reload_resources": [0, 5, 0],
		"ammo_hold_rgb": [0, 100, 0]
	},
	"bolt": {
		"min_range": 0,
		"max_range": 2000,
		"barrel_rgb": [0, 0, 250],
		"mag_size": 10,
		"reload_time": 1000,
		"reload_resources": [0, 0, 5],
		"ammo_hold_rgb": [0, 0, 100]
	}
}
turret_shake = [[0.002, 0.001], [-0.01, 0.030], [0.009, -0.009]]

# --Spawner-- #
nodule_w, nodule_h = 9, 9

# --Location-- #
loc_colour = [255, 0, 255]
loc_interactable_distance = 2
loc_arrived_distance = 3

# --Freighter-- #
engine_life = 1000
carriage_life = 50

# --Miscellaneous-- #
composition_rolls = 10
tradables = ["rubine", "verdite", "ceruliun", "mupees"]
mineral_list = ["rubine", "verdite", "ceruliun"]
mineral_info = {
	"rubine": {"rgb": [255, 0, 0], "carriage_carry": [20, 0, 0]},
	"verdite": {"rgb": [0, 255, 0], "carriage_carry": [0, 20, 0]},
	"ceruliun": {"rgb": [0, 0, 255], "carriage_carry": [0, 0, 20]}
}

# the values in these lists correspond to [rubine, verdite, ceruliun, mupees]
upgrade_values = {
	"bay": {
		"miner": [15, 0, 0, 0],
		"hold": [5, 10, 15, 0],
		"thrusters": [0, 10, 0, 0],
	},
	"warehouse": {
		"hold": [20, 20, 10, 0]
	}
}
upgrade_amounts = {
	'warehouse': 10,
	'bay': 1
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
	"bay": [0, 100, 0, 0],
	"warehouse": [100, 0, 0, 0],
	"turret": [0, 0, 100, 0]
}

poly_coord_array = []
for i in range(10):
	this_poly = []
	for j in range(4):
		this_vec = []
		for k in range(2):
			this_vec.append(random.uniform(-10, 10))
		this_poly.append(this_vec)
	poly_coord_array.append(this_poly)

bolt_coord_array = []
for i in range(10):
	this_poly = []
	for j in range(4):
		this_vec = []
		for k in range(2):
			this_vec.append(random.uniform(-5, 5))
		this_poly.append(this_vec)
	bolt_coord_array.append(this_poly)


def update_rect(self):
	self.rect.x = self.x
	self.rect.y = self.y


def distance_to_target(self):
	# print(self.target)
	t = self.target.rect.center
	x_dist = self.rect.center[0] - t[0]
	y_dist = self.rect.center[1] - t[1]
	return np.abs(math.hypot(x_dist, y_dist))


def angle_to_target(self):
	dx = self.target.rect.center[0]
	dy = self.target.rect.center[1]
	x = self.rect.center[0] - dx
	y = self.rect.center[1] - dy
	rads = math.atan2(x, y)
	return math.degrees(rads)


def turn(self):
	self.angle = angle_to_target(self) * self.agility


def move(self):
	# if not in arrived distance of target, turn and move toward target
	if distance_to_target(self) > self.target.arrived_distance:
		self.trajectory = (math.cos(self.angle), -math.sin(self.angle))
		self.location += self.trajectory + self.location


def find_bar_length(current_lvl, max_lvl, total_px):
	bl = math.ceil((current_lvl / max_lvl) * total_px)
	print(bl)
	return bl


def draw_beam(self, actor, colour=None):
	if colour is None:
		colour = [250, 250, 250]
	pygame.draw.line(self.screen, colour, (
		self.rect.center[0], self.rect.center[1]), (
						 actor.rect.center[0], actor.rect.center[1]), 1)


def draw_explosion(explode_object):
	tx = int(explode_object.x)
	ty = int(explode_object.y)
	variance = [-4, -2, 2, 4]
	for _ in range(random.randint(20, 50)):
		pygame.draw.circle(explode_object.screen, [255, 255, 255], (tx + random.choice(
			variance), ty + random.choice(variance)), random.randint(1, 5))
		pygame.draw.circle(explode_object.screen, [0, 0, 0], (tx + random.choice(
			variance), ty + random.choice(variance)), random.randint(1, 5))
		pygame.draw.circle(explode_object.screen, [255, 255, 255], (tx + random.choice(
			variance), ty + random.choice(variance)), random.randint(1, 5))


def set_composition(primary, secondary):
	# colour planet from amalgamation of the primary and secondary types
	rolls = composition_rolls
	prep_rgb = [0, 0, 0]
	choices = ["rubine", "verdite", "ceruliun"]
	for _ in range(2):
		choices.append(primary)
	for _ in range(1):
		choices.append(secondary)
	for _ in range(rolls):
		choice = random.choice(choices)
		choice_rgb = mineral_info[choice]["rgb"]
		for j in range(3):
			prep_rgb[j] += choice_rgb[j]
	return [i / rolls for i in prep_rgb]


def tally_resources(player):
	total = [0, 0, 0, player.mupees]
	for h in player.hangars:
		for f in h.facilities:
			if f.kind == 'warehouse':
				for i in range(3):
					total[i] += f.ores[i]
	print(f'tallied resources - {total}')
	return total


def resource_check(required, available):
	# check ores available[*, *, *, -]
	for i in range(3):
		if required[i] > available[i]:
			print(f"Not enough {mineral_list[i]}")
			return False
	else:
		print('resources available for withdrawal')
		return True


def withdraw_resources(player, resources):
	# pull each resource from warehouses, one type at a time
	# this should only ever run if availability of resources is guaranteed - see tally_resources
	print(f'withdrawing - {resources}')
	for k in range(3):
		for i in range(resources.copy()[k]):
			done = False
			while not done:
				for facility in reversed(player.hangars[0].facilities):
					if facility.kind == 'warehouse' and facility.ores[k] > 0:
						print(f'fac#{k}\nwdl #{i}\npre({facility.ores[k]})')
						facility.ores[k] -= 1
						print(f'post({facility.ores[k]})')
						done = True
						break
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
	return self.y <= screen_height


def on_screen_check_vec(vec):
	if vec.x < 0:
		return False
	if vec.x > screen_width:
		return False
	if vec.y < 0:
		return False
	return vec.y <= screen_height

