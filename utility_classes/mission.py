import pygame
import random


class Mission:
	"""Mission classes are a utility class that is used to set win
	conditions. Once win conditions are set it searches the game class
	and checks if the mission needs updating/completion.
	ARGS INFO
	- game (the game object)
	- win_attributes (references to the actual game's attributes to be checked)
	- win_quantities (the number to be acquired of the corresponding attribute)
	"""
	def __init__(self, game):
		self.game = game
		self.mission_type = random.choice(["build", "collect", "destroy", "gain"])

	def retrieve_win_attributes(self):
		pass

	def check_win(self):
		for i, attr in enumerate(self.win_attributes):
			if attr.value >= self.win_quantities[i]:
				print(f"Mission for {self.win_quantities[i]} {attr}  complete.")