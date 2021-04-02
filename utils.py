'''		some symbols
░·▓
⬢ (bad)
⬣ (good)
'''

import random
import math

colors = {}
colors["white"] = "\033[0m"
colors["blue"] = "\033[94m"
colors["red"] = "\033[31m"


#print a space after each of these
def playerToSymbol(id):
	if id == 0:
		return colors["white"] + "⬣" + colors["white"]
	if id == 1:
		return colors["blue"] + "⬣" + colors["white"]
	if id == 2:
		return colors["red"] + "⬣" + colors["white"]
	raise "Bad player ID exception"

alphabet = "abcdefghijklmnopqrstuvwxyz"

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

def softmax(values):
	e = [math.exp(v) for v in values]
	s = sum(e)
	p = [ev / s for ev in e]

	pi = [(p[i], i) for i in range(len(p))]

	pi.sort(key = lambda x : x[0])

	r = random.random()

	i = 0
	while i < len(pi) - 1:
		if r > pi[i][0]:
			i += 1
		else:
			return pi[i][1]
	return pi[i][1]


def softmin(values):
	e = [math.exp(v) for v in values]
	s = sum(e)
	p = [ev / s for ev in e]

	piNormal = [(p[i], i) for i in range(len(p))]
	piNormal.sort(key = lambda x : x[0])

	l = len(piNormal)
	pi = [(piNormal[i][0], piNormal[l - i - 1][1]) for i in range(l)] 

	r = random.random()

	i = 0
	while i < len(pi) - 1:
		if r > pi[i][0]:
			i += 1
		else:
			return pi[i][1]
	return pi[i][1]

def nextPlayer(current):
	return 1 if current == 2 else 2

