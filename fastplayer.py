import time
from utils import *
from state import numberAfterMove
import math

class FastPlayer:
	def __init__(self, playerNumber):
		self.playerNumber = playerNumber
		#visits, value
		self.stateInfo = {}
		self.expConst = 0.01
		self.rollouts = 0
		self.timeLimit = 5.0
		self.increment = True
		self.timeStep = 0
		self.gamma = 0.9
		self.softmax = False
        self.tiles = 0


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
		self.rollouts = 0
		self.timeStep += 1
		self.endTime = time.time() + self.timeLimit
        self.tiles = state.bdist * state.wdist

		while time.time() < self.endTime:
			self.rollout(state, self.playerNumber)

        moves = state.moves()

		#states = []
        numbers = []
		visits = []
		values = []
		heuristic = []
		for m in moves:
            number = numberAfterMove(state.number(), self.tiles, m, self.playerNumber)
			#s = state.clone()
			#s.setHexIndex(m, self.playerNumber)
			#states.append(s)
			#number = s.number()

			if number in self.stateInfo.keys():
				info = self.stateInfo[number]
				visits.append(info[0])
				values.append(info[1])
				
			else:
				o = s.outcome()
				v = 0
				v = 1 if o == self.playerNumber else (0 if o == 0 else -1)
				visits.append(0)
				values.append(v)


			h = values[-1] - self.expConst * math.sqrt(math.log(float(self.timeStep)) / (visits[-1] + 1))
			heuristic.append(h)

		#best = argmax(heuristic)
		best = argmax(values)
		move = moves[best]

		state.setHexIndex(move, self.playerNumber)

	def rollout(self, state, player):
		if time.time() > self.endTime:
			return

		if state.outcome() != 0:
			v = 1 if state.outcome() == self.playerNumber else -1
			num = state.number()
			info = []
			if num in self.stateInfo.keys():
				info = self.stateInfo[num]
			else:
				info = [0, 0]

			info[0] += 1
			info[1] = v
			self.stateInfo[num] = info

			return [v, v]

		moves = [i for i in range(4, len(state.board)) if state.board[i] == 0]

		states = []
		visits = []
		values = []
		for m in moves:
			s = state.clone()
			s.setHexIndex(m, player)
			states.append(s)
	
			number = s.number()
			if number in self.stateInfo.keys():
				info = self.stateInfo[number]
				visits.append(info[0])	
				values.append(info[1])
			else:
				visits.append(0)
				o = s.outcome()
				v = 0
				v = 1 if o == self.playerNumber else (0 if o == 0 else -1)
				values.append(v)

		heuristic = [0] * len(states)

		sgn = -1 if player != self.playerNumber else 1
		for i in range(len(states)):
			h = sgn * values[i] + self.expConst * math.sqrt(math.log(float(self.timeStep)) / (visits[i] + 1))
			heuristic[i] = h

		if self.softmax:
			i = softmax(heuristic)
		else:
			i = argmax(heuristic)

		ret = self.rollout(states[i], nextPlayer(player))
		
		if ret is None:
			return

		reward, estimate = ret

		visits[i] += 1
		values[i] = values[i] + (1.0 / visits[i]) * (reward - values[i])

		self.rollouts += 1
		#self.timeStep += 1 if self.increment else 0

		for i in range(len(states)):
			s = states[i]
			num = s.number()
			self.stateInfo[num] = [visits[i], values[i]]

		return [reward, values[i]]

