import math
import time
from utils import nextPlayer, argmax
from state import numberAfterMove
from collections import Counter

import os
import sys

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
		self.moves = [i for i in range(4, len(state.board)) if state.board[i] == 0]

		self.analyzed = False

		self.capturedCells = [0] * len(self.state.board)
		self.deadCells = [0] * len(self.state.board)
		self.shortcut = None

	#captured U pattern
	def capturePattern1(self, tempBoard, shortcutNode):
		modified = False

		for color in [1, 2]:
			for s in range(4, len(self.state.board)):
				#match around s
				if tempBoard[s] != color:
					continue

				su = self.state.dirAdj(s, "u")
				if su == -1 or tempBoard[su] != color:
					continue

				sd = self.state.dirAdj(s, "d")
				if sd == -1 or tempBoard[sd] != color:
					continue

				ul = self.state.dirAdj(su, "ul")
				if ul == -1 or tempBoard[ul] != color:
					continue

				dl = self.state.dirAdj(sd, "dl")
				if dl == -1 or tempBoard[dl] != color:
					continue

				f1 = self.state.dirAdj(s, "ul")
				f2 = self.state.dirAdj(s, "dl")

				if f1 == -1 or f2 == -1:
					continue

				if tempBoard[f1] == 0:
					tempBoard[f1] = color
					self.capturedCells[f1] = color
					shortcutNode.setHexIndex(f1, color, force = True)
					modified = True

				if tempBoard[f2] == 0:
					tempBoard[f2] = color
					self.capturedCells[f2] = color
					shortcutNode.setHexIndex(f2, color, force = True)
					modified = True

		return modified


	def capturePattern2(self, tempBoard, shortcutNode):
		modified = False

		colors = [1, 2]
		for color in colors:
			for s in range(4, len(tempBoard)):
				pass
				#start around s
	#columns
	def deadPattern1(self, tempBoard, shortcutNode):
		modified = False

		for s in range(4, len(tempBoard)):
			if tempBoard[s] == 0:
				continue
			c1 = tempBoard[s]
			c2 = nextPlayer(c1)

			su = self.state.dirAdj(s, "u")
			if su == -1 or tempBoard[su] != c1:
				continue

			m = self.state.dirAdj(s, "ur")
			if m == -1 or tempBoard[m] != 0:
				continue

			sr = self.state.dirAdj(m, "dr")
			if sr == -1 or tempBoard[sr] != c2:
				continue
		
			sru = self.state.dirAdj(sr, "u")
			if sru == -1 or tempBoard[sru] != c2:
				continue

			tempBoard[m] = nextPlayer(self.player)
			self.deadCells[m] = nextPlayer(self.player)
			shortcutNode.setHexIndex(m, nextPlayer(self.player))
			modified = True

		return modified


	def analyzeBoard(self):
		if self.analyzed:
			return

		self.analyzed = True

		tempBoard = list(self.state.board)
		shortcut = self.state.clone()

		modified = False
		while True:
			steady = True
			steady &= not self.capturePattern1(tempBoard, shortcut)
			steady &= not self.deadPattern1(tempBoard, shortcut)

			modified |= not steady
			if steady:
				break

		#now find shortcut node
		if modified:
			n2 = self.owner.getTableNode(shortcut.number(), self.player)
			if not n2 is None:
				self.shortcut = n2
			else:
				n2 = Node(shortcut, self.player, self.owner)
				self.shortcut = n2
				self.owner.saveTableNode(n2)

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
			n = self.owner.getTableNode(nextNum, np)
			if not n is None:
				self.children.append(n)
				continue
			s = self.state.clone()
			s.setHexIndex(m, self.player)
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
		
		self.transposition = [[{}] * self.bins] * 2
		self.message = ""
		self.visitCounts = Counter()
		self.kt = 40

		self.opponentMove = -1

	def getTableNode(self, stateNumber, toPlay):
		binId = stateNumber % self.bins
		b = self.transposition[toPlay - 1][binId]
		if stateNumber in b.keys():
			return b[stateNumber]
		return None

	def saveTableNode(self, node):
		sn = node.state.number()
		binId = sn % self.bins
		self.transposition[node.player - 1][binId][sn] = node

	def goto(self, state):
		#find opponent move
		prevBoard = [0] * len(state.board)
		if self.root:
			prevBoard = self.root.state.board
		for i in range(4, len(prevBoard)):
			if prevBoard[i] != state.board[i]:
				self.opponentMove = i
				break


		n = self.getTableNode(state.number(), self.playerNumber)
		if not n is None:
			self.root = n
			n.parent = None
		else:
			n = Node(state, self.playerNumber, self)	
			self.saveTableNode(n)
			self.root = n

		self.root.analyzeBoard()


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

		shortcutNode = self.root.shortcut if self.root.shortcut else self.root

		#get children
		#print("Root is using this state:")
		#shortcutNode.state.draw()
		#input("[Press Enter]")

		children = shortcutNode.children
		for i in range(len(children)):
			if children[i].winner == self.playerNumber:
				state.setHexIndex(self.root.state.moves()[i], self.playerNumber)
				return

		moves = [i for i in range(4, len(state.board)) if state.board[i] == 0]
		values = []

		for m in moves:
			if m in shortcutNode.moves:
				i = shortcutNode.moves.index(m)
				values.append(shortcutNode.children[i].value)
			else:
				values.append(shortcutNode.value)
				
			

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
		shortcutNode = self.root.shortcut if self.root.shortcut else self.root

		children = shortcutNode.children

		moves = [i for i in range(4, len(state.board)) if state.board[i] == 0]
		values = []
		visits = []

		for m in moves:
			if m in shortcutNode.moves:
				i = shortcutNode.moves.index(m)
				c = shortcutNode.children[i]
				v = c.value + (100 if c.winner == self.playerNumber else (0 if c.winner == 0 else -100))
				values.append(v)
				visits.append(shortcutNode.children[i].visits)
			else:
				values.append(shortcutNode.value)
				values.append(shortcutNode.visits)



		
		#queue.put([visits, values]
		returnDict[tNum] = [visits, values]
		returnDict[str(tNum) + "r"] = self.rollouts

	def rollout(self, node, expand):
		self.visitCounts[node.state.number()] += 1

		if self.visitCounts[node.state.number()] >= self.kt:
			node.analyzeBoard()

		if not node.shortcut is None:
			return self.rollout(node.shortcut, expand)

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
