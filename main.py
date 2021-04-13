"""		main

	Main program.
"""


import random
import os

from state import State
from utils import *

from humanplayer import HumanPlayer
from randomplayer import RandomPlayer

def clear():
	if os.name == "nt":
		os.system("cls")
	else:
		os.system("clear")

def draw():
	clear()
	game.draw()
	print("Game " + str(gameNumber) + " -- " + colors["p1"] + players[0].__class__.__name__ + colors["white"]\
		+ " vs " + colors["p2"] + players[1].__class__.__name__ + colors["white"])
	print("Wins: " + colors["p1"] + str(wins[0]) + colors["white"] +  "/" + colors["p2"] + str(wins[1]) + colors["white"])

#Parameters
wdist = 5
bdist = 5
maxGames = 20

player1Class = RandomPlayer
player2Class = RandomPlayer

#Initialization
wins = [0, 0]
gameNumber = 1

while gameNumber <= maxGames:
	players = [player1Class(1), player2Class(2)]
	
	game = State(wdist, bdist)
	toPlay = random.randint(1, 2)

	while game.outcome() == 0:
		clear()
		draw()

		player = players[toPlay - 1]
		move = player.getPlay(game.clone())

		if not game.setHexIndex(move, toPlay):
			print("Couldn't make move (player " + str(toPlay) + " move " + str(move))
			raise

		toPlay = nextPlayer(toPlay)

	wins[game.outcome() - 1] += 1

	clear()
	draw()

	gameNumber += 1
