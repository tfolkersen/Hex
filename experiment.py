"""		main

	Main program.
"""


import random
import os

from state import State
from utils import *

from humanplayer import HumanPlayer
from randomplayer import RandomPlayer
from basicplayer2 import BasicPlayer2
from fasterplayer2 import FasterPlayer2
from fasterplayer3 import FasterPlayer3
from mtplayer import MTPlayer

def clear():
	if os.name == "nt":
		os.system("cls")
	else:
		os.system("clear")

def draw():
	clear()
	game.draw()
	p1Name = players[0].playerName if hasattr(players[0], "playerName") else players[0].__class__.__name__
	p2Name = players[1].playerName if hasattr(players[1], "playerName") else players[1].__class__.__name__

	print("Game " + str(gameNumber) + " -- " + colors["p1"] + p1Name + colors["white"]\
		+ " vs " + colors["p2"] + p2Name + colors["white"])
	print("Wins: " + colors["p1"] + str(wins[0]) + colors["white"] +  "/" + colors["p2"] + str(wins[1]) + colors["white"])
	print("Rollouts: " + colors["p1"] + str(players[0].rollouts) + colors["white"] + "/" + colors["p2"] + str(players[1].rollouts) + colors["white"])

	print("P1 message: " + str(players[0].message))
	print("P2 message: " + str(players[1].message))


def makeRandomPlayer(playerNumber):
	p = RandomPlayer(playerNumber)
	p.rollouts = 0
	p.message = ""
	return p

def makeHumanPlayer(playerNumber):
	p = HumanPlayer(playerNumber)
	p.rollouts = 0
	p.message = ""
	return p

def makeBasicPlayer2(playerNumber):
	p = BasicPlayer2(playerNumber)
	p.timeLimit = timeLimit
	p.message = ""
	return p

def makeFasterPlayer2(playerNumber):
	p = FasterPlayer2(playerNumber)
	p.timeLimit = timeLimit
	p.maximizeNonVisited = True
	return p

def makeFasterPlayer3(playerNumber):
	p = FasterPlayer3(playerNumber)
	p.timeLimit = timeLimit
	p.maximizeNonVisited = True
	return p

def makeMTPlayer2(playerNumber):
	if playerNumber == 1:
		threads = p1Threads
	elif playerNumber == 2:
		threads = p2Threads
	else:
		print("Bad playerNumber in makeMTPlayer2: " + str(playerNumber))
		raise
	p = MTPlayer(playerNumber, threads, useAltPlayer = True)
	p.timeLimit = timeLimit
	p.maximizeNonVisited = True
	p.configurePlayers()
	return p

def makeMTPlayer3(playerNumber):
	if playerNumber == 1:
		threads = p1Threads
	elif playerNumber == 2:
		threads = p2Threads
	else:
		print("Bad playerNumber in makeMTPlayer2: " + str(playerNumber))
		raise
	p = MTPlayer(playerNumber, threads, useAltPlayer = False)
	p.timeLimit = timeLimit
	p.maximizeNonVisited = True
	p.configurePlayers()
	return p


experiments = [[makeBasicPlayer2, makeRandomPlayer], [makeFasterPlayer2, makeBasicPlayer2], [makeFasterPlayer3, makeFasterPlayer2], [makeMTPlayer3, makeFasterPlayer3]]
experiments = [[makeFasterPlayer3, makeBasicPlayer2]]

#Parameters
wdist = 6
bdist = 6
maxGames = 100
timeLimit = 1.0
p1Threads = 4
p2Threads = 4

outFile = open("data.txt", "w")
outFile.close()



for e in experiments:
	player1Factory = e[0]
	player2Factory = e[1]


	#Initialization
	wins = [0, 0]
	gameNumber = 1

	while gameNumber <= maxGames:
		players = [player1Factory(1), player2Factory(2)]
		
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

	p1Name = players[0].playerName if hasattr(players[0], "playerName") else players[0].__class__.__name__
	p2Name = players[1].playerName if hasattr(players[1], "playerName") else players[1].__class__.__name__

	outFile = open("data.txt", "a")
	outFile.write(p1Name + " vs " + p2Name + ": " + str(wins[0]) + "/" + str(wins[1]) + "\n")
	outFile.close()
