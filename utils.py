"""		utils

	Defines various utility functions and data.
"""

import random
import math
import string

#ANSI color codes
#See https://en.wikipedia.org/wiki/ANSI_escape_code#Colors
#For example, blue is "bright blue", and red is just "red"
colors = {}
colors["white"] = "\033[0m"
colors["red"] = "\033[31m"
colors["yellow"] = "\33[93m"
colors["green"] = "\033[92m"
colors["blue"] = "\033[94m"
colors["pink"] = "\33[95m"

#Player colors -- changing these should change these colors everywhere
colors["p1"] = colors["blue"]
colors["p2"] = colors["red"]

"""		playerToSymbol

	id -- integer id of player (0 for empty space, 1 for black, 2 for white)

	Returns string representing tile graphic for a player.
		The black player (1) is actually blue, and the white player (2) is actually red.
"""
def playerToSymbol(id):
	if id == 0:
		return colors["white"] + "⬣" + colors["white"]
	if id == 1:
		return colors["p1"] + "⬣" + colors["white"]
	if id == 2:
		return colors["p2"] + "⬣" + colors["white"]

	print("Bad player ID")
	raise

"""		alphaLabel

	id -- integer label in range [1, 26]

	Converts integer representing label on Hex board to an alphabet label.
"""
def alphaLabel(id):
	if id < 1 or id > 26:
		print("Bad label ID: " + str(id) + " (should be in [1, 26])")
		raise
	return string.ascii_lowercase[id - 1]

"""		argmax

	values -- list of values

	Returns index of list item having maximal value. Breaks ties randomly.
"""
def argmax(values):
	bestValue = values[0]
	bestIndices = [0]

	for i in range(1, len(values)):
		v = values[i]

		if v == bestValue:
			bestIndices.append(i)
		if v > bestValue:
			bestValue = v
			bestIndices = [i]

	return bestIndices[random.randint(0, len(bestIndices) - 1)]

"""		argmin

	values -- list of values

	Returns index of list item having minimal value. Breaks ties randomly.
"""
def argmin(values):
	bestValue = values[0]
	bestIndices = [0]

	for i in range(1, len(values)):
		v = values[i]

		if v == bestValue:
			bestIndices.append(i)
		if v < bestValue:
			bestValue = v
			bestIndices = [i]

	return bestIndices[random.randint(0, len(bestIndices) - 1)]

"""		softmax

	values -- list of values

	Returns index of an element according to the exponential softmax distribution. Larger elements are exponentially
		more likely to be chosen.
"""
def softmax(values):
	e = [math.exp(v) for v in values]
	s = sum(e)
	p = [ev / s for ev in e] #probability

	pi = [(p[i], i) for i in range(len(p))] #probability with index

	pi.sort(key = lambda x : x[0]) #sort by probability

	r = random.random() #roll

	i = 0
	while i < len(pi) - 1:
		if r > pi[i][0]:
			i += 1
		else:
			return pi[i][1]
	return pi[i][1]

"""		softmin

	values -- list of values

	Returns index of an element according to the exponential softmax distribution, but smaller elements are exponentially
		more likely to be chosen.
"""
def softmin(values):
	e = [math.exp(v) for v in values]
	s = sum(e)
	p = [ev / s for ev in e] #probability for softmax

	piNormal = [(p[i], i) for i in range(len(p))]
	piNormal.sort(key = lambda x : x[0]) #probability with index for argmax

	l = len(piNormal)
	pi = [(piNormal[i][0], piNormal[l - i - 1][1]) for i in range(l)] #shift indices to get argmin

	r = random.random() #roll

	i = 0
	while i < len(pi) - 1:
		if r > pi[i][0]:
			i += 1
		else:
			return pi[i][1]
	return pi[i][1]

"""		nextPlayer

	current -- integer representing current player (1 for black, 2 for white)

	Returns the number representing the player other than the one given.
"""
def nextPlayer(current):
	return 1 if current == 2 else 2
