import random
import sqlite3
import sys
import threading
import time

import pygame

import cfg
from class_player import Player
from class_station import Station
from class_sun import Sun
from class_spawner import Spawner
from class_freighter import Engine
from class_quadtree import Quadtree
from class_phaseCountDownDisplay import PhaseCountDownDisplay
from class_leaderboard import Leaderboard


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
		self.hostile_quadtree = Quadtree(self, self.screen_rect, max_objects=4, depth=0)
		self.friendly_quadtree = Quadtree(self, self.screen_rect, max_objects=4, depth=0)

		self.suns = []
		self.stations = []
		self.entities = []
		self.freighters = []
		self.projectiles = []
		self.explosions = []
		self.spawners = []
		self.hostiles = []
		self.players = []
		self.player_names = []

		self.next_populate_asteroids = time.time()
		self.next_watch_queue = time.time()
		self.next_force_feed_spawners = time.time() + cfg.force_feed_phase_time
		self.next_phase = time.time() + cfg.gather_phase_time

		self.gather_phase = True
		self.combat_phase = False
		self.round = 40
		self.round_label = cfg.bauhaus.render(
			f"Rd. {self.round}", True, cfg.col.bone)
		self.round_label_rect = self.round_label.get_rect()
		self.phase_display_text = "Defense in"
		self.phase_cd = PhaseCountDownDisplay(self)
		self.leader_board = Leaderboard(self)

		self.game_setup()

	def game_setup(self):
		# setup starting stations and players
		for _ in range(cfg.start_stations):
			self.new_station()
		for _ in range(cfg.start_suns):
			self.new_sun()
		for _ in range(cfg.start_spawners):
			self.new_spawner()

		# self.new_player("mupersega")
		for i in range(cfg.start_entities):
			self.new_player(f"P{i}")
		for _ in range(0):
			self.new_freight_train(
				random.randint(2, 6), random.choice(self.stations))

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

	def new_freight_train(self, carriages, destination_station):
		spawn_lines = [
			[400, 2000, 1100, 1200],
			[2000, 2100, 400, 1100]
		]
		ch = random.choice(spawn_lines)
		path = [
			pygame.Vector2(random.randint(ch[0], ch[1]), random.randint(ch[2], ch[3])),
			(destination_station.rect.centerx, destination_station.rect.bottom),
			(destination_station.rect.centerx, - 40 - (30 * carriages))
		]
		self.freighters.append(Engine(self, path, carriages))

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
		c.execute("SELECT * FROM queue WHERE completed=0")
		alles = c.fetchall()
		print(alles)
		if alles:
			threads = []
			for i in alles:
				sub_status = i[0]
				name = i[1]
				msg = i[2]
				c.execute("""
						UPDATE queue
						SET completed = 1
						WHERE user = ? AND message = ?;""", (name, msg))
				conn.commit()
				new_thread = threading.Thread(target=self.process, args=(sub_status, name, msg.split()))
				threads.append(new_thread)
				# new_thread.start()
			for i in threads:
				i.start()
			for i in threads:
				i.join()
		else:
			print("Nothing to process.")
			# print('error in try watch queue try block')
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
		if self.combat_phase:
			for _ in range(len(self.players)):
				sp = random.choice(self.spawners)
				sp.hold += self.round

	def initiate_combat_phase(self, phase_duration):
		# set environment for combat phase
		self.next_phase += phase_duration
		self.combat_phase = True
		self.gather_phase = False
		# set all player entities to "stay" behaviour:
		self.phase_display_text = "Gather in"
		for i in self.players:
			for j in i.entities:
				j.set_behaviour("stay")
		for i in self.stations:
			for j in i.hangars:
				for k in j.turrets:
					k.activate()
		for i in self.hostiles:
			i.hostile = True
		for i in self.spawners:
			i.desired_rotation_speed = self.round / 100 * len(self.players)
		for i in self.players:
			self.new_freight_train(int(self.round / 10) + 1, i.hangars[0].station)
		self.force_feed_spawners()

	def initiate_gather_phase(self, phase_duration):
		# set environment for gather phase
		self.next_phase += phase_duration
		self.round += 1
		self.round_label = cfg.bauhaus.render(
			f"Rd. {self.round}", True, cfg.col.bone)
		self.gather_phase = True
		self.combat_phase = False
		# set all player entities to "mine" behaviour:
		self.phase_display_text = "Defense in"
		for i in self.players:
			for j in i.entities:
				j.set_behaviour("mine")
		for i in self.spawners:
			i.desired_rotation_speed = 0
		for i in self.stations:
			for j in i.hangars:
				for k in j.turrets:
					return
					# k.deactivate()

	def phase_change_check(self, current_time):
		if current_time > self.next_phase:
			if not self.combat_phase:
				self.initiate_combat_phase(cfg.combat_phase_time)
			else:
				self.initiate_gather_phase(cfg.gather_phase_time)

		if self.combat_phase:
			pygame.draw.circle(self.screen, [255, 0, 0], (300, 40), 20)
		elif self.gather_phase:
			pygame.draw.circle(self.screen, [0, 255, 0], (300, 40), 20)

	def mainloop(self):  # sourcery no-metrics
		while True:
			curr_time = time.time()
			# Scheduled checks
			if curr_time > self.next_populate_asteroids:
				self.next_populate_asteroids += cfg.asteroid_pop_phase_time
				self.populate_asteroids()
			if curr_time > self.next_force_feed_spawners:
				self.next_force_feed_spawners += cfg.force_feed_phase_time
				self.force_feed_spawners()
			if curr_time > self.next_watch_queue:
				self.next_watch_queue += cfg.watch_queue_phase_time
				self.watch_queue()
				self.leader_board.order_players("kills")
				self.leader_board.blit_to_board()
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					pygame.quit()
					sys.exit()

				if event.type == pygame.KEYDOWN:
					# --DEBUG CONTROLS-- #
					# EXIT = Esc
					# SPAWN asteroid = space
					# SPAWN station = s
					# PRINT resource tally = r
					# BUILD bay = b
					# BUILD warehouse = w
					# UPGRADE miner = m
					# UPGRADE thrusters = t

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
			hostile_count = cfg.bauhaus.render(f"{len(self.hostiles)} enemies", True, cfg.col.pumpkin)
			self.screen.blit(hostile_count, (20, 20))
			self.leader_board.draw()

			# Prep Quadtrees
			# HOSTILE QUAD
			self.hostile_quadtree = Quadtree(self, self.screen_rect, max_objects=2, depth=0)
			for i in self.hostiles:
				self.hostile_quadtree.insert(i)
			# FRIENDLY QUAD
			self.friendly_quadtree = Quadtree(self, self.screen_rect, max_objects=4, depth=0)
			for i in self.freighters:
				for j in i.full_train:
					self.friendly_quadtree.insert(j)
			# Loops.
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

			for i in self.freighters:
				i.loop()

			for i in self.spawners:
				i.loop()

			for i in self.hostiles:
				i.loop()

			for i in self.players:
				i.process_auto()
				for j in i.entities:
					j.loop()

			for i in self.projectiles.copy():
				i.loop()

			for i in self.explosions.copy():
				i.loop()

			self.hostile_quadtree.draw([100, 0, 0])
			# self.friendly_quadtree.draw([0, 0, 100])
			self.phase_change_check(curr_time)
			self.phase_cd.loop()
			pygame.display.update()
			pygame.time.Clock().tick(self.fps)
			# print(f'|{len(self.freighters)}|')


if __name__ == "__main__":
	game = Game()
	game.mainloop()
