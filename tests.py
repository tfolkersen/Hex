"""		tests

	Defines some tests of various functionality.
"""

import os
from state import State
from utils import colors

"""		nonAdjacentTest

	Makes a 7x7 board and colors a cell with player 1 color,
		marks nearby non adjacent cells with player 2 color,
		then draws the board.
"""
def nonAdjacentTest():
	w = 7
	b = 7
	s = State(w, b)
	
	s.setHex("d4", 1)
	s.setHex("c3", 2)
	s.setHex("b5", 2)
	s.setHex("c6", 2)
	s.setHex("e5", 2)
	s.setHex("e2", 2)
	s.setHex("f3", 2)

	s.draw()

"""		adjacencyTest

	Makes a 5x5 board and on every iteration, shows a hex and highlights its adjacent
		hexes. Shows edges too.
"""
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

		cs = [colors["white"]] * 4
		for j in adj:
			if j >= 0 and j <= 3:
				cs[j] = colors["red"]

		print(cs[0] + "/" + cs[1] + "\\")
		print(cs[3] + "\\" + cs[2] + "/")
		print(colors["white"])

		input("[Press enter]")

"""		searchTest

	Generates a random 5x5 board and shows for each player whether or not
		they have won.
"""
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


