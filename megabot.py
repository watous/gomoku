import random
from player import Player


class Megabot(Player):
    def __init__(self, game):
        self.game = game
        self.empty_position = tuple(random.randint(0,i-1) for i in self.game.dimensions)
        self.plan={self.empty_position:0}
        #should initialize values
        #now it is rate(0)=0
        self.history = []
        self.randomness = 0

    def turn(self):
        maximum = max(self.plan.values())
        maxplace = []
        for i in self.plan:
            if 0 <= self.plan[i] >= maximum - self.randomness:
                maxplace.append(i)
                    
        if maximum < 0: #best position is occupied
            chosen = self.empty_position
        else:
            chosen = random.choice(maxplace)  
        if not self.play(chosen):
            raise ValueError("Could not play to chosen coordinates({})".format(chosen))
        if len(self.history) >= 3:
            self.randomness = 0
        return
    
    def view(self,reverse=False,position=None,newstone=None):
        if reverse:
            position=list(position) #the rest is at the end of count()
        else:
            position = list(self.game.history[-1])
            self.history.append(self.plan.get(self.game.history[-1],0))
            self.plan[self.game.history[-1]]=0 #must be a tuple!
            newstone = self.game.plan[self.game.history[-1]] #must be a tuple!
            self.plan[tuple(position)] = -1 #occupied
        lend = len(self.game.dimensions)
        step = [-1 for _ in range(lend)]
        current = position[:]
        while any(step): #all directions
            for drc in range(self.game.win_length): #all possible winning rows in that direction
                for i in range(lend):
                    position[i] += drc * step[i]
                stones = {}
                empty = set()
                for j in range(self.game.win_length): #all coordinates in that winning positions 
                    stone = self.game.plan.get(tuple(position), None)
                    if self.game.is_empty(tuple(position)) :
                        empty.add(tuple(position))
                    elif stone is None: #out of board
                        break #this is the break
                        #now continue with another winning position, ...
                    elif position != current:
                        stones[stone] = stones.get(stone, 0) + 1
                    for i in range(lend):
                        position[i] -= step[i]
                else: #... skip this
                    if len(stones) <= 1:
                        if len(stones) == 0:
                            value = rate(1)
                        elif newstone in stones:
                            value = rate(stones[newstone] + 1) - rate(stones[newstone])
                        else:
                            for i in stones:
                                value = -rate(stones[i])
                        if reverse: value = -value #review (in undo)
                        for i in empty:                           
                            self.plan[i] = self.plan.get(i, 0)+ value
                position = current[:]
                if empty:
                    self.empty_position = empty.pop()
            i = 0
            while i < lend and step[i] == 1:
                step[i] = -1
                i += 1
            step[i] += 1
        if reverse:
            self.plan[tuple(position)] = self.history.pop()
        """for i in range(self.game.dimensions[0]):
            for j in range(self.game.dimensions[1]):
                print(str(self.plan.get((j,i),0)).rjust(3),end="")
            print()
        print()"""
        return

    def review(self, position, stone):
        return self.view(reverse=True, position=position, newstone=stone)

    def swap(self):
        self.randomness = 10
        


def rate(length):
    return 3**(length-1) if length else 0
    #normally just 3**length
