import math
import time
from utils import nextPlayer, argmax

#store transposition info in a table somewhere

class Node:
	def __init__(self, state, player):
		self.state = state.clone()
		self.parent = None
		self.children = None
		self.player = player

	def expandChildren(self):
		if not self.children is None:
			return

		self.children = []
		moves = self.state.moves()
		np = nextPlayer(self.player)
		for m in moves:
			s = self.state.clone()
			s.setHexIndex(m, self.player)
			#self.children.append(s)
			self.children.append(Node(s, np))

class FasterPlayer:
	def __init__(self, playerNumber):
		self.playerNumber = playerNumber
		self.timeLimit = 0.0
		self.bootstrap = False
		self.expConst = 0.01
		self.maximizeNonVisited = False
		self.rollouts = 0

		#visits, value
		self.bins = 10000
		#self.stateInfo = [{} for i in range(self.bins)]
		self.stateInfo = {}
		#self.descendents = [{} for i in range(self.bins)]

		self.root = None

	def goto(self, state):
		if not self.root is None:
			children = self.root.children
			for c in children:
				if c.state.number() == state.number():
					self.root = c
					self.root.parent = None
					if self.root.children is None:
						self.root.expandChildren()
					return

		n = Node(state, self.playerNumber)
		self.root = n
		n.expandChildren()
		return

	def makePlay(self, state, timeStep):
		self.goto(state)

		self.endTime = time.time() + self.timeLimit

		while time.time() < self.endTime:
			self.rollouts += 1
			self.rollout(self.root)

		#get children

		children = self.root.children
		values = []
		for cn in children:
			inf = self.getInfo(cn.state.number())
			values.append(inf[1])

		bestIndex = argmax(values)
		bestMove = self.root.state.moves()[bestIndex]

		state.setHexIndex(bestMove, self.playerNumber)

	def getInfo(self, stateNumber):
		if stateNumber in self.stateInfo.keys():
			return self.stateInfo[stateNumber]
		else:
			self.stateInfo[stateNumber] = [0, 0]
			return [0, 0]
	#	binId = stateNumber % self.bins
	#	b = self.stateInfo[binId]
	#	if stateNumber in b.keys():
	#		return b[stateNumber]
	#	else:
	#		self.stateInfo[binId][stateNumber] = [0, 0]
	#		return [0, 0]

	def saveInfo(self, stateNumber, info):
		self.stateInfo[stateNumber] = info
		#binId = stateNumber % self.bins
		#self.stateInfo[binId][stateNumber] = info

	def rollout(self, node):
		#retrieve data about this node's state
		info = self.getInfo(node.state.number())

		info[0] += 1

		node.expandChildren()

		#if node is terminal, return
		if node.state.outcome() != 0:
			v = 1 if node.state.outcome() == self.playerNumber else -1
			info[1] = v
			self.saveInfo(node.state.number(), info)
			return v

		#Node isn't terminal, get its children (should be generated already)
		moves = node.state.moves()
		children = node.children

		childInfos = []
		for cn in children:
			inf = self.getInfo(cn.state.number())
			childInfos.append(inf)

		#compute heuristic
		heuristic = []
		sgn = 1 if node.player == self.playerNumber else -1
		bonus = 3 if self.maximizeNonVisited and inf[0] == 0 else 0
		for i in range(len(children)):
			inf = childInfos[i]
			h = sgn * inf[1] + self.expConst * math.sqrt(math.log(info[0]) / (inf[0] + 1)) + bonus
			heuristic.append(h)


		bestIndex = argmax(heuristic)
		bestNode = children[bestIndex]
		v = self.rollout(bestNode)

		info[1] = info[1] + (1.0 / info[0]) * (v - info[1]) 

		self.saveInfo(node.state.number(), info)
		return v
