import random
import re
import time
import os
import copy
import math
import json

'''
░·▓
⬢ (bad)
⬣ (good)
'''

#UL, UR, DR, DL
#0, B, W
#0, BL, RE

cWhite = "\033[0m"
cBlue = "\033[94m"
cRed = "\033[31m"

print("\033[0m")

def playerToColor(id):
	if id == 0:
		return cWhite + "⬣ " + cWhite
	if id == 1:
		return cBlue + "⬣ " + cWhite
	if id == 2:
		return cRed + "⬣ " + cWhite
	raise "Bad player ID exception"

alphabet = "abcdefghijklmnopqrstuvwxyz"
class State:
	def __init__(self, wdist = 5, bdist = 5):
		self.board = [1, 2, 1, 2] + [0] * (bdist * wdist)
		self.bdist = bdist
		self.wdist = wdist
		self.bchars = [cBlue + alphabet[i] + cWhite for i in range(0, wdist)]
		self.wchars = [cRed + str(i) + cWhite for i in range(1, bdist + 1)]
		self.labels = self.bchars[::-1] + [" "] + self.wchars

		self.labelLengths = [len(alphabet[i]) for i in range(0, wdist)][::-1] + [1] +\
			[len(str(i)) for i in range(1, bdist + 1)]

		self.cacheNum = 0
		self.cacheResult = 0

		self.top = [4 + 0 + bdist * i for i in range(wdist)]
		self.bottom = [4 + bdist - 1 + bdist * i for i in range(wdist)]
		self.left = [4 + i for i in range(bdist)]
		self.right = [4 + (wdist - 1) * bdist + i for i in range(bdist)]

		self.edges = [self.top, self.right, self.bottom, self.left]	

	def clone(self):
		return copy.deepcopy(self)

	def pathTest(self, start, end, player):
		board = self.board

		if board[start] != player or board[end] != player:
			return False

		todo = [start]
		closed = [False] * len(board)

		while todo:
			v = todo.pop()
			closed[v] = True
			neighbours = self.adjacent(v)
			for n in neighbours:
				if closed[n]:
					continue
				if n == end:
					if board[n] == player:
						return True
					return False
				if board[n] == player:
					todo.append(n)
		return False

	def result(self):
		if self.cacheResult == -1:
			self.cacheResult = 0
			if self.pathTest(0, 2, 1): #Path for black (from 0 to 2)
				self.cacheResult = 1
			elif self.pathTest(1, 3, 2): #Path for white (from 1 to 3)
				self.cacheResult = 2
		return self.cacheResult

	def number(self):
		if self.cacheNum == -1:
			num = 0
			tiles = self.wdist * self.bdist
			for i in range(4, len(self.board)):
				v = self.board[i]
				num += 1 << (i - 4) + (v - 1) * tiles if v != 0 else 0
			self.cacheNum = num

		return self.cacheNum

	def __bwToIndex(self, bCoord, wCoord, silent = False):
		wdist = self.wdist
		bdist = self.bdist

		if type(bCoord) is str and bCoord.isalpha():
			bCoord = ord(bCoord.lower()) - ord("a")
		else:
			bCoord -= 1

		wCoord = int(wCoord)
		wCoord -= 1

		if not silent:
			if (bCoord < 0 or bCoord >= wdist) or (wCoord < 0 or wCoord >= bdist):
				raise "Bad bwToIndex coordinates: (" + str(bCoord) + ", " + str(wCoord) + ")"

		index = bCoord * bdist + wCoord + 4
		return index


	def randomize(self):
		self.cacheNum = -1
		for i in range(4, len(self.board)):
			self.board[i] = random.randint(0, 2)

	#given a board index, return adjacent board indices
	#	b + 1 ---> index + bdist
	#	w + 1 ---> index + 1
	def adjacent(self, index):
		bdist = self.bdist
		wdist = self.wdist

		if index < 4:
			return self.edges[index]

		neighbours = set()
	
		low = 4
		high = len(self.board) - 1

		bottom = bdist - 1 + 4
		top = (wdist - 1) * bdist + 4

		#up left (good)
		n = index - 1
		if ((index - 4) % bdist) - 1 < 0:
			n = 0
		#print("UL " + str(n))
		neighbours.add(n)

		#down right (good)
		n = index + 1
		if ((index - 4) % bdist) + 1 >= bdist:
			n = 2
		#print("DR " + str(n))
		neighbours.add(n)

		#up right (good)
		n = index + bdist
		if (n > high):
			n = 1
		#print("UR " + str(n))
		neighbours.add(n)

		#down left (good)
		n = index - bdist
		if (n < low):
			n = 3
		#print("DL " + str(n))
		neighbours.add(n)

		#up
		edge = False
		if index in self.edges[0]:
			#print("up -- 0")
			edge = True
			neighbours.add(0)
		if index in self.edges[1]:
			#print("up -- 1")
			edge = True
			neighbours.add(1)
		if not edge:
			n = index + bdist - 1
			#print("up -- " + str(n))
			neighbours.add(n)

		#down
		edge = False
		if index in self.edges[2]:
			#print("down -- 2")
			edge = True
			neighbours.add(2)
		if index in self.edges[3]:
			#print("down -- 3")
			edge = True
			neighbours.add(3)
		if not edge:
			n = index - bdist + 1
			#print("down -- " + str(n))
			neighbours.add(n)


		return neighbours

	def randomMove(self, value):
		self.cacheNum = -1
		self.cacheResult = -1
		choices = []
		for i in range(4, len(self.board)):
			if self.board[i] == 0:
				choices.append(i)
		index = random.randint(0, len(choices) - 1)
		self.board[choices[index]] = value

	def testfill(self):
		self.cacheNum = -1
		for i in range(0, len(self.board)):
			self.board[i] = i

	def setHexIndex(self, index, value):
		if index < 0 or index >= len(self.board):
			return False
	
		if self.board[index] == 0:
			self.board[index] = value
			self.cacheNum = -1
			self.cacheResult = -1
			return True
		return False

	#1,1 or a,1
	def setHex2(self, bCoord, wCoord, value):
		index = self.__bwToIndex(bCoord, wCoord, silent = True)
		return self.setHexIndex(index, value)

	def setHex(self, coord, value):
		coord = coord.lower()
		formatSearch = re.search("([a-z])([0-9]+)", coord)
		matchesFormat = formatSearch is not None and formatSearch.span() == (0, len(coord))

		if not matchesFormat:
			return False

		b = re.search("[a-z]", coord).group(0)
		w = re.search("[0-9]+", coord).group(0)

		return self.setHex2(b, w, value)

	def draw(self):
		print(self.board)

		bdist = self.bdist
		wdist = self.wdist
		rows = bdist + wdist - 1

		centerRow = wdist - 1

		maxWidth = min(bdist, wdist)
		top = (wdist - 1) * bdist
		dist = bdist + 1


		startOffset = centerRow - 1 + 2
		print(" " * 2 * startOffset, end="")
		print(self.bchars[-1], end="")
		print("")

		for i in range(rows):
			offset = abs(i - centerRow) + 2
			width = min(i + 1, maxWidth) if i <= centerRow else min(rows - i, maxWidth) 
			base = top - i * bdist if i <= centerRow else i - centerRow
			#print(str(i) + " " + str(offset) + " " + str(width) + " " + str(base))

			row = [base + dist * j for j in range(0, width)]

			label = self.labels[i + 1]

			#print spaces
			offset -= 2
			offset *= 2
			offset += (1 - self.labelLengths[i + 1])

			print(" " * offset, end = "")

			#print label
			print(label, end="    ")

			#print tiles
			for j in range(len(row)):
				tileIndex = row[j] + 4
				tileId = self.board[tileIndex]
				tileChar = playerToColor(tileId)
				print(tileChar, end = "")
				if j < len(row) - 1:
					print(" " * 2, end = "")
			print("")
		
		endOffset = rows - centerRow
		print("  " * endOffset, end = "")
		print(self.labels[-1])
		
