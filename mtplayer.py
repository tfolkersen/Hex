import threading
from fasterplayerst2 import FasterPlayerST2
from queue import Queue
from utils import argmax
import atexit

from multiprocessing import Process, Manager


class MTPlayer:
	def __init__(self, playerNumber, tCount):
		self.playerNumber = playerNumber
		self.timeLimit = 0.0
		self.bootstrap = False
		self.expConst = 0.01
		self.maximizeNonVisited = False
		self.rollouts = 0
		self.gamma = 1.0
		self.tCount = tCount
		self.threads = []


	def configurePlayers(self):
		self.players = []
		self.manager = Manager()
		self.dataDict = self.manager.dict()

		#atexit.register(self.killThreads)

		for i in range(self.tCount):
			p = FasterPlayerST2(self.playerNumber)
			p.timeLimit = self.timeLimit
			p.expConst = self.expConst
			p.bootstrap = self.bootstrap
			p.maximizeNonVisited = self.maximizeNonVisited
			p.gamma = self.gamma
			self.players.append(p)
	
			self.dataDict[str(i) + "flag"] = 0
			proc = Process(target = FasterPlayerST2.startJob, args = (p, i, self.dataDict))
			self.threads.append(proc)
			proc.start()


	def killThreads(self):
		for i in range(len(self.threads)):
			self.dataDict[str(i) + "flag"] = -1
			self.threads[i].join()
		#print("Closed all MTPlayer threads successfully")

	def makePlay(self, state, timeStep):
		self.rollouts = 0

		for i in range(len(self.players)):
			self.dataDict[str(i) + "state"] = state
			self.dataDict[str(i) + "flag"] = 1

		for i in range(len(self.threads)):
			while self.dataDict[str(i) + "flag"] != 0:
				pass

		info = []
		rollouts = []
		for i in range(len(self.threads)):
			info.append(self.dataDict[i])
			rollouts.append(self.dataDict[str(i) + "r"])

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

			mVal = sum([(values[t][m] * visits[t][m]) / allVisits for t in range(len((self.threads)))])
			mValues.append(mVal)

		bestMove = moves[argmax(mValues)]

		state.setHexIndex(bestMove, self.playerNumber)




