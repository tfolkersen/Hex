import random
import re
import time
import os
import copy
import math
import json

from state import *
from utils import *


print(colors["white"], end="")





from randomplayer import RandomPlayer

while True:
	p1 = RandomPlayer(1)
	p2 = RandomPlayer(2)

	game = State(5, 5)

	player = 1
	time = 1


	os.system("clear")
	game.draw()
	print("Turn: " + str(player))
	input("[Press enter]")
	player = nextPlayer(player)


	while game.outcome() == 0:
		if player == 1:
			p1.makePlay(game, time)
		elif player == 2:
			p2.makePlay(game, time)

		os.system("clear")
		game.draw()
		print("Turn: " + str(player))
		input("[Press enter]")
		player = nextPlayer(player)

	exit(0)
		
		


