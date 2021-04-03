from utils import *
import random
import copy
import re

stateHelper = {}

def numberAfterMove(stateNumber, tiles, index, value):
	num = stateNumber
	num += 1 << ((index - 4) + (value - 1) * tiles) if value != 0 else 0
	return num

class State:

	def __init__(self):
		pass

	def __init__(self, wdist = 5, bdist = 5):
		self.board = [1, 2, 1, 2] + [0] * (bdist * wdist)
		self.bdist = bdist
		self.wdist = wdist
		self.dims = (wdist, bdist)

		if not self.dims in stateHelper.keys():
			stateHelper[self.dims] = {}

			h = stateHelper[self.dims]

			top = [4 + 0 + bdist * i for i in range(wdist)]
			bottom = [4 + bdist - 1 + bdist * i for i in range(wdist)]
			left = [4 + i for i in range(bdist)]
			right = [4 + (wdist - 1) * bdist + i for i in range(bdist)]

			edges = [top, right, bottom, left]	


			bchars = [colors["blue"] + alphabet[i] + colors["white"] for i in range(0, wdist)]
			wchars = [colors["red"] + str(i) + colors["white"] for i in range(1, bdist + 1)]
			labels = bchars[::-1] + [" "] + wchars

			labelLengths = [len(alphabet[i]) for i in range(0, wdist)][::-1] + [1] +\
				[len(str(i)) for i in range(1, bdist + 1)]


			h["top"] = top
			h["bottom"] = bottom
			h["left"] = left
			h["right"] = right
			h["edges"] = edges

			h["bchars"] = bchars
			h["wchars"] = wchars
			h["labels"] = labels
			h["labelLengths"] = labelLengths

			self._initAdjacencySets()

		self.cacheNum = 0
		self.cacheOutcome = 0
		self.moveList = -1

	def clone(self):
		#return copy.deepcopy(self)
		#return copy.copy(self)

		s = State()

		s.board = list(self.board)
		s.bdist = self.bdist
		s.wdist = self.wdist
		s.dims = self.dims

		s.cacheNum = self.cacheNum
		s.cacheOutcome = self.cacheOutcome
		s.moveList = -1 if self.moveList == -1 else list(self.moveList)
		return s



	def _invalidateCache(self):
		#self.cacheNum = -1
		self.cacheOutcome = -1
		self.moveList = -1

	def moves(self):
		if self.moveList == -1:
			self.moveList = tuple([i for i in range(4, len(self.board)) if self.board[i] == 0])
		return self.moveList

	#start and end are board indices
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

	def outcome(self):
		if self.cacheOutcome == -1:
			self.cacheOutcome = 0
			if self.pathTest(0, 2, 1): #Path for black (from 0 to 2)
				self.cacheOutcome = 1
			elif self.pathTest(1, 3, 2): #Path for white (from 1 to 3)
				self.cacheOutcome = 2
		return self.cacheOutcome

	def number(self):
		if self.cacheNum == -1:
			num = 0
			tiles = self.wdist * self.bdist
			for i in range(4, len(self.board)):
				v = self.board[i]
				num += 1 << ((i - 4) + (v - 1) * tiles) if v != 0 else 0
			self.cacheNum = num

		return self.cacheNum


	#silent is ignored
	def _bwToIndex(self, bCoord, wCoord, silent = False):
		wdist = self.wdist
		bdist = self.bdist

		if type(bCoord) is str and bCoord.isalpha():
			bCoord = ord(bCoord.lower()) - ord("a")
		else:
			bCoord -= 1

		wCoord = int(wCoord)
		wCoord -= 1

		if not silent or True:
			if (bCoord < 0 or bCoord >= wdist) or (wCoord < 0 or wCoord >= bdist):
				raise "Bad bwToIndex coordinates: (" + str(bCoord) + ", " + str(wCoord) + ")"

		index = bCoord * bdist + wCoord + 4
		return index


	def randomize(self):
		self._invalidateCache()
		for i in range(4, len(self.board)):
			self.board[i] = random.randint(0, 2)



	#given a board index, return adjacent board indices
	#	b + 1 ---> index + bdist
	#	w + 1 ---> index + 1
	def _computeAdjacentSet(self, index):
		bdist = self.bdist
		wdist = self.wdist

		edges = stateHelper[self.dims]["edges"]

		if index < 4:
			return edges[index]

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
		if index in edges[0]:
			#print("up -- 0")
			edge = True
			neighbours.add(0)
		if index in edges[1]:
			#print("up -- 1")
			edge = True
			neighbours.add(1)
		if not edge:
			n = index + bdist - 1
			#print("up -- " + str(n))
			neighbours.add(n)

		#down
		edge = False
		if index in edges[2]:
			#print("down -- 2")
			edge = True
			neighbours.add(2)
		if index in edges[3]:
			#print("down -- 3")
			edge = True
			neighbours.add(3)
		if not edge:
			n = index - bdist + 1
			#print("down -- " + str(n))
			neighbours.add(n)


		return neighbours

	def _initAdjacencySets(self):
		h = stateHelper[self.dims]
		h["adjacency"] = []
		adj = h["adjacency"]

		for i in range(0, len(self.board)):
			s = self._computeAdjacentSet(i)
			adj.append(s)

	def adjacent(self, index):
		if index < 0 or index >= len(self.board):
			raise "Bad index in State.adjacent"
		return stateHelper[self.dims]["adjacency"][index]

			

	def randomMove(self, value):
		self._invalidateCache()

		choices = []
		for i in range(4, len(self.board)):
			if self.board[i] == 0:
				choices.append(i)
		index = random.randint(0, len(choices) - 1)
		self.setHexIndex(choices[index], value)
		#self.board[choices[index]] = value

	def testfill(self):
		self._invalidateCache()
		for i in range(0, len(self.board)):
			self.board[i] = i

	def setHexIndex(self, index, value):
		if index < 0 or index >= len(self.board):
			return False
	
		if self.board[index] == 0:
			self._invalidateCache()
			self.board[index] = value
			self.cacheNum = numberAfterMove(self.cacheNum, self.bdist * self.wdist, index, value)
			return True
		return False


	#1,1 or a,1
	def setHex2(self, bCoord, wCoord, value):
		index = self._bwToIndex(bCoord, wCoord, silent = True)
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

		helper = stateHelper[self.dims]
		bchars = helper["bchars"]
		labels = helper["labels"]
		labelLengths = helper["labelLengths"]

		bdist = self.bdist
		wdist = self.wdist
		rows = bdist + wdist - 1

		centerRow = wdist - 1

		maxWidth = min(bdist, wdist)
		top = (wdist - 1) * bdist
		dist = bdist + 1


		startOffset = centerRow - 1 + 2
		print(" " * 2 * startOffset, end="")
		print(bchars[-1], end="")
		print("")

		for i in range(rows):
			offset = abs(i - centerRow) + 2
			width = min(i + 1, maxWidth) if i <= centerRow else min(rows - i, maxWidth) 
			base = top - i * bdist if i <= centerRow else i - centerRow
			#print(str(i) + " " + str(offset) + " " + str(width) + " " + str(base))

			row = [base + dist * j for j in range(0, width)]

			label = labels[i + 1]

			#print spaces
			offset -= 2
			offset *= 2
			offset += (1 - labelLengths[i + 1])

			print(" " * offset, end = "")

			#print label
			print(label, end="    ")

			#print tiles
			for j in range(len(row)):
				tileIndex = row[j] + 4
				tileId = self.board[tileIndex]
				tileChar = playerToSymbol(tileId) + " "
				print(tileChar, end = "")
				if j < len(row) - 1:
					print(" " * 2, end = "")
			print("")
		
		endOffset = rows - centerRow
		print("  " * endOffset, end = "")
		print(labels[-1])


		
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


