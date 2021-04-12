import math
import time
from utils import nextPlayer, argmax
from state import numberAfterMove

import os
import sys

#store transposition info in a table somewhere


largeNumber = 99999999999999

class Node:
	def __init__(self, state, player, owner):
		self.state = state.clone()
		self.parent = None
		self.children = None
		self.player = player
		self.visits = 0
		self.value = 0
		self.owner = owner
		self.winner = 0

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
			n = self.owner.getTableNode(nextNum)
			if not n is None:
				self.children.append(n)
				continue
			s = self.state.clone()
			s.setHexIndex(m, self.player)
			#self.children.append(s)
			n = Node(s, np, self.owner)
			self.children.append(n)
			self.owner.saveTableNode(n)

class FasterPlayerST3:
	def __init__(self, playerNumber):
		self.playerNumber = playerNumber
		self.timeLimit = 0.0
		self.bootstrap = False
		self.expConst = 0.01
		self.maximizeNonVisited = False
		self.rollouts = 0
		self.gamma = 1.0

		self.root = None

		self.bins = 10000
		self.transposition = [{}] * self.bins
		self.message = ""


	def getTableNode(self, stateNumber):
		binId = stateNumber % self.bins
		b = self.transposition[binId]
		if stateNumber in b.keys():
			return b[stateNumber]
		return None

	def saveTableNode(self, node):
		sn = node.state.number()
		binId = sn % self.bins
		self.transposition[binId][sn] = node


	def goto(self, state):
		n = self.getTableNode(state.number())
		if not n is None:
			self.root = n
			n.parent = None
		n = Node(state, self.playerNumber, self)	
		self.saveTableNode(n)
		self.root = n

	def makePlay(self, state, timeStep):
		self.message = ""
		self.rollouts = 0
		self.goto(state)

		self.endTime = time.time() + self.timeLimit

		while time.time() < self.endTime:
			self.rollouts += 1
			self.rollout(self.root, True)

		if self.root.winner:
			self.message = str(self.playerNumber) + " knows that " + str(self.root.winner) + " wins"

		#get children

		children = self.root.children
		for i in range(len(children)):
			if children[i].winner == self.playerNumber:
				state.setHexIndex(self.root.state.moves()[i], self.playerNumber)

		values = [cn.value for cn in children]

		bestIndex = argmax(values)
		bestMove = self.root.state.moves()[bestIndex]

		state.setHexIndex(bestMove, self.playerNumber)

	def startJob(self, tNum, data):
		flagName = str(tNum) + "flag"
		stateName = str(tNum) + "state"

		null = open(os.devnull, "w")
		sys.stderr = null

		while True:
			if data[flagName] == 1:
				state = data[stateName]
				self.getPlayInfo(state, 0, tNum, data)
				data[flagName] = 0
			if data[flagName] == -1:
				return

	def getPlayInfo(self, state, timeStep, tNum, returnDict):
		returnDict[str(tNum) + "msg"] = ""
		self.rollouts = 0
		self.goto(state)

		self.endTime = time.time() + self.timeLimit

		while time.time() < self.endTime:
			self.rollouts += 1
			self.rollout(self.root, True)

		if self.root.winner:
			pass
			returnDict[str(tNum) + "msg"] = str(self.playerNumber) + " knows that " + str(self.root.winner) + " wins"

		#get children
		children = self.root.children
		values = [cn.value + (100 if cn.winner == self.playerNumber else (0 if cn.winner == 0 else -100)) for cn in children]
		visits = [cn.visits for cn in children]
		
		#queue.put([visits, values]
		returnDict[tNum] = [visits, values]
		returnDict[str(tNum) + "r"] = self.rollouts

	def rollout(self, node, expand):
		if node.winner:
			return [node.value, self.gamma]

		#have no children
		if node.children is None:
			if expand:
				node.expandChildren()
				expand = False

		node.visits += 1

		#if node is terminal, return
		if node.state.outcome() != 0:
			v = 1 if node.state.outcome() == self.playerNumber else -1
			node.winner = node.state.outcome()
			node.visits = largeNumber
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

		#Check for solved children
		allSolved = True
		for cn in children:
			if cn.winner == node.player:
				node.winner = node.player
				node.visits = largeNumber
				node.value = cn.value
				return [node.value, self.gamma]
			elif not cn.winner:
				allSolved = False
		if allSolved:
			node.winner = nextPlayer(node.player)
			node.value = 1.0 if node.winner == self.playerNumber else -1.0
			return [node.value, self.gamma]


		node.value = node.value + (1.0 / node.visits) * (gamma * v - node.value)
		return [v, gamma * self.gamma]
