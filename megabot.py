import random
from player import Player


class Megabot(Player):
    def __init__(self, game):
        self.game = game
        self.random_empty_pos = tuple(random.randint(0,i-1) for i in self.game.dimensions)
        self.plan={self.random_empty_pos:0}
        #hodnoty by se měly initnout
        #teď to funguje tak že rate(0)=0

        self.history = []

    def turn(self):
        maximum = -100
        maxplace = []
        for i in self.plan:
            if self.plan[i] >= maximum:
                if self.plan[i] > maximum:
                    maxplace = [i]
                else:
                    maxplace.append(i)
                maximum = self.plan[i]
        if maximum < 0: #nejlepší pole je zabrané
            chosen = self.random_empty_pos
        else:
            chosen = random.choice(maxplace)  
        if not self.play(chosen):
            raise ValueError("Could not play to chosen coordinates({}), or winlength > max(dimensions)".format(chosen))
        return
    
    def view(self,reverse=False,pos=None,newsymbol=None):
        if reverse:
            pos=list(pos) #the rest is at the end of count()
        else:
            pos = list(self.game.history[-1])
            self.history.append(self.plan.get(self.game.history[-1],0))
            self.plan[self.game.history[-1]]=0 #must be a tuple!
            newsymbol = self.game.plan[self.game.history[-1]] #must be a tuple!
            self.plan[tuple(pos)] = -1 #zabrané políčko
        lend = len(self.game.dimensions)
        step = [-1 for _ in range(lend)]
        current = pos[:]
        while step != [0 for _ in range(lend)]: #all directions
            for drc in range(self.game.winlength): #all possible winning positions in that direction
                #row=0
                for i in range(lend):
                    pos[i] += drc * step[i]
                symbols = {}
                empty = set()
                for j in range(self.game.winlength): #all coordinates in that winning positions 
                    symbol = self.game.plan.get(tuple(pos),None)
                    #if symbol is not None:
                        #print(pos)
                    #if mysymb is not None and symbol == mysymb:
                        #row+=1
                    if self.game.isempty(tuple(pos)) :
                        empty.add(tuple(pos))
                    elif symbol is None: #out of plan
                        break #this is the break
                        #it should continue with another winning position
                    elif pos != current:
                        symbols[symbol] = symbols.get(symbol,0)+1
                    for i in range(lend):
                        pos[i] -= step[i]
                else: #break as continue
                    if len(symbols) <= 1:
                        if len(symbols) == 0:
                            value = rate(1)
                        elif newsymbol in symbols:
                            value = rate(symbols[newsymbol]+1)-rate(symbols[newsymbol])
                        else:
                            for i in symbols:
                                value=-rate(symbols[i])
                        if reverse: value = -value #uncount(in undo)
                        for i in empty:                           
                            self.plan[i] = self.plan.get(i,0)+ value
                pos = current[:]
                if empty:
                    self.random_empty_pos = empty.pop()
            i = 0
            while i < lend and step[i] == 1:
                step[i] = -1
                i += 1
            step[i] += 1
        if reverse:
            self.plan[tuple(pos)] = self.history.pop()
        return

    def review(self, pos, symbol):
        return self.view(reverse=True,pos=pos,newsymbol=symbol)


def rate(length):
    return 3**(length-1) if length else 0
    #normalne jenom 3**length
