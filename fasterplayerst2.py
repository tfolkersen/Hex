import math
import time
from utils import nextPlayer, argmax
from state import numberAfterMove

#store transposition info in a table somewhere

bins = 10000
transposition = [{}] * bins

def getTableNode(stateNumber):
	binId = stateNumber % bins
	b = transposition[binId]
	if stateNumber in b.keys():
		return b[stateNumber]
	return None

def saveTableNode(node):
	sn = node.state.number()
	binId = sn % bins
	transposition[binId][sn] = node

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
		sn = self.state.number()
		tiles = self.state.bdist * self.state.wdist
		for m in moves:
			nextNum = numberAfterMove(sn, tiles, m, self.player)
			n = getTableNode(nextNum)
			if not n is None:
				self.children.append(n)
				continue
			s = self.state.clone()
			s.setHexIndex(m, self.player)
			#self.children.append(s)
			n = Node(s, np)
			self.children.append(n)
			saveTableNode(n)

class FasterPlayerST2:
	def __init__(self, playerNumber):
		self.playerNumber = playerNumber
		self.timeLimit = 0.0
		self.bootstrap = False
		self.expConst = 0.01
		self.maximizeNonVisited = False
		self.rollouts = 0
		self.gamma = 1.0

		self.root = None

	def goto(self, state):
		n = getTableNode(state.number())
		if not n is None:
			self.root = n
			n.parent = None
		n = Node(state, self.playerNumber)	
		saveTableNode(n)
		self.root = n

	def makePlay(self, state, timeStep):
		self.rollouts = 0
		self.goto(state)

		self.endTime = time.time() + self.timeLimit

		while time.time() < self.endTime:
			self.rollouts += 1
			self.rollout(self.root, True)

		#get children

		children = self.root.children
		values = [cn.value for cn in children]

		bestIndex = argmax(values)
		bestMove = self.root.state.moves()[bestIndex]

		state.setHexIndex(bestMove, self.playerNumber)

	def rollout(self, node, expand):
		#have no children
		if node.children is None:
			if expand:
				node.expandChildren()
				expand = False

		node.visits += 1

		#if node is terminal, return
		if node.state.outcome() != 0:
			v = 1 if node.state.outcome() == self.playerNumber else -1
			node.value = v
			return [v, self.gamma]

		#Node isn't terminal, get its children (should be generated already)
		moves = node.state.moves()
		children = node.children

		#No children, simulate rollout
		if children is None:
			p = node.player
			s = node.state.clone()
			gamma = 1
			while s.outcome() == 0:
				s.randomMove(p)
				p = nextPlayer(p)
				gamma *= self.gamma
			v = 1.0 if s.outcome() == self.playerNumber else -1
			node.value = node.value + (1.0 / node.visits) * (v * gamma - node.value)
			return [v, gamma * self.gamma]

		#compute heuristic
		heuristic = []
		sgn = 1 if node.player == self.playerNumber else -1
		for cn in children:
			bonus = 3 if self.maximizeNonVisited and cn.visits == 0 else 0
			h = sgn * cn.value + self.expConst * math.sqrt(math.log(node.visits) / (cn.visits + 1)) + bonus
			heuristic.append(h)


		bestIndex = argmax(heuristic)
		bestNode = children[bestIndex]
		v, gamma = self.rollout(bestNode, expand)

		node.value = node.value + (1.0 / node.visits) * (gamma * v - node.value)
		return [v, gamma * self.gamma]
