"""		humanplayer

	Defines human player class.
"""

"""		HumanPlayer

	Player that gets human input.
"""
class HumanPlayer:
	"""		(constructor)
		player -- integer of this player (1 or 2)
	"""
	def __init__(self, player):
		self.playerNumber = player

	"""		getPlay

		state -- (instance of State), state to make a play on

		Returns index of the move to make.
	"""
	def getPlay(self, state):
		while True:
			try:
				action = input("Enter player " + str(self.playerNumber) + " action: ")
				index = state.coordToIndex(action)
				return index
			except Exception as e:
				print("Bad coordinate")


