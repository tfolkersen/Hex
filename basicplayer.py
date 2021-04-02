import time
from utils import *
import math

class BasicPlayer:
	def __init__(self, playerNumber):
		self.playerNumber = playerNumber
		#visits, value
		self.stateInfo = {}
		self.expConst = 0.01
		self.rollouts = 0
		self.timeLimit = 5.0
		self.increment = True
		self.timeStep = 0


	def save(self, filename):
		f = open(filename, "w")
		f.write(json.dumps([self.timeStep, self.stateInfo]))
		f.close()

	def load(self, filename):
		f = open(filename, "r")
		l = f.read()
		data = json.loads(l)
		self.timeStep = data[0]
		self.stateInfo = data[1]
		f.close()
	

	def makePlay(self, state, timeStep):
		self.timeStep += 1
		timeLimit = self.timeLimit
		moves = [i for i in range(4, len(state.board)) if state.board[i] == 0]


		states = []
		visits = []
		values = []
		for m in moves:
			s = state.clone()
			s.setHexIndex(m, self.playerNumber)
			states.append(s)
	
			number = s.number()
			if number in self.stateInfo.keys():
				info = self.stateInfo[number]
				visits.append(info[0])	
				values.append(info[1])
			else:
				visits.append(0)
				values.append(0)

		heuristic = []
		for i in range(len(states)):
			#if visits[i] == 0:
			#	heuristic.append(0)
			#else:
			#	h = values[i] + self.expConst * math.sqrt(math.log(float(timeStep)) / visits[i])
			#	heuristic.append(h)

			h = values[i] + self.expConst * math.sqrt(math.log(float(self.timeStep)) / (visits[i] + 1))
			heuristic.append(h)

		end = time.time() + timeLimit
		self.rollouts = 0
		while time.time() < end:
			i = argmax(heuristic)

			outcome = self.rollout(states[i])
			v = 1 if outcome == self.playerNumber else -1
			visits[i] += 1
			values[i] = values[i] + (1.0 / visits[i]) * (v - values[i])

			#heuristic[i] = values[i] + self.expConst * math.sqrt(math.log(float(timeStep)) / visits[i])
			self.rollouts += 1
			#self.timeStep += 1 if self.increment else 0
			for i in range(len(states)):
				h = values[i] + self.expConst * math.sqrt(math.log(float(self.timeStep)) / (visits[i] + 1))
				heuristic[i] = h

		for i in range(len(states)):
			s = states[i]
			num = s.number()
			self.stateInfo[num] = [visits[i], values[i]]

		best = argmax(values)
		move = moves[best]

		state.setHexIndex(move, self.playerNumber)

	def rollout(self, state):
		s = state.clone()
		toPlay = nextPlayer(self.playerNumber)
		while s.outcome() == 0:
			s.randomMove(toPlay)
			toPlay = nextPlayer(toPlay)
		return s.outcome()


	# action = best action according to
	# val(a) + c * sqrt(ln(t) / vis(a))

