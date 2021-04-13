"""		randomPlayer

	Defines random player class.
"""

import random

"""		RandomPlayer

	On its turn, makes a random play.
"""
class RandomPlayer():
	"""		(constructor)
		player -- integer representing player (1 or 2)
	"""
	def __init__(self, player):
		self.playerNumber = player
	
	"""		getPlay

		state -- (instance of State), state to play in
		
		Makes a random play.
	"""
	def getPlay(self, state):
		moves = state.moves()
		return moves[random.randint(0, len(moves) - 1)]
