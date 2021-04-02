			

import random
import cProfile
import os

from state import State
from basicplayer import BasicPlayer
from basicplayer2 import BasicPlayer2
from mctsplayer import MCTSPlayer
from humanplayer import HumanPlayer
from randomplayer import RandomPlayer
from fastplayer import FastPlayer
from slowplayer import SlowPlayer


from utils import *

cRed = colors["red"]
cBlue = colors["blue"]
cWhite = colors["white"]



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
	wdist = 6
	bdist = 6

	game = State(wdist, bdist)

	p1 = FastPlayer(1)
	p1.message = None
	p1.rollouts = 0
	p1.stateInfo = {}


	#p1.softmax = True
	p2 = SlowPlayer(2)
	#p2.softmax = True
	p2.rollouts = 0
	p2.stateInfo = {}

	p1.bootstrap = False
	p2.bootstrap = False
	p1.expConst = 0.01
	p2.expConst = 0.01
	p1.maximizeNonVisited = True
	p2.maximizeNonVisited = True

	#p2 = HumanPlayer(2)

	limit = 4.0
	gameCount = 500
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

	while game.outcome() == 0:
		if player == 1:
			#input("[Press enter]")
			#cProfile.run("p1.makePlay(game, p1s)")
			#exit(0)
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


	res = game.outcome()
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

	if gameNo == gameCount + 1:
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

	while game.outcome() == 0:
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
	
	print("Player " + str(game.outcome()) + " wins!")
	input("[Press enter to play again]")

