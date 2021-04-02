class HumanPlayer:
	def __init__(self, playerNumber):
		self.playerNumber = playerNumber
		self.rollouts = 0
		self.stateInfo = {}

	def makePlay(self, state, timeStep):
		action = input("Enter player " + str(self.playerNumber) + " action: ")
		while not state.setHex(action, self.playerNumber):
			action = input("Can't place hex there, pick an open hex: ")

