import pygame
import random
import math

from utility_classes import cfg
from environment_classes.class_explosion import Explosion


class Starseeker:
	"""This is a special weapon available only with favour used for destruction of 
	large items, namely spawn rings. It sets a detonate distance half way between
	the launch location and the target. At which time it will break into more versions
	of itself (clusters) and they will carry on to nodules on that ring."""
	def __init__(self, game, player, midpos, start_velocity, split, target=None):
		self.game = game
		self.player = player
		self.split = split
		self.split_mod = split / 6
		self.clusters = 2
		self.image = cfg.starseeker_imgs[self.split]

		self.location = pygame.Vector2(
			midpos[0] - self.image.get_width() * .5,
			midpos[1])
		self.acceleration = pygame.Vector2(0, 0)
		self.velocity = pygame.Vector2(start_velocity)
		self.speed = 1
		self.angle = random.randint(-360, 360)

		self.rect = pygame.Rect(self.location, self.image.get_size())

		self.target = target or self.find_target()
		self.detonate_distance = self.get_detonate_distance(.9)
		self.target_locked = False
		self.thrusters = 1

		# self.set_start_angle()

	def find_target(self):
		return random.choice(self.game.spawners)
	
	def get_detonate_distance(self, percent):
		this_vec = pygame.Vector2(self.rect.center)
		target_vec = pygame.Vector2(self.target.rect.center)
		return this_vec.distance_to(target_vec) * percent

	def lock_target(self):
		# Decrease speed then shoot off once target locked.
		if self.target_locked:
			return
		self.velocity *= .98
		# self.lock_time += 1
		if self.velocity.magnitude() < .02 + self.split_mod:
			self.target_locked = True
			self.thrusters = 7
			return
		if self.velocity.magnitude() < .05 + self.split_mod:
			self.thrusters = 4
			return
		if self.velocity.magnitude() < .1 + self.split_mod:
			self.thrusters = 2

	def set_start_angle(self):
		ang_vec = pygame.Vector2(self.location) - pygame.Vector2(self.location - self.velocity)
		rads = math.atan2(ang_vec[0], ang_vec[1])
		deg = math.degrees(rads)
		self.angle = deg

	def rotate(self):
		if self.target_locked:
			ang_vec = pygame.Vector2(self.rect.center) - self.target.rect.center
			rads = math.atan2(ang_vec[0], ang_vec[1])
			deg = math.degrees(rads)
			self.angle = deg
			# print(self.angle)
		else:
			ang_vec = pygame.Vector2(self.rect.center) - self.target.rect.center
			rads = math.atan2(ang_vec[0], ang_vec[1])
			deg = math.degrees(rads)
			self.angle += (deg - self.angle) * .03 + self.split_mod

	def move(self):
		self.acceleration = self.location - self.target.rect.center
		if self.target_locked:
			self.velocity = self.acceleration.normalize() * self.speed
			self.speed += self.speed ** -.6
		self.location -= self.velocity
		self.rect.topleft = self.location

	def make_trail(self):
		for i in range(self.thrusters):
			self.game.projectiles.append(
				StarseekerTrail(self.game, (
					self.rect.centerx + random.uniform(-i, i) * 3,
					self.rect.centery + random.uniform(-i, i) * 3),
								self))

	def kill(self):
		if self in self.game.projectiles.copy():
			self.game.projectiles.remove(self)
			self.game.explosions.append(
				Explosion(self.game, self.rect.center, 8 - self.split, random.choice([
					cfg.col.p_one,
					cfg.col.p_two,
					cfg.col.p_three,
					cfg.col.p_four,
						]),
					self.velocity))

	def detonate(self):
		# Die and spawn children if in detonation distance.
		d = self.location.distance_to(self.target.rect.center)
		if d <= self.detonate_distance:
			# If in detonation range but OUTSIDE kill range, only then break apart.
			if d > 300 and self.split < 3:
				# Spawn things and die.
				for _ in range(self.clusters):
					new_target = random.choice(self.target.nodules) if hasattr(self.target, "nodules") else self.target
					self.game.projectiles.append(Starseeker(
						self.game,
						self.player,
						self.rect.center,
						pygame.Vector2(random.uniform(-4, 4), random.uniform(-4, 4)) + (self.velocity * .5),
						self.split + 1,
						new_target
					))
					self.kill()
			# If in Kill range
			elif d < 20:
				self.kill()

	def draw(self):
		draw_image = pygame.transform.rotate(self.image, self.angle)
		self.game.screen.blit(draw_image, self.location)
		# pygame.draw.rect(self.game.screen, [50, 0, 0], self.rect)

	def loop(self):
		self.rotate()
		self.lock_target()
		self.make_trail()
		self.move()
		self.detonate()
		self.draw()


class StarseekerTrail:
	def __init__(self, game, location, parent):
		self.game = game
		self.parent = parent
		self.location = pygame.Vector2(location)
		self.velocity = pygame.Vector2(0, 1).rotate(-parent.angle)  # DO NOT CHANGE
		self.dim = [random.randint(0, 2), random.randint(0, 2)]

		self.life = random.randint(2, 10 - parent.split * 2)
		self.sparkle_window = random.randint(1, 2 + self.parent.split)
		self.rgb = random.choice([
			cfg.col.p_one,
			cfg.col.p_two,
			cfg.col.p_three,
			cfg.col.p_four,
		])

	def sparkle(self):
		pass

	def decay(self):
		self.life -= 1
		if self.life <= 0:
			self.game.projectiles.remove(self)

	def move(self):
		# DO NOT CHANGE - self.location += self.velocity * self.parent.thrusters
		self.location += self.velocity * self.parent.thrusters

	def draw(self):
		if self.life % self.sparkle_window == 0:
			pygame.draw.rect(self.game.screen, self.rgb, (self.location, self.dim))

	def loop(self):
		self.sparkle()
		self.decay()
		self.move()
		self.draw()

