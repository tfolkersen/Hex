from state import State
from randomplayer import RandomPlayer
import random

from utils import *


wdist = 4
bdist = 4

while True:
    p1 = RandomPlayer(1)
    p2 = RandomPlayer(2)

    game = State(wdist, bdist)

    player = random.randint(1, 2)

    timestep = 1

    while game.outcome() == 0:
        if player == 1:
            p1.makePlay(game, 
   
