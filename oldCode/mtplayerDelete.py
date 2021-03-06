import threading
from fasterplayerst2Delete import FasterPlayerST2Delete
from queue import Queue
from utils import argmax

from multiprocessing import Process, Manager


class MTPlayerDelete:
	def __init__(self, playerNumber, threads):
		self.playerNumber = playerNumber
		self.timeLimit = 0.0
		self.bootstrap = False
		self.expConst = 0.01
		self.maximizeNonVisited = False
		self.rollouts = 0
		self.gamma = 1.0
		self.threads = threads


	def configurePlayers(self):
		self.players = []
		for i in range(self.threads):
			p = FasterPlayerST2Delete(self.playerNumber)
			p.timeLimit = self.timeLimit
			p.expConst = self.expConst
			p.bootstrap = self.bootstrap
			p.maximizeNonVisited = self.maximizeNonVisited
			p.gamma = self.gamma
			self.players.append(p)


	def makePlay(self, state, timeStep):
		self.rollouts = 0
		threads = []
		returns = []

		manager = Manager()
		returnDict = manager.dict()
		for tNum in range(len(self.players)):
			#returns.append(Queue())
			#t = threading.Thread(target = p.getPlayInfo, args=(state, timeStep, returns[-1]))
			p = self.players[tNum]
			t = Process(target = p.getPlayInfo, args = (state, timeStep, tNum, returnDict))
			threads.append(t)
			t.start()

		for i in range(len(threads)):
			threads[i].join()

		info = []
		rollouts = []
		for i in range(len(threads)):
			info.append(returnDict[i])
			rollouts.append(returnDict[str(i) + "r"])

		self.rollouts = sum(rollouts)

		moves = state.moves()
		visits = [inf[0] for inf in info]
		values = [inf[1] for inf in info]

		mValues = []

		for m in range(len(moves)):
			allVisits = sum([vis[m] for vis in visits])

			if allVisits == 0:
				mValues.append(0)
				continue

			mVal = sum([(values[t][m] * visits[t][m]) / allVisits for t in range(self.threads)])
			mValues.append(mVal)

		bestMove = moves[argmax(mValues)]


		state.setHexIndex(bestMove, self.playerNumber)




