import time
from utils import *
import math

class Node:
	def __init__(self, state, player):
		self.state = state.clone()
		self.player = player
		self.parent = None
		self.children = None
		self.moves = None
		self.visits = 0
		self.wins = 0
		self.losses = 0
	
	def expandChildren(self):
		if self.children is not None:
			return

		np = nextPlayer(self.player)
		self.children = []
		self.moves = [i for i in range(4, len(self.state.board)) if self.state.board[i] == 0]

		for m in self.moves:
			s = self.state.clone()
			s.setHexIndex(m, self.player)
			c = Node(s, np)
			c.parent = self
			self.children.append(c)

	def ucb(self, relativePlayer):
		v = self.value(relativePlayer)

		h = v + 0.01 * math.sqrt(math.log(self.parent.visits + 1) / (self.visits + 1))
		return h

	def value(self, relativePlayer):
		w = 0
		if relativePlayer == self.player:
			w = self.wins
		else:
			w = self.losses

		v = float(w) / self.visits if self.visits > 0 else 0
		return v


	def update(self, outcome):
		self.visits += 1
		
		if self.player == outcome:
			self.wins += 1
		else:
			self.losses += 1
		

class MCTSPlayer:
	def __init__(self, playerNumber):
		self.playerNumber = playerNumber
		self.root = None
		self.timeLimit = 0.0
		self.rollouts = 0
		self.discardCount = 0

	def goto(self, state):
		#no root or no children
		if self.root is None or self.root.children is None:
			n = Node(state, self.playerNumber)
			self.root = n
			self.discardCount += 1
			return

		#try to find node in children
		number = state.number()
		for c in self.root.children:
			if c.state.number() == number:
				
				if c.state.board != state.board:
					print("board mismatch")	
					print(c.state.board)
					print(state.board)
					exit(0)

				self.root = c
				c.parent = None
				return

		print("failed to find number")
		exit(0)

	def makePlay(self, state, timeStep):
		self.rollouts = 0

		self.message = ""

		#root is now given state
		self.goto(state)

		self.message += "OK " + str(state.number() == self.root.state.number())

		

		endTime = time.time() + self.timeLimit

		while time.time() < endTime:
			self.rollouts += 1
			#traverse tree to find a leaf
			stack = []
			node = self.root

			while True:
				stack.append(node)

				if node.children is None:
					break

				values = [c.ucb(self.playerNumber) for c in node.children]
				bestIndex = argmax(values)

				node = node.children[bestIndex]


			#expand the leaf if applicable
			outcome = node.state.outcome()
			if outcome == 0:
				node.expandChildren()
				#pick a child and do simulation
				node = node.children[random.randint(0, len(node.children) - 1)]
				stack.append(node)

				node.state.outcome()
				s = node.state.clone()
				p = node.player
				while s.outcome() == 0:
					s.randomMove(p)
					p = nextPlayer(p)
				outcome = s.outcome()


			#update the whole stack
			for i in range(0, len(stack), -1):
				n = stack[i]
				n.update(outcome)

		#now pick move
		values = [c.value(self.playerNumber) for c in self.root.children]
		bestIndex = argmax(values)
		bestMove = self.root.moves[bestIndex]

		self.message += " best: " + str(bestMove)

		if state.setHexIndex(bestMove, self.playerNumber) == False:
			self.message = "Failed to set " + str(bestMove) + " -- was already " + str(state.board[bestMove])
			if state.number() != self.root.state.number():
				self.message += " state numbers didn't match"

		self.goto(state)
		self.message += " discards: " + str(self.discardCount)

