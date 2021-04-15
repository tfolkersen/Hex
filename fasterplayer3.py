"""		fasterplayer3

	Defines a player that uses a transposition table and some simple
		inferior cell analysis.
"""

import math
import time
from utils import nextPlayer, argmax
from state import numberAfterMove

import os
import sys

largeNumber = 99999999999999 #weight solved states by this number for multithreaded players

"""		Node

	Represents a node in the MCTS search tree.
"""
class Node:
	"""		(constructor)

		state -- instance of State that this Node represents
		player -- integer of player to play from this Node (1 or 2)
		owner -- Player object owning this Node
	"""
	def __init__(self, state, player, owner):
		self.state = state.clone()
		self.children = None
		self.player = player
		self.visits = 0
		self.value = 0
		self.owner = owner
		self.winner = 0
		self.moves = state.moves()

		self.analyzed = False #True when inferior cell analysis has been applied

		self.capturedCells = [0] * len(self.state.board) #cells that have been captured
		self.deadCells = [0] * len(self.state.board) #cells that are dead
		self.shortcut = None #if inferior cell analysis has been applied and made a difference, this Node is the result

	"""		capturePattern1

		tempBoard -- temporary state board 
		shortcutState -- state being worked on
		
		Captured U pattern from "Hex, The Full Story" page 166 figure 9.17. Returns True
			if a change has been made.
	"""
	def capturePattern1(self, tempBoard, shortcutState):
		modified = False

		for color in [1, 2]:
			for s in range(4, len(tempBoard)):
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
					shortcutState.setHexIndex(f1, color, force = True)
					modified = True

				if tempBoard[f2] == 0:
					tempBoard[f2] = color
					self.capturedCells[f2] = color
					shortcutState.setHexIndex(f2, color, force = True)
					modified = True

		return modified

	"""		deadPattern1

		tempBoard -- temporary state board 
		shortcutState -- state being worked on


		Columns dead cell pattern from "Hex, The Full Story", page 166 figure 9.17.
			Returns True if a change has been made
	"""
	def deadPattern1(self, tempBoard, shortcutState):
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
			shortcutState.setHexIndex(m, nextPlayer(self.player))
			modified = True

		return modified

	"""		analyzeBoard

		Run inferior cell analysis on the board if it hasn't been done already.
	"""
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
				n2.expandChildren()
			else:
				n2 = Node(shortcut, self.player, self.owner)
				n2.expandChildren()
				self.shortcut = n2
				self.owner.saveTableNode(n2)

	"""		expandChildren

		Expands children nodes if they haven't been expanded.
	"""
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
			n = self.owner.getTableNode(nextNum, np) #look up node in transposition table
			if not n is None:
				self.children.append(n)
				continue
			s = self.state.clone()
			s.setHexIndex(m, self.player)
			n = Node(s, np, self.owner)
			self.children.append(n)
			self.owner.saveTableNode(n)

