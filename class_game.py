import random
import sqlite3
import sys
import threading

import pygame

import cfg
from class_player import Player
from class_station import Station
from class_sun import Sun


admins = ['mupersega']
conn = sqlite3.connect('/C:/Users/cambo/OneDrive/documents/bot_queue/queue.db')
c = conn.cursor()


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
		self.suns = []
		self.stations = []
		self.entities = []
		self.projectiles = []
		self.players = []
		self.player_names = []

		self.game_setup()

	def game_setup(self):
		# setup starting stations and players
		for i in range(cfg.start_stations):
			self.new_station()
		for i in range(cfg.start_suns):
			self.new_sun()
		for i in range(cfg.start_entities):
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
		if cmd == "!asteroids":
			if user in admins:
				try:
					for i in range(int(msg[1])):
						self.random_crash()
				except:
					# this is to catch incorrect number of args.
					print("set num asteroids")
					return
		# this play command will be processed at the game level to init a new player.
		if cmd == "!play":
			if user not in self.player_names:
				self.new_player(user)
				return
			else:
				print(f'{user} is already in the game.')
				return
		if len(message) > 1:
			args = message[1:]
		else:
			args = None
		for i in self.players:
			print(i.name)
			if i.name == user:
				i.perform(cmd, sub_status, args)
				print('beginning perform')

	def mainloop(self):
		loop_counter = 0
		secondary_loop = 0
		while True:
			# Watch for quit event.
			if loop_counter > 260:
				self.populate_asteroids()
				self.watch_queue()
				for player in self.players:
					player.process_auto()
				loop_counter = 0
				secondary_loop += 1
				if secondary_loop > 3:
					secondary_loop = 0
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
						self.players[0].bays[0].occupant.shoot()

			# Clear screen.
			self.screen.fill((0, 0, 0))

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

			for i in self.players:
				for j in i.entities:
					j.loop()

			for i in self.projectiles:
				i.loop()

			pygame.display.update()
			pygame.time.Clock().tick(self.fps)
			loop_counter += 1
			# Draw screen.


if __name__ == "__main__":
	game = Game()
	game.mainloop()
