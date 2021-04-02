import os
from state import State
from utils import colors


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

