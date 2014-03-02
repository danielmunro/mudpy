class Proficiency:
    def __init__(self):
        self.hook = ""
        self.improvechance = 0.05
        self.level = 15
    
    def checkimprove(self):
        # @todo make this work
        return
        from random import random
        if random() < self.improvechance:
            self.level += 1
            self.observer.notify("Your skill in "+str(self)+" improves!")
        elif random() - 0.01 < self.improvechance:
            self.level += 1
            self.observer.notify("Learning from your mistakes, your skill in "+str(self)+" improves!")
    
    def messageLearnSuccess(self):
        return 
    
    def __str__(self):
        return self.name
    
    def attackstart(self):
        self.checkimprove()

    def attackmodifier(self):
        self.checkimprove()

    def attackresolution(self):
        self.checkimprove()
    
    def move(self):
        self.checkimprove()
    
    def sell(self):
        self.checkimprove()
    
    def brew(self):
        self.checkimprove()
    
    def cast(self):
        self.checkimprove()
    
    def melee(self, attack):
        aggro = attack.aggressor
        tar = aggro.target

        try:
            aggrolvl = aggro.proficiencies['melee']
        except KeyError:
            aggrolvl = 1

        try:
            tarlvl = tar.proficiencies['melee']
        except KeyError:
            tarlvl = 1

        attack.hitroll += aggro.level * (aggrolvl / 100) - (tarlvl / 100)
