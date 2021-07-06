import pygame
import random

from utility_classes import cfg


class Capsule:
	"""Projectile class paid for with favour which is launched from a station's launch bay. Upon target lock
	it pops and sends boosts to player bays/mining ships. It lasts for a time and glows underneath the bay.
	Note that the launch bay feeds args to this class."""
	def __init__(self, game, player, midpos, start_velocity, capsule_type):
		self.game = game
		self.player = player
		self.capsule_type = capsule_type

		# Type specifics
		self.image = cfg.capsule_info[capsule_type]["img"]
		self.ring_rgb = cfg.capsule_info[capsule_type]["ring_rgb"]
		self.beam_rgb = cfg.capsule_info[capsule_type]["beam_rgb"]
		self.glow_rgb = cfg.capsule_info[capsule_type]["glow_rgb"]
		self.attribute_mod = cfg.capsule_info[capsule_type]["attribute"]
		self.attrib_change = cfg.capsule_info[capsule_type]["attribute_change"]
		self.duration = cfg.capsule_info[capsule_type]["duration"]

		self.location = pygame.Vector2(
			midpos[0] - self.image.get_width() * .5,
			midpos[1])
		self.acceleration = pygame.Vector2(0, 0)
		self.velocity = pygame.Vector2(start_velocity)
		self.speed = 1
		self.angle = random.randint(-360, 360)

		self.rect = pygame.Rect(self.location, self.image.get_size())

		self.ready = False
		self.finished = False
		self.targets = self.establish_targets(cfg.capsule_info[capsule_type]["target_facility"])
		self.ring_radius = self.rect.width * .5

		self.beams = []
		self.pulses = []

	def spool_up(self):
		# Spooling up
		if self.velocity.magnitude() < 0.01:
			if not self.ready:
				self.ring_radius -= (self.ring_radius + 50) ** -.1
				if self.ring_radius <= self.rect.width * .5:
					self.ready = True
					self.create_beams_and_pulses()
					self.apply_boons()
		else:
			self.ring_radius += (self.ring_radius + 50) ** -.4

	def create_beams_and_pulses(self):
		for i in self.targets:
			self.beams.append(Beam(
				self, cfg.facility_w_third,
				self.rect.center,
				i.rect.center,
				self.beam_rgb
			))
			self.pulses.append(Pulse(
				self,
				i.rect.center,
				self.attribute_mod,
				self.attrib_change,
				self.duration,
				self.glow_rgb))

	def establish_targets(self, kind):
		return [facility for facility in self.player.hangars[0].facilities if facility.kind == kind]

	def move(self):
		self.location -= self.velocity
		self.rect.topleft = self.location
		self.velocity *= .95

	def kill(self):
		if self in self.game.projectiles.copy():
			self.game.projectiles.remove(self)
			self.retract_boons()

	def draw(self):
		self.game.screen.blit(self.image, self.rect.topleft)
		pygame.draw.circle(
			self.game.screen, self.ring_rgb, self.rect.center, self.ring_radius, 1)
	
	def update_beams(self):
		for i in self.beams:
			i.loop()
	
	def update_pulses(self):
		for i in self.pulses:
			i.loop()

	def apply_boons(self):
		# Only apply boosts to those that are not already boosted.
		for i in [t for t in self.targets if t.boosted is False]:
			i.boosted = True
			setattr(i, self.attribute_mod,
					getattr(i, self.attribute_mod) + self.attrib_change)

	def retract_boons(self):
		for i in [t for t in self.targets if t.boosted is True]:
			i.boosted = False
			setattr(i, self.attribute_mod,
					getattr(i, self.attribute_mod) - self.attrib_change)

	def loop(self):
		self.move()
		if not self.ready:
			self.spool_up()
			self.draw()
		self.update_beams()
		self.update_pulses()


class Beam:
	"""Supporting visual class of capsules drawn from pop location to target object, with a
	lifespan."""
	def __init__(self, parent, beam_width, start_pos, finish_pos, beam_rgb):
		self.parent = parent
		self.beam_width = beam_width
		self.start_pos = pygame.Vector2(start_pos[0] - beam_width * .5, start_pos[1] - beam_width * .5)
		self.finish_pos = pygame.Vector2(finish_pos[0] - beam_width * .5, finish_pos[1] - beam_width * .5)
		self.life = 100
		self.current_life = 100
		self.decay_value = 1
		self.rgb_one = beam_rgb
		self.rgb_two = [255, 255, 255]
	
	def update_rgb(self):
		pct = self.current_life / self.life
		self.rgb_one = [int(i * pct) for i in self.rgb_one]
		self.rgb_two = [int(i * pct) for i in self.rgb_two]

	def decay(self):
		self.current_life -= self.decay_value
		if self.current_life <= 0:
			self.kill()

	def kill(self):
		if self in self.parent.beams.copy():
			self.parent.beams.remove(self)
	
	def draw(self):
		pygame.draw.line(
			self.parent.game.screen, self.rgb_one, self.start_pos, self.finish_pos, self.beam_width)
		pygame.draw.line(
			self.parent.game.screen, self.rgb_two, self.start_pos, self.finish_pos, 1)

	def loop(self):
		self.decay()
		self.update_rgb()
		self.draw()
		

class Pulse:
	"""Supporting visual class of capsules drawn underneath target object, with a glowing pulse
	effect. This object has a lifespan and a boost attribute which is considered by the player."""
	def __init__(self, parent, pos, attr, amt, lifespan, glow_rgb):
		self.parent = parent
		self.pos = pygame.Vector2(pos)
		self.attr = attr
		self.amount = amt
		self.lifespan = lifespan
		# Glow information.
		self.base_colour = glow_rgb
		self.padding = cfg.capsule_info[self.parent.capsule_type]["padding"]
		self.glow_rgb = []
		self.max_glow_value = 100
		self.glow_value = 100

	def decay(self):
		# Life decay
		self.lifespan -= 1
		if self.lifespan <= 0:
			self.kill()
		# Glow decay
		self.glow_value -= self.glow_value ** -.1
		if self.glow_value <= 1:
			self.glow_value = self.max_glow_value

	def update_rgb(self):
		# Glow mechanic will pulse rgb from full value to black on repeat.
		pct = self.glow_value / self.max_glow_value
		self.glow_rgb = [int(i * pct) for i in self.base_colour]

	def kill(self):
		if self in self.parent.pulses.copy():
			self.parent.pulses.remove(self)
			if not len(self.parent.pulses):
				self.parent.kill()

	def draw(self):
		pygame.draw.circle(self.parent.game.screen, self.glow_rgb, self.pos, cfg.facility_w_third + self.padding)

	def loop(self):
		self.decay()
		self.update_rgb()
		self.draw()

