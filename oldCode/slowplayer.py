import math
from utils import argmax, nextPlayer
import time

class SlowPlayer:
	def __init__(self, playerNumber):
		self.playerNumber = playerNumber
		self.timeLimit = 0.0
		self.bootstrap = False
		self.expConst = 0.01
		self.maximizeNonVisited = False
		self.rollouts = 0

		#visits, value
		self.stateInfo = {}

	def makePlay(self, state, timeStep):
		#Given state, do search

		self.endTime = time.time() + self.timeLimit

		while time.time() < self.endTime:
			self.rollouts += 1
			self.rollout(state, self.playerNumber)

		#Now get all children

		moves = state.moves()

		children = []
		values = []
		for m in moves:
			s = state.clone()
			s.setHexIndex(m, self.playerNumber)
			children.append(s)

			if s.number() in self.stateInfo.keys():
				values.append(self.stateInfo[s.number()][1])
			else:
				values.append(0)


		bestIndex = argmax(values)

		bestMove = moves[bestIndex]
		state.setHexIndex(bestMove, self.playerNumber)


	#returns result of this simulation
	def rollout(self, state, player):
		#Get this state's info

		info = []
		if state.number() in self.stateInfo.keys():
			info = self.stateInfo[state.number()]
		else:
			info = [0, 0]

		info[0] += 1

		#If state is terminal
		if state.outcome() != 0:
			v = 1 if state.outcome() == self.playerNumber else -1
			info[1] = v
			self.stateInfo[state.number()] = info
			return v

		#State is not terminal, get children
		moves = state.moves()
		states = []
		childInfo = []
		for m in moves:
			s = state.clone()
			s.setHexIndex(m, player)
			states.append(s)
			if s.number() in self.stateInfo.keys():
				childInfo.append(self.stateInfo[s.number()])
			else:
				childInfo.append([0, 0])


		#Evaluate heuristic
		heuristic = []
		
		sgn = 1 if player == self.playerNumber else -1
		for i in range(len(states)):
			bonus = 3.0 if self.maximizeNonVisited and childInfo[i][0] == 0 else 0
			h = sgn * childInfo[i][1] + self.expConst * math.sqrt(math.log(info[0]) / (childInfo[i][0] + 1)) + bonus
			heuristic.append(h)

		#Pick best option according to current player
		bestIndex = argmax(heuristic)
		bestState = states[bestIndex]

		outcome = self.rollout(bestState, nextPlayer(player))

		if self.bootstrap:
			est = self.stateInfo[bestState.number()][1]
			info[1] = info[1] + (1.0 / info[0]) * (outcome * 0.5 + est * 0.5 - info[1])
		else:
			info[1] = info[1] + (1.0 / info[0]) * (outcome - info[1])

		self.stateInfo[state.number()] = info
		for i in range(len(states)):
			self.stateInfo[states[i].number()] = childInfo[i]

		return outcome
