import random
import sqlite3
import sys
import threading
import time
import os

import pygame

import cfg
from class_player import Player
from class_station import Station
from class_sun import Sun
from class_spawner import Spawner
from class_quadtree import Quadtree


admins = ['mupersega']
conn = sqlite3.connect('/C:/db/queue.db')
c = conn.cursor()
#
# x = -1800
# y = 450
# os.environ['SDL_VIDEO_WINDOW_POS'] = f"{x},{y}"


class Game:
	"""Class to manage the whole game."""

	def __init__(self):
		# self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
		self.screen = pygame.display.set_mode((
			cfg.screen_width, cfg.screen_height))
		self.fps = cfg.fps

		self.universe_primary = cfg.universe_primary
		self.universe_secondary = cfg.universe_secondary

		# lists of created objects
		self.screen_rect = pygame.Rect(0, 0, cfg.screen_width, cfg.screen_height)
		self.main_quadtree = Quadtree(self, self.screen_rect, max_objects=4, depth=0)
		self.suns = []
		self.stations = []
		self.entities = []
		self.projectiles = []
		self.explosions = []
		self.spawners = []
		self.players = []
		self.player_names = []

		self.next_populate_asteroids = time.time()
		self.next_watch_queue = time.time()
		self.next_force_feed_spawners = time.time() + cfg.force_feed_phase_time
		self.next_phase = time.time() + cfg.gather_phase_time

		self.gather_phase = True
		self.combat_phase = False

		self.game_setup()

	def game_setup(self):
		# setup starting stations and players
		for _ in range(cfg.start_stations):
			self.new_station()
		for _ in range(cfg.start_suns):
			self.new_sun()

		for _ in range(cfg.start_spawners):
			self.new_spawner()
		for _ in range(cfg.start_entities):
			self.new_player("mupersega")

	def new_player(self, name):
		new_player = Player(self, name)
		self.player_names.append(name)
		self.players.append(new_player)

	def new_station(self):
		new_station = Station(self, len(self.stations), random.randint(
			cfg.min_hangars_per, cfg.max_hangars_per))
		self.stations.append(new_station)

	def new_sun(self):
		new_sun = Sun(self, 6)
		self.suns.append(new_sun)
	
	def new_spawner(self):
		new_spawner = Spawner(self)
		self.spawners.append(new_spawner)

	def random_crash(self):
		potentials = []
		for i in self.suns:
			for j in i.planets:
				potentials.append(j)
		chosen_planet = random.choice(potentials)
		chosen_planet.spawn_asteroids()

	def count_asteroids(self):
		total_asteroids = 0
		for sun in self.suns:
			for planet in sun.planets:
				total_asteroids += len(planet.asteroids)
		return total_asteroids

	def populate_asteroids(self):
		# I need to connect the spawning of asteroids to the current amount of asteroids in the world.
		if random.randint(0, 1000) > ((self.count_asteroids() / cfg.universe_max_asteroids) * 1000):
			self.random_crash()

	def clear_old_projectiles(self):
		for i in self.projectiles.copy():
			if i.life < 1:
				self.projectiles.remove(i)

	def watch_queue(self):
		# clear any completed rows
		c.execute("DELETE FROM queue WHERE completed=1")
		conn.commit()
		print("CLEAN")
		# try to
		try:
			c.execute("SELECT * FROM queue WHERE completed=0")
			full = c.fetchone()
			print(full)
			sub_status = full[0]
			name = full[1]
			msg = full[2]
			c.execute("""
					UPDATE queue
					SET completed = 1
					WHERE user = ? AND message = ?;""", (name, msg))
			conn.commit()
			new_thread = threading.Thread(target=self.process, args=(sub_status, name, msg.split()))
			new_thread.start()
		except:
			print('error in try watch queue try block')
			return

	def process(self, sub_status, name, msg):
		sub_status = sub_status
		user = name.lower()
		print(msg)
		message = msg
		cmd = msg[0]
		print(f'{user} time to {cmd}')
		# game commands are those that are not player specific or are initiated by the creator. ME!!!
		if cmd == "!asteroids" and user in admins:
			try:
				for _ in range(int(msg[1])):
					self.random_crash()
			except:
				# this is to catch incorrect number of args.
				print("set num asteroids")
				return
		# this play command will be processed at the game level to init a new player.
		if cmd == "!play":
			if user not in self.player_names:
				self.new_player(user)
			else:
				print(f'{user} is already in the game.')
			return
		args = message[1:] if len(message) > 1 else None
		for i in self.players:
			print(i.name)
			if i.name == user:
				i.perform(cmd, sub_status, args)
				print('beginning perform')

	def force_feed_spawners(self):
		for _ in range(5):
			sp = random.choice(self.spawners)
			sp.hold += 10

	def initiate_combat_phase(self, phase_duration):
		# set environment for combat phase
		self.next_phase += phase_duration
		self.combat_phase = True
		self.gather_phase = False
		# set all player entities to "stay" behaviour:
		for i in self.players:
			for j in i.entities:
				j.set_behaviour("stay")
		for i in self.stations:
			for j in i.hangars:
				for k in j.turrets:
					k.activate()

	def initiate_gather_phase(self, phase_duration):
		# set environment for gather phase
		self.next_phase += phase_duration
		self.gather_phase = True
		self.combat_phase = False
		# set all player entities to "mine" behaviour:
		for i in self.players:
			for j in i.entities:
				j.set_behaviour("mine")
		for i in self.stations:
			for j in i.hangars:
				for k in j.turrets:
					k.deactivate()

	def phase_change_check(self):
		if time.time() > self.next_phase:
			if not self.combat_phase:
				self.initiate_combat_phase(cfg.combat_phase_time)
			else:
				self.initiate_gather_phase(cfg.gather_phase_time)

		if self.combat_phase:
			pygame.draw.circle(self.screen, [255, 0, 0], (300, 40), 20)
		elif self.gather_phase:
			pygame.draw.circle(self.screen, [0, 255, 0], (300, 40), 20)

	def mainloop(self):  # sourcery no-metrics
		loop_counter = 0
		while True:
			curr_time = time.time()
			# Scheduled checks
			# if curr_time > self.next_populate_asteroids:
			# 	self.next_populate_asteroids += cfg.asteroid_pop_phase_time
			# 	self.populate_asteroids()
			# if curr_time > self.next_force_feed_spawners:
			# 	self.next_force_feed_spawners += cfg.force_feed_phase_time
			# 	self.force_feed_spawners()
			# if curr_time > self.next_watch_queue:
			# 	self.next_watch_queue += cfg.watch_queue_phase_time
			# 	self.watch_queue()
			#
			if loop_counter > 260:
				self.populate_asteroids()
				self.watch_queue()
				self.force_feed_spawners()
				loop_counter = 0
				# secondary_loop += 1
				# if secondary_loop > 3:
				# 	secondary_loop = 0
			# Watch for quit event.
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					pygame.quit()
					sys.exit()

				if event.type == pygame.KEYDOWN:
					# EXIT = Esc
					# SPAWN asteroid = space
					# SPAWN station = s
					# PRINT resource tally = r
					# BUILD bay = b
					# BUILD warehouse = w
					# UPGRADE miner = m
					# UPGRADE thrusters = t
					# SHOOT projectile = p

					if event.key == pygame.K_SPACE:
						self.random_crash()
					if event.key == pygame.K_ESCAPE:
						pygame.quit()
						sys.exit()
					if event.key == pygame.K_s:
						self.new_station()
					if event.key == pygame.K_r:
						cfg.tally_resources(self.players[0])
					if event.key == pygame.K_t:
						msg = "!upgrade bay 1 thrusters"
						self.process("1", "mupersega", msg.split())
					if event.key == pygame.K_m:
						msg = "!upgrade bay 1 miner"
						self.process("1", "mupersega", msg.split())
					if event.key == pygame.K_b:
						msg = "!build bay"
						self.process("1", "mupersega", msg.split())
					if event.key == pygame.K_w:
						msg = "!build warehouse"
						self.process("1", "mupersega", msg.split())
					if event.key == pygame.K_p:
						if self.players[0].bays[0].occupant.behaviour == "mine":
							self.players[0].bays[0].occupant.set_behaviour("stay")
						elif self.players[0].bays[0].occupant.behaviour == "stay":
							self.players[0].bays[0].occupant.set_behaviour("mine")
						for p in self.players:
							for t in p.turrets:
								t.shoot()

			# Clear screen.
			self.screen.fill((0, 0, 0))

			# Prep Quadtree
			self.main_quadtree = Quadtree(self, self.screen_rect, max_objects=4, depth=0)
			for i in self.spawners:
				for j in i.roamers:
					self.main_quadtree.insert(j)
			# loops.
			for i in self.suns:
				i.loop()
				for j in i.planets:
					j.loop()
					for k in j.asteroids:
						k.loop()

			for i in self.stations:
				i.loop()
				for j in i.hangars:
					if j:
						j.draw()
						j.loop()
				for j in i.hangars:
					if j:
						j.draw_turrets()

			for i in self.spawners:
				i.loop()
				for j in i.roamers:
					j.loop()

			for i in self.players:
				i.process_auto()
				for j in i.entities:
					j.loop()

			for i in self.projectiles.copy():
				i.loop()

			for i in self.explosions.copy():
				i.loop()

			# self.main_quadtree.draw()
			# self.phase_change_check()
			pygame.display.update()
			pygame.time.Clock().tick(self.fps)
			loop_counter += 1


if __name__ == "__main__":
	game = Game()
	game.mainloop()