'''
	  bdist
	<---->

0   1   2   3   4		^
5   6   7   8   9		|	wdist
10  11  12  13  14		|
15  16  17  18  19		v
20  21  22  23  24

sweep diagonally and add 4 to find board index
'''

'''
example = State(5, 5)
example.setHex("c3", 1)
example.setHex("c2", 2)
example.setHex("c4", 2)
example.setHex("b3", 2)
example.setHex("d3", 2)
example.setHex("d2", 2)
example.setHex("b4", 2)
example.draw()
'''

def adjacencyTest():
	w = 5
	b = 5
	for i in range(0, 4 + w * b):
		os.system("clear")
		print("Hex " + str(i))
		s = State(w, b)
		s.board[i] = 1
		adj = s.adjacent(i)
		print(adj)
		for a in adj:
			s.board[a] = 2
		s.draw()

		colors = [cWhite] * 4
		for j in adj:
			if j >= 0 and j <= 3:
				colors[j] = cRed

		print(colors[0] + "/" + colors[1] + "\\")
		print(colors[3] + "\\" + colors[2] + "/")
		print(cWhite)

		input("[Press enter]")

#adjacencyTest()
#exit(0)


def searchTest():
	w = 5
	b = 5
	while True:
		os.system("clear")
		s = State(w, b)
		s.randomize()
		s.draw()
	
		print("1 win: " + str(s.pathTest(0, 2, 1)))
		print("2 win: " + str(s.pathTest(1, 3, 2)))

		input("[Press enter to generate another board]")
	
