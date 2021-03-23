import random
import re
import time
import os

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
		return cWhite + "⬣ "
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

		self.cacheNum = 0
		self.cacheResult = 0

		self.top = [4 + 0 + bdist * i for i in range(wdist)]
		self.bottom = [4 + bdist - 1 + bdist * i for i in range(wdist)]
		self.left = [4 + i for i in range(bdist)]
		self.right = [4 + (wdist - 1) * bdist + i for i in range(bdist)]

		self.edges = [self.top, self.right, self.bottom, self.left]	

	def result(self):
		return 0
		if self.cacheResult == -1:
			#Path for black (from 0 to 2)
			#Path for white (from 1 to 3)
			pass

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

	def __bwToIndex(self, bCoord, wCoord):
		wdist = self.wdist
		bdist = self.bdist

		if type(bCoord) is str and bCoord.isalpha():
			bCoord = ord(bCoord.lower()) - ord("a")
		else:
			bCoord -= 1

		wCoord = int(wCoord)
		wCoord -= 1

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

	#1,1 or a,1
	def setHex2(self, bCoord, wCoord, value):
		self.cacheNum = -1

		index = self.__bwToIndex(bCoord, wCoord)

		if self.board[index] == 0:
			self.board[index] = value
			return True
		return False

	#a1
	def setHex(self, coord, value):
		self.cacheNum = -1
		b = re.search("[a-zA-Z]+", coord).group(0)
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

			#print spaces
			offset -= 2
			print("  " * offset, end = "")

			#print label
			print(self.labels[i + 1], end="    ")

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

w = 5
b = 5
def adjacencyTest():
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

		d = input("[Press enter]")

#adjacencyTest()
#exit(0)

############################################################ The actual game

game = State(5, 5)

player = 1
def nextPlayer(current):
	return 1 if current == 2 else 2

while game.result() == 0:
	os.system("clear")
	game.draw()
	
	if player == 1:
		action = input("Enter player 1 action: ")
		while not game.setHex(action, 1):
			action = input("Can't place hex there, pick an open hex: ")
#	elif player == 2:
#		action = input("Enter player 2 action: ")
#		while not game.setHex(action, 2):
#			action = input("Can't place hex there, pick an open hex: ")

	if player == 2:
		game.randomMove(2)
	player = nextPlayer(player)

