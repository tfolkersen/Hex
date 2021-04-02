class RandomPlayer():
	def __init__(self, playerNumber):
		self.playerNumber = playerNumber
	
	def makePlay(self, state, timeStep):
		state.randomMove(self.playerNumber)

