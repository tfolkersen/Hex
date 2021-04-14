"""		mtplayer

	Defines a multithreaded player that runs a player on each thread.
"""

from fasterplayer2 import FasterPlayer2
from fasterplayer3 import FasterPlayer3
from utils import argmax
import atexit

#don't use default "threading" library as this has the global interpreter lock problem
from multiprocessing import Process, Manager


"""		MTPlayer

	Multithreaded player class. On each thread it runs an independent player, and then
		it gets back value estimates from those players and combines them. The players are
		independent because large amounts of data can't be shared between them. The Process
		class creates a new separate process with its own memory space.
"""
class MTPlayer:
	"""		(constructor)

		player -- integer of player this Player represents (1 or 2)
		tCount -- how many threads to use
		useAltPlayer -- default False, if True will use a different player

		User must run configurePlayers after setting parameters, then these are copied to
			the child processes.
	"""
	def __init__(self, player, tCount, useAltPlayer = False):
		self.player = player
		self.timeLimit = 0.0
		self.expConst = 0.01
		self.maximizeNonVisited = False
		self.rollouts = 0
		self.gamma = 1.0
		self.tCount = tCount
		self.threads = [] #child processes
		self.message = "" #If this Player has a message to print, put it here
		self.useAltPlayer = useAltPlayer

	"""		configurePlayers

		Creates child processes and copy configuration data to them.
	"""
	def configurePlayers(self):
		self.players = []
		self.manager = Manager()
		self.dataDict = self.manager.dict()

		#atexit.register(self.killThreads)

		if self.useAltPlayer:
			self.playerName = "MT-FasterPlayer2"
		else:
			self.playerName = "MT-FasterPlayer3"

		for i in range(self.tCount):
			if self.useAltPlayer:
				p = FasterPlayer2(self.player)
			else:
				p = FasterPlayer3(self.player)
			p.timeLimit = self.timeLimit
			p.expConst = self.expConst
			p.maximizeNonVisited = self.maximizeNonVisited
			p.gamma = self.gamma
			self.players.append(p)
	
			self.dataDict[str(i) + "flag"] = 0
			proc = Process(target = FasterPlayer2.startJob, args = (p, i, self.dataDict))
			self.threads.append(proc)
			proc.start()

	"""		killThreads

		Tells all child processes to return.
	"""
	def killThreads(self):
		for i in range(len(self.threads)):
			self.dataDict[str(i) + "flag"] = -1
			self.threads[i].join()
		#print("Closed all MTPlayer threads successfully")

	"""		getPlay

		state -- instance of State to play on

		Given a game state, returns a move.
	"""
	def getPlay(self, state):
		self.message = ""
		self.rollouts = 0

		for i in range(len(self.players)): #give state to child processes and tell them all to work
			self.dataDict[str(i) + "state"] = state
			self.dataDict[str(i) + "msg"] = ""
			self.dataDict[str(i) + "flag"] = 1
			

		for i in range(len(self.threads)): #Wait for all children to finish
			while self.dataDict[str(i) + "flag"] != 0:
				pass

		info = [] #returned data from each child process
		rollouts = []
		messages = []
		for i in range(len(self.threads)):
			info.append(self.dataDict[i])
			rollouts.append(self.dataDict[str(i) + "r"])
			messages.append(self.dataDict[str(i) + "msg"] + " ")

		self.message = messages

		self.rollouts = sum(rollouts)

		moves = state.moves()
		visits = [inf[0] for inf in info]
		values = [inf[1] for inf in info]

		mValues = [] #weighted sum of move values

		for m in range(len(moves)): #for each move
			allVisits = sum([vis[m] for vis in visits]) #all visits to this child

			if allVisits == 0: #no value -- hasn't been visited
				mValues.append(0)
				continue

			mVal = sum([(values[t][m] * visits[t][m]) / allVisits for t in range(len(self.threads))]) #sum values weighted by visit count
			mValues.append(mVal)

		bestMove = moves[argmax(mValues)]

		return bestMove





