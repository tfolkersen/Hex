"""		fasterPlayer2

	Defines a player that uses a transposition table
"""


import math
import time
from utils import nextPlayer, argmax
from state import numberAfterMove, State

import os
import sys

largeNumber = 99999999999999 #used for weighting values of states that have been solved

"""		Node

	Represents a node in the MCTS search tree
"""
class Node:
	"""		(constructor)

		state -- instance of State this node represents
		player -- integer of player to play at this Node (1 or 2)
		owner -- the Player object owning this Node
	"""
	def __init__(self, state, player, owner):
		self.state = state.clone()
		self.children = None #Nodes reachable from this Node
		self.player = player
		self.visits = 0
		self.value = 0
		self.owner = owner
		self.winner = 0 #If this Node is solved, this player wins

	"""		expandChildren

		If children haven't been expanded yet, expands them.
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
			n = self.owner.getTableNode(nextNum)	#check transposition table
			if not n is None:
				self.children.append(n)
				continue
			s = self.state.clone()
			s.setHexIndex(m, self.player)
			n = Node(s, np, self.owner)
			self.children.append(n)
			self.owner.saveTableNode(n) #store in transposition table

"""		FasterPlayer2

	A player that uses a transposition table
"""
class FasterPlayer2:
	"""		(constructor)

		player -- integer of player that this Player represents (1 or 2)
	"""
	def __init__(self, player):
		self.player = player
		self.timeLimit = 0.0 #How long this player has for search
		self.expConst = 0.01 #exploration coefficient
		self.maximizeNonVisited = False #if true, non explored children are given a large exploration bonus
		self.rollouts = 0 #rollouts done during the current search
		self.gamma = 1.0 #discount factor -- in [0.0, 1.0] but should leave at 1.0

		self.root = None #root Node

		self.bins = 10000 #split transposition table up so it's faster to search
		self.transposition = [{}] * self.bins
		self.message = ""	#if this player has something to print, put it here

	"""		getTableNode

		stateNumber -- integer representing State

		Returns Node in transposition table for the given State number.
			Returns None if Node not found
	"""
	def getTableNode(self, stateNumber):
		binId = stateNumber % self.bins
		b = self.transposition[binId]
		if stateNumber in b.keys():
			return b[stateNumber]
		return None

	"""		saveTableNode

		node -- (instance of Node), the Node to save

		Saves a Node into the transposition table
	"""
	def saveTableNode(self, node):
		sn = node.state.number()
		binId = sn % self.bins
		self.transposition[binId][sn] = node

	"""		goto

		state -- instance of State to go to

		Sets the root Node to one representing the given State
	"""
	def goto(self, state):
		n = self.getTableNode(state.number()) #check transposition table
		if not n is None:
			self.root = n
			return
		n = Node(state, self.player, self) #Node not found, make one and save it
		self.saveTableNode(n)
		self.root = n

	"""		getPlay

		state -- instance of State to play on

		Given a state, searches for the allowed time and returns a move.
	"""
	def getPlay(self, state):
		self.message = ""
		self.rollouts = 0
		self.goto(state)

		self.endTime = time.time() + self.timeLimit

		while time.time() < self.endTime:
			self.rollouts += 1
			self.rollout(self.root, True)

		if self.root.winner: #root is solved
			self.message = str(self.player) + " knows that " + str(self.root.winner) + " wins"

		#get children
		children = self.root.children
		for i in range(len(children)):
			if children[i].winner == self.player:
				return self.root.state.moves()[i]

		values = [cn.value for cn in children]

		bestIndex = argmax(values)
		bestMove = self.root.state.moves()[bestIndex]
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

		#print("Starting " + str(tNum))

		while True: #busy loop...
			if data[flagName] == 1: #there is a new job to do
				state = data[stateName]
				self.getPlayInfo(state, tNum, data)
				data[flagName] = 0 #consumed
			if data[flagName] == -1: #kill job
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

		#get children info
		children = self.root.children
		values = [cn.value + (100 if cn.winner == self.player else (0 if cn.winner == 0 else -100)) for cn in children] #add bonus to solved states
		visits = [cn.visits for cn in children]
		
		#return results
		returnDict[tNum] = [visits, values]
		returnDict[str(tNum) + "r"] = self.rollouts

	"""		rollout

		node -- instance of Node to start search from
		expand -- True if leaf node should be expanded. If False, will simulate rollout using random policy after leaf node.

		Recursively does one simulation starting from the given Node. Returns value of outcome, and discount factor. Expand
			is set to False after expanding one Node's children.
	"""
	def rollout(self, node, expand):
		if node.winner: #node is solved
			return [node.value, self.gamma]

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
			node.visits = largeNumber #set visits to some large number so that this node is heavily weighted by multi-threaded players
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
			node.value = node.value + (1.0 / node.visits) * (v * gamma - node.value) #value update
			return [v, gamma]

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
			if cn.winner == node.player:
				node.winner = node.player #this node is solved because the player here can go to a node where they win
				node.visits = largeNumber
				node.value = cn.value
				return [node.value, 1.0]
			elif not cn.winner:
				allSolved = False
		if allSolved: #all solved but no winner, so this node is a loss
			node.winner = nextPlayer(node.player)
			node.value = 1.0 if node.winner == self.player else -1.0
			return [node.value, 1.0]


		node.value = node.value + (1.0 / node.visits) * (gamma * v - node.value)
		return [v, gamma * self.gamma]