#searchTest()
#exit(0)


### Player

def argmax(values):
	bestValue = values[0]
	bestIndices = [0]

	for i in range(1, len(values)):
		v = values[i]

		if v == bestValue:
			bestIndices.append(i)
		if v > bestValue:
			bestValue = v
			bestIndices = [i]

	return bestIndices[random.randint(0, len(bestIndices) - 1)]

def softmax(values):
	e = [math.exp(v) for v in values]
	s = sum(e)
	p = [ev / s for ev in e]

	pi = [(p[i], i) for i in range(len(p))]

	pi.sort(key = lambda x : x[0])

	r = random.random()

	i = 0
	while i < len(pi) - 1:
		if r > pi[i][0]:
			i += 1
		else:
			return pi[i][1]
	return pi[i][1]


def softmin(values):
	e = [math.exp(v) for v in values]
	s = sum(e)
	p = [ev / s for ev in e]

	piNormal = [(p[i], i) for i in range(len(p))]
	piNormal.sort(key = lambda x : x[0])

	l = len(piNormal)
	pi = [(piNormal[i][0], piNormal[l - i - 1][1]) for i in range(l)] 

	r = random.random()

	i = 0
	while i < len(pi) - 1:
		if r > pi[i][0]:
			i += 1
		else:
			return pi[i][1]
	return pi[i][1]




def argmin(values):
	bestValue = values[0]
	bestIndices = [0]

	for i in range(1, len(values)):
		v = values[i]

		if v == bestValue:
			bestIndices.append(i)
		if v < bestValue:
			bestValue = v
			bestIndices = [i]

	return bestIndices[random.randint(0, len(bestIndices) - 1)]




class RandomPlayer():
	def __init__(self, playerNumber):
		self.playerNumber = playerNumber
	
	def makePlay(self, state, timeStep):
		state.randomMove(self.playerNumber)

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
		while s.result() == 0:
			s.randomMove(toPlay)
			toPlay = nextPlayer(toPlay)
		return s.result()


	# action = best action according to
	# val(a) + c * sqrt(ln(t) / vis(a))

class BasicPlayer2:
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
		self.softmax = True


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

		while time.time() < self.endTime:
			self.rollout(state, self.playerNumber)

		moves = [i for i in range(4, len(state.board)) if state.board[i] == 0]

		states = []
		visits = []
		values = []
		heuristic = []
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
				o = s.result()
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

		if state.result() != 0:
			v = 1 if state.result() == self.playerNumber else -1
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
				o = s.result()
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


class HumanPlayer:
	def __init__(self, playerNumber):
		self.playerNumber = playerNumber
		self.rollouts = 0
		self.stateInfo = {}

	def makePlay(self, state, timeStep):
		action = input("Enter player " + str(self.playerNumber) + " action: ")
		while not state.setHex(action, self.playerNumber):
			action = input("Can't place hex there, pick an open hex: ")

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


	def update(self, result):
		self.visits += 1
		
		if self.player == result:
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
			outcome = node.state.result()
			if outcome == 0:
				node.expandChildren()
				#pick a child and do simulation
				node = node.children[random.randint(0, len(node.children) - 1)]
				stack.append(node)

				node.state.result()
				s = node.state.clone()
				p = node.player
				while s.result() == 0:
					s.randomMove(p)
					p = nextPlayer(p)
				outcome = s.result()


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
				



		

			

		



############################################################ The actual game


def nextPlayer(current):
	return 1 if current == 2 else 2




############################################################


a1 = 0.01
a2 = 0.01
gameNo = 1
learn = False

w1 = 0
w2 = 0



p1 = BasicPlayer2(1)
p2 = BasicPlayer(2)


p1 = HumanPlayer(1)
p2 = BasicPlayer2(2)

p1 = BasicPlayer2(1)

perc = 0
percs = []

col1 = ""
col2 = ""

p1 = MCTSPlayer(1)
p1.message = None
p1.rollouts = 0
p1.stateInfo = {}

