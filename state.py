"""		state

	Defines State class representing a position in the game of Hex.
"""

from utils import *
import random
import copy
import re

#Dictionary caching information shared between states of common dimensions
stateHelper = {}

"""		numberAfterMove

	stateNumber -- integer representing State
	tiles -- bdist * wdist (how many cells are in the board)
	move -- integer index of move in State's board array
	player -- integer of player making the move (1 or 2)

	Given a State's number and a move, returns updated State number.
"""
def numberAfterMove(stateNumber, tiles, move, player):
	num = stateNumber
	num += 1 << ((move - 4) + (player - 1) * tiles) if player != 0 else 0
	if player == 0: #setting hex to 0 requires unsetting some bits
		mask = 1 << ((move - 4) + (1 - 1) * tiles) #player 1
		mask |= 1 << ((move - 4) + (2 - 1) * tiles) #player 2
		extracted = num & mask
		num -= extracted
	return num

"""		State

	Represents a position in the game of Hex.
"""
class State:
	"""		(empty constructor)

		This shouldn't be used in most cases. This is used by the clone function for computational efficiency.
	"""
	def __init__(self):
		pass

	"""		(intended constructor)

		wdist -- integer distance (in cells) between white's sides (default 5)
		bdist -- integer distance (in cells) between black's sides (default 5)
	"""
	def __init__(self, wdist = 5, bdist = 5):
		#array of player pieces -- 1 for black and 2 for white
		#indices 0, 1, 2, and 3 are top, right, bottom, and left edges respectively
		#these edges are treated like any other cell so that some computations are simpler
		self.board = [1, 2, 1, 2] + [0] * (bdist * wdist)

		self.bdist = bdist
		self.wdist = wdist
		self.dims = (wdist, bdist)

		#Generate info shared between states of these dimensions if this info isn't already stored
		if not self.dims in stateHelper.keys():
			stateHelper[self.dims] = {}

			h = stateHelper[self.dims]

			top = [4 + 0 + bdist * i for i in range(wdist)] #indices of cells along top edge (upper left of screen -- upper black edge)
			bottom = [4 + bdist - 1 + bdist * i for i in range(wdist)] #indices of cells along bottom edge (lower right of screen -- lower black edge)
			left = [4 + i for i in range(bdist)] #indices of cells along left edge (lower left of screen -- left white edge)
			right = [4 + (wdist - 1) * bdist + i for i in range(bdist)] #indices of cells along right edge (upper right of screen -- right white edge)

			edges = [top, right, bottom, left]	

			#black edge's cell labels
			bchars = [colors["p1"] + alphaLabel(i + 1) + colors["white"] for i in range(0, wdist)]

			#white edge's cell labels
			wchars = [colors["p2"] + str(i) + colors["white"] for i in range(1, bdist + 1)]

			#Labels ordered according to their use in rendering -- one line has no label so there's an empty label there
			labels = bchars[::-1] + [" "] + wchars

			#Lengths of labels (as shown on display, not lengths of strings as these have color characters in them that take up 0 space)
			labelLengths = [len(alphaLabel(i + 1)) for i in range(0, wdist)][::-1] + [1] +\
				[len(str(i)) for i in range(1, bdist + 1)]


			#Save info in dictionary
			h["top"] = top
			h["bottom"] = bottom
			h["left"] = left
			h["right"] = right
			h["edges"] = edges

			h["bchars"] = bchars
			h["wchars"] = wchars
			h["labels"] = labels
			h["labelLengths"] = labelLengths


			#Initialize other more complex information
			self._initDirAdj()
			self._initAdjacencySets()

		self.cacheNum = 0 #cached integer representing this State
		self.cacheOutcome = 0 #cached winner of this State (0 for no winner yet, otherwise 1 for player 1 win, 2 for player 2 win)
		self.moveList = -1 #list of valid moves from this State, or -1 if not cached

	"""		clone

		Returns a copy of this State. No longer uses copy.deepcopy as this was slow.
			This function needs to be maintained as new data is added to State.
	"""
	def clone(self):
		s = State()

		s.board = list(self.board)
		s.bdist = self.bdist
		s.wdist = self.wdist
		s.dims = self.dims

		s.cacheNum = self.cacheNum
		s.cacheOutcome = self.cacheOutcome
		s.moveList = -1 if self.moveList == -1 else list(self.moveList)
		return s

	"""		_invalidateCache

		Invalidates cached values (i.e. move list, number, etc.). Call this from internal functions
			that modify the State (like placing new pieces on the board).

		NOTE: self.cacheNum isn't invalidated because it must be updated incrementally, otherwise performance suffers.
	"""
	def _invalidateCache(self):
		self.cacheOutcome = -1
		self.moveList = -1

	"""		moves

		Returns a tuple of board array indices representing valid moves (empty cells). Caches moves.
	"""
	def moves(self):
		if self.moveList == -1:
			self.moveList = tuple([i for i in range(4, len(self.board)) if self.board[i] == 0])
		return self.moveList

	"""		pathTest

		start -- integer board index of start cell (could be an edge cell too)
		end -- integer board index of end cell (could be an edge cell too)
		player -- integer id of player whose pieces are to be followed on the path (1 or 2)

		Returns True if a path exists between the start and end cell indices following the given player's pieces.
			If either the start or end cells belong to another player, this returns False.
	"""
	def pathTest(self, start, end, player):
		board = self.board

		if board[start] != player or board[end] != player:
			return False

		todo = [start] #List of open cells
		closed = [False] * len(board) #Keep track of previously-visited cells

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
		#No path found
		return False

	"""		outcome

		Returns outcome of this State. 0 if no player has won, or 1 if player 1 has won, or 2 if player 2 has won.
			Caches outcome.
	"""
	def outcome(self):
		if self.cacheOutcome == -1:
			self.cacheOutcome = 0
			if self.pathTest(0, 2, 1): #Path for black (from 0 to 2)
				self.cacheOutcome = 1
			elif self.pathTest(1, 3, 2): #Path for white (from 1 to 3)
				self.cacheOutcome = 2
		return self.cacheOutcome

	"""		number

		Returns an integer uniquely identifying this State's board.
			This can be used for transposition tables. Caches number.
	"""
	def number(self):
		if self.cacheNum == -1:
			num = 0
			tiles = self.wdist * self.bdist
			for i in range(4, len(self.board)):
				v = self.board[i]
				num += 1 << ((i - 4) + (v - 1) * tiles) if v != 0 else 0
			self.cacheNum = num

		return self.cacheNum

	"""		_bwToIndex

		bCoord -- Coordinate along black axis (integer starting at 1, or letter starting at "a")
		wCoord -- Coordinate along white axis (integer starting at 1, or string of integer starting at 1)

		Returns board index corresponding to board coordinates (i.e. a1, b4, etc.).
	"""
	def _bwToIndex(self, bCoord, wCoord):
		wdist = self.wdist
		bdist = self.bdist

		if type(bCoord) is str and bCoord.isalpha():
			bCoord = ord(bCoord.lower()) - ord("a")
		else:
			bCoord -= 1

		wCoord = int(wCoord)
		wCoord -= 1

		if (bCoord < 0 or bCoord >= wdist) or (wCoord < 0 or wCoord >= bdist):
			print("Bad _bwToIndex coordinates: (" + str(bCoord) + ", " + str(wCoord) + ")")
			raise

		index = bCoord * bdist + wCoord + 4
		return index

	"""		randomize

		Generates a random board
	"""
	def randomize(self):
		self._invalidateCache()
		for i in range(4, len(self.board)):
			self.board[i] = random.randint(0, 2)

	"""		_computeAdjacentSet

		index -- integer board index

		Given board cell index, returns the set of all adjacent board indices. This function doesn't
			cache the sets, so this function will affect performance if used frequently. Use adjacent() instead.
	"""
	def _computeAdjacentSet(self, index):
		#	b + 1 ---> index + bdist
		#	w + 1 ---> index + 1

		bdist = self.bdist
		wdist = self.wdist

		edges = stateHelper[self.dims]["edges"]

		if index < 4:
			return edges[index] #TODO this returns a list and not a set...

		neighbours = set()
	
		low = 4 #minimal index that isn't a border
		high = len(self.board) - 1 #maximal index

		bottom = bdist - 1 + 4 #index of non-border cell at the bottom of the screen
		top = (wdist - 1) * bdist + 4 #index of non-border cell at the top of the screen

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

	"""		dirAdj		"directionally adjacent cell"

		index -- integer index of board cell (not border)
		direction -- direction to go in (string)

		directions are:
			"u" -- up
			"ul" -- up left
			"ur" -- up right
			"d" -- down
			"dl" -- down left
			"dr" -- down right

		Given a board index and a direction, returns the index of the board cell in that
			direction, or -1 if no such cell exists. Uses cached data. A border cell used as an index
			will return -1, and if a border cell is in the given direction, -1 is returned.
	"""
	def dirAdj(self, index, direction):
		return stateHelper[self.dims]["dir"][index][direction]

	"""		_initDirAdj

		Computes and caches the data for self.dirAdj(). 
	"""
	def _initDirAdj(self):
		h = stateHelper[self.dims]
		edges = h["edges"]

		h["dir"] = {}

		#initialize all neighbours to -1
		for i in range(len(self.board)):
			h["dir"][i] = {}
			d = h["dir"][i]
			d["u"] = -1
			d["ul"] = -1
			d["ur"] = -1
			d["d"] = -1
			d["dl"] = -1
			d["dr"] = -1

		bdist = self.bdist
		wdist = self.wdist

		low = 4 #index of minimal non-border cell
		high = len(self.board) - 1 #index of maximal cell

		bottom = bdist - 1 + 4 #index of non-border cell at the bottom of the screen
		top = (wdist - 1) * bdist + 4 #index of non-border cell at the top of the screen

		for index in range(4, len(self.board)):
			d = h["dir"][index]

			#up left
			n = index - 1
			if ((index - 4) % bdist) - 1 < 0:
				n = -1
			d["ul"] = n
			

			#down right
			n = index + 1
			if ((index - 4) % bdist) + 1 >= bdist:
				n = -1
			d["dr"] = n

			#up right
			n = index + bdist
			if (n > high):
				n = -1
			d["ur"] = n

			#down left
			n = index - bdist
			if (n < low):
				n = -1
			d["dl"] = n

			#up
			edge = False
			if index in edges[0]:
				edge = True
			if index in edges[1]:
				edge = True
			if not edge:
				n = index + bdist - 1
				d["u"] = n

			#down
			edge = False
			if index in edges[2]:
				edge = True
			if index in edges[3]:
				edge = True
			if not edge:
				n = index - bdist + 1
				d["d"] = n

	"""		_initAdjacencySets

		Computes the adjacency sets for all board cells and caches them.
	"""
	def _initAdjacencySets(self):
		h = stateHelper[self.dims]
		h["adjacency"] = []
		adj = h["adjacency"]

		for i in range(0, len(self.board)):
			s = self._computeAdjacentSet(i)
			adj.append(s)

	"""		adjacent

		index -- integer index of board cell

		Returns the set of indices of board cells adjacent to the given cell index.
	"""
	def adjacent(self, index):
		if index < 0 or index >= len(self.board):
			print("Bad index in State.adjacent: " + str(index))
			raise
		return stateHelper[self.dims]["adjacency"][index]
			
	"""		randomMove

		player -- integer of player whose color to use (1 for black, 2 for white)

		Randomly place a piece for the specified player
	"""
	def randomMove(self, player):
		self._invalidateCache()

		choices = []
		for i in range(4, len(self.board)):
			if self.board[i] == 0:
				choices.append(i)
		index = random.randint(0, len(choices) - 1)
		self.setHexIndex(choices[index], player)

	"""		testFill

		Fills the board with values 0, 1, 2, ...
	"""
	def testfill(self):
		self._invalidateCache()
		self.cacheNum = -1
		for i in range(0, len(self.board)):
			self.board[i] = i

	"""		setHexIndex

		index -- board index of cell to place hex at
		player -- integer of player for whom this hex is being placed
		force -- default False. If True will overwrite existing hex, otherwise will not overwrite

		Places a hex for the specified player at the specified board location. If force = True, this will overwrite any previously
			placed hex, otherwise this will not overwrite a previously placed hex. Returns True if succeeded, otherwise returns False.
	"""
	def setHexIndex(self, index, player, force = False):
		if index < 0 or index >= len(self.board):
			return False
	
		if self.board[index] == 0 or force:
			self._invalidateCache()
			self.board[index] = player
			self.cacheNum = numberAfterMove(self.cacheNum, self.bdist * self.wdist, index, player)
			return True
		return False

	"""		setHex2

		bCoord -- coordinate along black axis (integer starting at 1, or letter starting at "a")
		wCoord -- coordinate along white axis (integer starting at 1)
		player -- integer of player for whom this hex is being placed
		force -- default False. If True will overwrite existing hex, otherwise will not overwrite

		Places a hex for the specified player at the specified board location. If force = True, this will overwrite any previously
			placed hex, otherwise this will not overwrite a previously placed hex. Returns True if succeeded, otherwise returns False.
	"""
	def setHex2(self, bCoord, wCoord, player, force = False):
		index = self._bwToIndex(bCoord, wCoord)
		return self.setHexIndex(index, player, force)

	"""		coordToIndex

		coord -- string of board coordinates (i.e. "a5, "b6", etc.)

		Given board coordinates, returns index of corresponding board cell.
	"""
	def coordToIndex(self, coord):
		coord = coord.lower()
		formatSearch = re.search("([a-z])([0-9]+)", coord)
		matchesFormat = formatSearch is not None and formatSearch.span() == (0, len(coord))

		if not matchesFormat:
			#return False
			print("Badly formatted coordinate in State.coordToIndex: " + str(coord))
			raise

		b = re.search("[a-z]", coord).group(0)
		w = re.search("[0-9]+", coord).group(0)

		return self._bwToIndex(b, w)

	"""		setHex

		coord -- string board coordinates (i.e. "a4", "b6", etc.)
		player -- integer of player for whom to place this piece
		force -- default False. If True will overwrite existing hex, otherwise won't overwrite

		Places a hex for the specified player at the specified board location. If force = True, this will overwrite any previously
			placed hex, otherwise this will not overwrite a previously placed hex. Returns True if succeeded, otherwise returns False.
	"""
	def setHex(self, coord, player, force = False):
		index = self.coordToIndex(coord)
		return self.setHexIndex(index, player, force)

	"""		draw

		Draws the board on the screen.
			(This function is poorly documented and hard to read.)
	"""
	def draw(self):
		#print(self.board)

		helper = stateHelper[self.dims]
		bchars = helper["bchars"]
		labels = helper["labels"]
		labelLengths = helper["labelLengths"]

		bdist = self.bdist
		wdist = self.wdist
		rows = bdist + wdist - 1 #rows to print

		centerRow = wdist - 1 #row corresponding to left corner

		maxWidth = min(bdist, wdist)
		top = (wdist - 1) * bdist #index of hex at top of screen
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


