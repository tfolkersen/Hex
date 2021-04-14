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
		self.visits = 0
		self.value = 0

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

class FasterPlayerNT:
	def __init__(self, playerNumber):
		self.playerNumber = playerNumber
		self.timeLimit = 0.0
		self.bootstrap = False
		self.expConst = 0.01
		self.maximizeNonVisited = False
		self.rollouts = 0

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
		values = [cn.value for cn in children]

		bestIndex = argmax(values)
		bestMove = self.root.state.moves()[bestIndex]

		state.setHexIndex(bestMove, self.playerNumber)

	def rollout(self, node):
		node.expandChildren()

		node.visits += 1

		#if node is terminal, return
		if node.state.outcome() != 0:
			v = 1 if node.state.outcome() == self.playerNumber else -1
			node.value = v
			return v

		#Node isn't terminal, get its children (should be generated already)
		moves = node.state.moves()
		children = node.children

		#compute heuristic
		heuristic = []
		sgn = 1 if node.player == self.playerNumber else -1
		for cn in children:
			bonus = 3 if self.maximizeNonVisited and cn.visits == 0 else 0
			h = sgn * cn.value + self.expConst * math.sqrt(math.log(node.visits) / (cn.visits + 1)) + bonus
			heuristic.append(h)


		bestIndex = argmax(heuristic)
		bestNode = children[bestIndex]
		v = self.rollout(bestNode)

		node.value = node.value + (1.0 / node.visits) * (v - node.value)
		return v