while True:
	wdist = 4
	bdist = 4

	game = State(wdist, bdist)

	p1 = MCTSPlayer(1)
	p1.message = None
	p1.rollouts = 0
	p1.stateInfo = {}


	#p1.softmax = True
	p2 = RandomPlayer(2)
	#p2.softmax = True
	p2.rollouts = 0
	p2.stateInfo = {}

	limit = 4.0
	p1.timeLimit = limit
	p2.timeLimit = limit
	p1.expConst = a1
	p2.expConst = a2
	p1s = 1
	p2s = 1

	p1.increment = True
	p2.increment = True

	player = random.randint(1, 2)
	#player = 1

	if player == 1:
		col1 = cBlue
		col2 = cRed
	else:
		col1 = cRed
		col2 = cBlue

	os.system("clear")
	game.draw()
	print("Game number " + str(gameNo))
	print("(" + str(a1) + " " + str(a2) + ")")
	print(col1 + "P1" + cWhite + "/" + col2 + "P2" + cWhite + ": " + str(w1) + " " + str(w2))
	print("Rollouts: " + str(p1.rollouts) + " " + str(p2.rollouts))
	print("Entries: " + str(len(p1.stateInfo.keys())) + " " + str(len(p2.stateInfo.keys())))
	perc = -1 if len(p1.stateInfo.keys()) == 0 else len([1 for k in p1.stateInfo.keys() if p1.stateInfo[k][1] == 0]) / len(p1.stateInfo.keys())
	print("% of 0s: " + str(perc))
	print("Message: ", end="")
	print(p1.message)

	while game.result() == 0:
		if player == 1:
			#input("[Press enter]")
			p1.makePlay(game, p1s)
			p1s += 1
		if player == 2:
			p2.makePlay(game, p2s)
			p2s += 1

		player = nextPlayer(player)

		os.system("clear")
		game.draw()
		print("Game number " + str(gameNo))
		print("(" + str(a1) + " " + str(a2) + ")")
		print(col1 + "P1" + cWhite + "/" + col2 + "P2" + cWhite + ": " + str(w1) + " " + str(w2))
		print("Rollouts: " + str(p1.rollouts) + " " + str(p2.rollouts))
		print("Entries: " + str(len(p1.stateInfo.keys())) + " " + str(len(p2.stateInfo.keys())))
		perc = -1 if len(p1.stateInfo.keys()) == 0 else len([1 for k in p1.stateInfo.keys() if p1.stateInfo[k][1] == 0]) / len(p1.stateInfo.keys())
		print("% of 0s: " + str(perc))
		print("Message: ", end="")
		print(p1.message)


	res = game.result()
	if res == 1:
		w1 += 1
	else:
		w2 += 1

	if learn:
		if res == 1:
			a2 = a2 + 0.03 * (a1 - a2)
		else:
			a1 = a1 + 0.03 * (a2 - a1)

	gameNo += 1

	perc = -1 if len(p1.stateInfo.keys()) == 0 else len([1 for k in p1.stateInfo.keys() if p1.stateInfo[k][1] == 0]) / len(p1.stateInfo.keys())
	percs.append(perc)

	if gameNo == 100 + 1:
		#p1.save("p1.dat")
		print("P1/P2: " + str(w1) + " " + str(w2))
		print(sum(percs) / len(percs))
		exit(0)

	#if gameNo == 20:
	#	p1.save("p1.dat")
	#	exit(0)




############################################################



opponent = BasicPlayer2(1)
opponent.expConst = 0.01


previous = (0, 0)

while True:
	os.system("clear")

	wdist = int(input("Enter distance for white (integer): "))
	bdist = int(input("Enter distance for black (integer): "))

	if (wdist, bdist) != previous:
		opponent = BasicPlayer(1)
		opponent.expConst = 0.01

	previous = (wdist, bdist)

	game = State(wdist, bdist)
	#opponent = BasicPlayer2(2)
	opponent.timeLimit = 4.0
	opponentStep = 1

	player = 1


	os.system("clear")
	game.draw()
	print("\nPrevious rollouts: " + str(opponent.rollouts))
	print("Entries: " + str(len(opponent.stateInfo.keys())))

	while game.result() == 0:
		if player == 2:
			action = input("Enter player 1 action: ")
			while not game.setHex(action, 1):
				action = input("Can't place hex there, pick an open hex: ")
	#	elif player == 2:
	#		action = input("Enter player 2 action: ")
	#		while not game.setHex(action, 2):
	#			action = input("Can't place hex there, pick an open hex: ")

		if player == 1:
			opponent.makePlay(game, opponentStep)
			opponentStep += 1

		player = nextPlayer(player)

		os.system("clear")
		game.draw()
		print("\nPrevious rollouts: " + str(opponent.rollouts))
		print("Entries: " + str(len(opponent.stateInfo.keys())))
	
	print("Player " + str(game.result()) + " wins!")
	input("[Press enter to play again]")
