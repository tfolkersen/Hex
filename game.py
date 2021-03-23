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

	def randomize(self):
		for i in range(4, len(self.board)):
			self.board[i] = random.randint(0, 2)

	def testfill(self):
		for i in range(0, len(self.board)):
			self.board[i] = i

	#1,1 or a,1
	def setHex2(self, bCoord, wCoord, value):
		wdist = self.wdist
		bdist = self.bdist

		if bCoord is str and bCoord.isalpha():
			bCoord = ord(bCoord.lower()) - ord("a")
		else:
			bCoord -= 1

		wCoord = int(wCoord)
		wCoord -= 1

		if (bCoord < 0 or bCoord >= wdist) or (wCoord < 0 or wCoord >= bdist):
			print("lol")
			raise "Bad setHex2 coordinates: (" + str(bCoord) + ", " + str(wCoord) + ")"

		index = bCoord * bdist + wCoord + 4
		self.board[index] = value

	#a1
	def setHex(self, coord, value):
		b = re.search("[a-zA-Z]+", coord).group(0)
		w = re.search("[0-9]+", coord).group(0)
		self.setHex2(b, w, value)


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