"""		FasterPlayer3

	A player that uses a transposition table and simple inferior cell analysis.
"""
class FasterPlayer3:
	"""		(constructor)
	"""
	def __init__(self, player):
		self.player = player
		self.timeLimit = 0.0 #time allowed for searches
		self.expConst = 0.01 #exploration coefficient
		self.maximizeNonVisited = False #if True, actions not explored will be given a large exploration bonus
		self.rollouts = 0 #rollouts simulated during the allowed time
		self.gamma = 1.0 #discount factor in range [0.0, 1.0], should stay at 1.0

		self.root = None #root Node in MCTS tree

		self.bins = 10000 #split transposition table to make it faster to search
		
		self.transposition = [[{}] * self.bins] * 2
		self.message = "" #if Player has something to print, put it here
		self.kt = 40 #knowledge threshold -- when a Node is visited this many times, cell analysis is applied to it

		self.opponentMove = -1 #what move the opponent did last, or -1 if not applicable

	"""		getTableNode

		stateNumber -- number of state to look up
		toPlay -- integer of player playing in this node (1 or 2)

		Look up a Node in the transposition table. Returns Node if found, otherwise
			returns None
	"""
	def getTableNode(self, stateNumber, toPlay):
		binId = stateNumber % self.bins
		b = self.transposition[toPlay - 1][binId]
		if stateNumber in b.keys():
			return b[stateNumber]
		return None

	"""		saveTableNode

		node -- instance of Node to save

		Saves given Node in the transposition table.
	"""
	def saveTableNode(self, node):
		sn = node.state.number()
		binId = sn % self.bins
		self.transposition[node.player - 1][binId][sn] = node

	"""		goto

		state -- instance of State to go to

		Makes the root Node the node representing the given State.
	"""
	def goto(self, state):
		#find opponent move
		prevBoard = [0] * len(state.board)
		if self.root:
			prevBoard = self.root.state.board
		for i in range(4, len(prevBoard)):
			if prevBoard[i] != state.board[i]:
				self.opponentMove = i
				break

		#look for node in transposition table
		n = self.getTableNode(state.number(), self.player)
		if not n is None:
			self.root = n
		else:
			n = Node(state, self.player, self)	
			self.saveTableNode(n)
			self.root = n

		self.root.expandChildren()
		self.root.analyzeBoard()

	"""		getPlay

		state -- instance of State to play in

		Given a State, returns a move to make. Searches for the allowed time.
	"""
	def getPlay(self, state):
		self.message = ""
		self.rollouts = 0
		self.goto(state)

		self.endTime = time.time() + self.timeLimit

		while time.time() < self.endTime:
			self.rollouts += 1
			self.rollout(self.root, True)

		if self.root.winner:
			self.message = str(self.player) + " knows that " + str(self.root.winner) + " wins"

		shortcutNode = self.root.shortcut if self.root.shortcut else self.root

		#get children
		#print("Root is using this state:")
		#shortcutNode.state.draw()
		#input("[Press Enter]")

		children = shortcutNode.children

		moves = state.moves()
		values = []

		for m in moves:
			if m in shortcutNode.moves:
				i = shortcutNode.moves.index(m)

				if shortcutNode.children[i].winner == self.player:
					return m

				values.append(shortcutNode.children[i].value)
			else:
				i = self.root.moves.index(m)
				if self.root.children[i].winner == self.player:
					return m
				values.append(shortcutNode.value)
				
		bestIndex = argmax(values)
		bestMove = moves[bestIndex]
		#bestMove = self.root.state.moves()[bestIndex]

		return bestMove

	"""		startJob

		tNum -- integer identifying this thread
		data -- Manager.dict object

		Runs search on a thread. Communicates with owner thread using "data".
	"""

	def startJob(self, tNum, data):
		flagName = str(tNum) + "flag"
		stateName = str(tNum) + "state"

		null = open(os.devnull, "w") #suppress messages when thread is killed
		sys.stderr = null

		while True: #busy loop...
			if data[flagName] == 1:
				state = data[stateName]
				self.getPlayInfo(state, tNum, data)
				data[flagName] = 0
			if data[flagName] == -1:
				return

	"""		getPlayInfo

		state -- instance of State to play on
		tNum -- integer identifying this thread
		returnDict -- instance of Manager.dict

		Runs search on this thread and writes resulting values into returnDict.
	"""
	def getPlayInfo(self, state, tNum, returnDict):
		_ = State(state.dims[0], state.dims[1]) #state helper might not have been passed to this thread...
		returnDict[str(tNum) + "msg"] = ""
		self.rollouts = 0
		self.goto(state)

		self.endTime = time.time() + self.timeLimit

		while time.time() < self.endTime:
			self.rollouts += 1
			self.rollout(self.root, True)

		if self.root.winner:
			returnDict[str(tNum) + "msg"] = str(self.player) + " knows that " + str(self.root.winner) + " wins"

		shortcutNode = self.root.shortcut if self.root.shortcut else self.root

		moves = state.moves()
		values = []
		visits = []

		for m in moves:
			if m in shortcutNode.moves:
				i = shortcutNode.moves.index(m)
				c = shortcutNode.children[i]
				v = c.value + (100 if c.winner == self.player else (0 if c.winner == 0 else -100))
				values.append(v)
				visits.append(c.visits)
			else:
				i = self.root.moves.index(m)
				c = self.root.children[i]
				v = shortcutNode.value + (100 if c.winner == self.player else (0 if c.winner == 0 else -100))
				values.append(v)
				visits.append(c.visits)
		
		returnDict[tNum] = [visits, values]
		returnDict[str(tNum) + "r"] = self.rollouts

	"""		rollout

		node -- instance of Node to start search from
		expand -- True if leaf node should be expanded. If False, will simulate rollout using random policy after leaf node.

		Recursively does one simulation starting from the given Node. Returns value of outcome, and discount factor. Expand
			is set to False after expanding one Node's children.
	"""
	def rollout(self, node, expand):
		if not node.shortcut is None:
			return self.rollout(node.shortcut, expand)

		if node.visits >= self.kt:
			node.analyzeBoard()

		if node.winner:
			return [node.value, 1.0]

		#have no children
		if node.children is None:
			if expand:
				node.expandChildren()
				expand = False

		node.visits += 1

		#if node is terminal, return
		if node.state.outcome() != 0:
			v = 1 if node.state.outcome() == self.player else -1
			node.winner = node.state.outcome()
			node.visits = largeNumber
			node.value = v
			return [v, 1.0]

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
			v = 1.0 if s.outcome() == self.player else -1
			node.value = node.value + (1.0 / node.visits) * (v * gamma - node.value)
			return [v, gamma * self.gamma]

		#compute heuristic
		heuristic = []
		sgn = 1 if node.player == self.player else -1
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
			if cn.winner == node.player: #this node is a winner because this node's player can move to a winning node
				node.winner = node.player
				node.visits = largeNumber
				node.value = cn.value
				return [node.value, 1.0]
			elif not cn.winner:
				allSolved = False
		if allSolved: #all solved but no winner, this node is a loss
			node.winner = nextPlayer(node.player)
			node.value = 1.0 if node.winner == self.player else -1.0
			return [node.value, 1.0]


		node.value = node.value + (1.0 / node.visits) * (gamma * v - node.value)
		return [v, gamma * self.gamma]
