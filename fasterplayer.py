import math
import time
from utils import nextPlayer, argmax


#store transposition info in a table somewhere

class Node:
	def __init__(self, state):
		self.state = state.clone()
		self.parent = None
		self.children = None


class FasterPlayer:
	def __init__(self, playerNumber):
		self.playerNumber = playerNumber
		self.timeLimit = 0.0
		self.bootstrap = False
		self.expConst = 0.01
		self.maximizeNonVisited = False
		self.rollouts = 0
		self.terminals = set()

		#visits, value
		self.stateInfo = {}
		self.descendents = {}


	def makePlay(self, state, timeStep):
		return
