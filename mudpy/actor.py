from __future__ import division
from . import debug, persistence, room, utility
from observer import Observer
from attributes import Attributes
from item import Inventory, Corpse

from random import choice, randint, uniform
import time

class Actor(Observer):
    MAX_STAT = 25

    def __init__(self):
        super(Actor, self).__init__()
        self.id = persistence.getRandomID()
        self.name = "an actor"
        self.long = ""
        self.description = ""
        self.level = 0
        self.experience = 0
        self.alignment = 0
        self.attributes = self.getDefaultAttributes()
        self.trainedAttributes = Attributes()
        self.curhp = self.attributes.hp
        self.curmana = self.attributes.mana
        self.curmovement = self.attributes.movement
        self.sex = "neutral"
        self.room = None
        self.abilities = []
        self.affects = []
        self.target = None
        self.inventory = Inventory()
        self.race = None
        self.trains = 0
        self.practices = 0
        self.disposition = Disposition.STANDING
        self.proficiencies = dict()
        
        self.equipped = dict((position, None) for position in ['light', 'finger0', 'finger1', 'neck0', 'neck1', 'body', 'head', 'legs', 'feet', 'hands', 'arms', 'torso', 'waist', 'wrist0', 'wrist1', 'wield0', 'wield1', 'float'])
        self.attacks = ['reg']
    
    def getProficiencies(self):
        d = dict(self.proficiencies)
        d.update(self.race.proficiencies)
        return d

    def getProficiency(self, proficiency):
        for p in self.getProficiencies():
            if(p.name == proficiency):
                return p
    
    def addProficiency(self, proficiency, level):
        try:
            self.proficiencies[proficiency].level += level
        except KeyError:
            import factory
            from proficiency import Proficiency
            self.proficiencies[proficiency] = factory.new(Proficiency(), proficiency)
            self.proficiencies[proficiency].level = level
    
    def getEquipmentByPosition(self, position):
        for _position in self.equipped:
            if _position.find(position) == 0:
                return self.equipped[_position]
    
    def setEquipment(self, equipment):
        return self.setEquipmentByPosition(equipment.position, equipment)
    
    def setEquipmentByPosition(self, position, equipment):
        for _position in self.equipped:
            if _position.find(position) == 0:
                self.equipped[_position] = equipment
                return True
        return False
    
    def getMovementCost(self):
        return self.race.movementCost + 1 if self.isEncumbered() else self.race.movementCost
    
    def getMaxWeight(self):
        return 100+(self.level*100)
    
    def isEncumbered(self):
        return self.inventory.get_weight() > self.getMaxWeight() * 0.95
    
    def notify(self, message):
        pass
    
    def tick(self):
        modifier = uniform(0.05, 0.125)
        if self.disposition == Disposition.INCAPACITATED:
            modifier = -modifier
        elif self.disposition == Disposition.LAYING:
            modifier += uniform(0.01, 0.05)
        elif self.disposition == Disposition.SLEEPING:
            modifier += uniform(0.05, 0.1)
        self.curhp += self.getAttribute('hp') * modifier
        self.curmana += self.getAttribute('mana') * modifier
        self.curmovement += self.getAttribute('movement') * modifier
        self.normalizestats()
    
    def pulse(self):
        self.doRegularAttacks()
    
    def normalizestats(self):
        for attr in ['hp', 'mana', 'movement']:
            maxstat = self.getAttribute(attr)
            actorattr = 'cur'+attr
            if getattr(self, actorattr) > maxstat:
                setattr(self, actorattr, maxstat)

    def getUnmodifiedAttribute(self, attributeName):
        return getattr(self.attributes, attributeName) + getattr(self.trainedAttributes, attributeName) + getattr(self.race.attributes, attributeName)

    def getAttribute(self, attributeName):
        amount = self.getUnmodifiedAttribute(attributeName)
        for affect in self.affects:
            amount += getattr(affect.attributes, attributeName)
        for equipment in self.equipped.values():
            if equipment:
                amount += getattr(equipment.attributes, attributeName)
        if attributeName in Attributes.stats:
            return min(amount, self.getMaxAttribute(attributeName))
        return amount

    def getMaxAttribute(self, attributeName):
        racialAttr = getattr(self.race.attributes, attributeName)
        return min(getattr(self.attributes, attributeName) + racialAttr + 4, racialAttr + 8)
    
    def getAbilities(self):
        return self.abilities + self.race.abilities

    def __str__(self):
        return self.name
    
    def getWieldedWeapons(self):
        return list(equipment for equipment in [self.equipped['wield0'], self.equipped['wield1']] if equipment)
    
    def doRegularAttacks(self, recursedAttackIndex = 0):
        from . import server
        if self.target:
            if not self.target.target:
                self.target.target = self
                server.__instance__.heartbeat.attach('pulse', self.target.pulse)

            if self.disposition != Disposition.INCAPACITATED:
                try:
                    Attack(self, self.attacks[recursedAttackIndex])
                    self.doRegularAttacks(recursedAttackIndex + 1)
                except IndexError: pass
        else:
            server.__instance__.heartbeat.detach('pulse', self)
    
    def status(self):
        hppercent = self.curhp / self.getAttribute('hp')
        
        if hppercent < 0.1:
            description = 'is in awful condition'
        elif hppercent < 0.15:
            description = 'looks pretty hurt'
        elif hppercent < 0.30:
            description = 'has some big nasty wounds and scratches'
        elif hppercent < 0.50:
            description = 'has quite a few wounds'
        elif hppercent < 0.75:
            description = 'has some small wounds and bruises'
        elif hppercent < 0.99:
            description = 'has a few scratches'
        else:
            description = 'is in excellent condition'

        return str(self).title()+' '+description+'.'
    
    def move(self, direction):
        from . import command, factory

        if self.target:
            self.notify("You are fighting!")
            return

        if self.disposition == Disposition.INCAPACITATED:
            self.notify("You are incapacitated and will die soon if not aided.")
            return

        new_room = self.room.directions[direction]
        if not new_room:
            self.notify("Alas, nothing is there.")
            return

        cost = self.getMovementCost()
        if(self.attributes.movement >= cost):
            # actor is leaving, subtract movement cost
            self.attributes.movement -= cost

            # remove actor from room
            self.room.dispatch('leaving', actor=self, direction=direction)
            self.room.actors.remove(self)
            self.room.detach('leaving', self.leaving)
            self.room.detach('arriving', self.arriving)

            # place actor in new room
            self.room = new_room
            self.room.actors.append(self)
            self.room.dispatch('arriving', actor=self, direction=room.Direction.get_reverse(direction))
            self.room.attach('leaving', self.leaving)
            self.room.attach('arriving', self.arriving)
            self.moved(direction)
            debug.log(str(self)+' moves to '+str(self.room))
        else:
            self.notify("You are too tired to move.")

    def moved(self, args):
        pass
    
    def die(self):
        if self.target:
            self.target.rewardExperienceFrom(self)
        self.removeFromBattle()
        self.disposition = Disposition.LAYING
        self.curhp = 1
        corpse = Corpse()
        corpse.name = "the corpse of "+str(self)
        corpse.description = "The corpse of "+str(self)+" lies here."
        corpse.weight = self.race.size * 20
        corpse.material = "flesh"
        for item in self.inventory.items:
            self.inventory.remove(item)
            corpse.inventory.append(item)
        self.room.inventory.append(corpse)
    
    def rewardExperienceFrom(self, victim):
        self.experience += victim.getKillExperience(self)
        diff = self.experience / self.getExperiencePerLevel()
        if diff > self.level:
            gain = 0
            while gain < diff:
                self.levelUp()
                gain += 1
    
    def getKillExperience(self, killer):
        leveldiff = self.level - killer.level
        experience = 200 + 30 * leveldiff
        if leveldiff > 5:
            experience *= 1 + randint(0, leveldiff*2) / 100
        aligndiff = abs(self.alignment - killer.alignment) / 2000
        if aligndiff > 0.5:
            mod = randint(15, 35) / 100
            experience *= 1 + aligndiff - mod
        experience = uniform(experience * 0.8, experience * 1.2)
        return experience if experience > 0 else 0

    def getExperiencePerLevel(self):
        return 1000

    def levelUp(self):
        self.level += 1
    
    def removeFromBattle(self):
        if self.target and self.target.target is self:
            self.target.target = None

        if self.target:
            self.target = None
    
    def getAlignment(self):
        if self.alignment <= -1000:
            return "evil"
        elif self.alignment <= 0:
            return "neutral"
        elif self.alignment >= 1000:
            return "good"
    
    def lookedAt(self):
        return self.long if self.long else str(self)+" the "+str(self.race)+" is "+self.disposition+" here"

    def startAffect(self, args):
        self.room.announce(args['affect'].getMessages('success', self))
        self.affects.append(args['affect'])
    
    def endAffect(self, affect):
        self.room.announce(args['affect'].getMessages('end', self))
        self.affects.remove(affect)

    def leaving(self, actor):
        pass

    def arriving(self, actor):
        pass
    
    @staticmethod
    def getDamageVerb(dam_roll):
        if dam_roll < 5:
            return "clumsy"
        elif dam_roll < 10:
            return "amateur"
        elif dam_roll < 15:
            return "competent"
        else:
            return "skillful"

    @staticmethod
    def getDefaultAttributes():
        a = Attributes()
        a.hp = 20
        a.mana = 100
        a.movement = 100
        a.ac_bash = 100
        a.ac_pierce = 100
        a.ac_slash = 100
        a.ac_magic = 100
        a.hit = 1
        a.dam = 1
        return a

class Mob(Actor):
    ROLE_TRAINER = 'trainer'
    ROLE_ACOLYTE = 'acolyte'

    def __init__(self):
        self.movement = 0
        self.movement_timer = self.movement
        self.respawn = 1
        self.auto_flee = False
        self.area = None
        self.role = ''
        super(Mob, self).__init__()
    
    def tick(self):
        super(Mob, self).tick()
        if self.movement:
            self.decrementMovementTimer()
    
    def decrementMovementTimer(self):
        self.movement_timer -= 1;
        if self.movement_timer < 0:
            direction = choice([direction for direction, room in self.room.directions.iteritems() if room and room.area == self.room.area])
            self.move(direction)
            self.movement_timer = self.movement
    
    def normalizestats(self):
        if self.curhp < 0:
            self.die()
        super(Mob, self).normalizestats()
    
    def die(self):
        super(Mob, self).die()
        self.room.announce({
            "*": str(self).title()+" arrives in a puff of smoke."
        })
    
class User(Actor):
    persistibleProperties = ['id', 'name', 'long', 'level', 'experience', 'alignment', 'attributes', 'trainedAttributes', 'affects', 'sex', 'abilities', 'inventory', 'trains', 'practices', 'disposition', 'proficiencies']

    def __init__(self):
        from . import server
        super(User, self).__init__()
        self.delay_counter = 0
        self.last_delay = 0
        self.trains = 5
        self.practices = 5
        self.client = None
        server.__instance__.heartbeat.attach('stat', self.stat)
        server.__instance__.heartbeat.attach('cycle', self.updateDelay)
    
    def prompt(self):
        return "%i %i %i >> " % (self.curhp, self.curmana, self.curmovement)
    
    def notify(self, message):
        if self.client.user:
            self.client.write(message)
    
    def tick(self):
        super(User, self).tick()
        self.notify("\n"+self.prompt())
    
    def stat(self):
        if self.target:
            self.notify(self.target.status()+"\n\n"+self.prompt())
    
    def normalizestats(self):
        if self.curhp < -9:
            self.die()
        elif self.curhp <= 0:
            self.disposition = Disposition.INCAPACITATED
            self.notify("You are incapacitated and will slowly die if not aided.\n")
        elif self.disposition == Disposition.INCAPACITATED and self.curhp > 0:
            self.disposition = Disposition.LAYING
            self.notify("You suddenly feel a bit better.\n")
        super(User, self).normalizestats()
    
    def die(self):
        super(User, self).die()
        self.room.actors.remove(self)
        self.room = room.__ROOMS__[room.__START_ROOM__]
        self.room.actors.append(self)
        self.room.announce({
            self: "You feel a rejuvinating rush as you pass through this mortal plane.",
            "*": str(self).title()+" arrives in a puff of smoke."
        })
        self.notify("\n"+self.prompt())
    
    def updateDelay(self):
        from . import server
        if self.delay_counter > 0:
            if not self.last_delay:
                server.__instance__.heartbeat.detach('cycle', self.client.poll)
            currenttime = int(time.time())
            if currenttime > self.last_delay:
                self.delay_counter -= 1
                self.last_delay = currenttime
        elif self.last_delay:
            server.__instance__.heartbeat.attach('cycle', self.client.poll)
            self.last_delay = 0
    
    def levelUp(self):
        super(User, self).levelUp()
        self.notify("You leveled up!")
    
    def loggedin(self):

        def performAbility(ability):
            self.delay_counter += ability.delay+1

        from . import factory, server
        from command import Command
        if not self.room:
            self.room = room.__ROOMS__[room.__START_ROOM__]
        server.__instance__.heartbeat.attach('tick', self.tick)
        factory.new(Command(), "look").tryPerform(self)
        self.room.actors.append(self)
        self.notify("\n"+self.prompt())
        debug.log('client logged in as '+str(self))
        for ability in self.getAbilities():
            ability.attach('perform', performAbility)
            def checkInput(args):
                if ability.name.startswith(args[1]):
                    ability.tryPerform(self, args[2:])
                    return True
            self.client.attach('input', checkInput)

    def leaving(self, args):
        super(User, self).leaving(args)
        if not args['actor'] == self:
            self.notify(str(args['actor'])+" left heading "+args['direction']+".\n")

    def arriving(self, args):
        super(User, self).arriving(args)
        self.notify(str(args['actor'])+" arrived from the "+args['direction']+".\n")

    def moved(self, args):
        from . import factory, command
        factory.new(command.Command(), "look").tryPerform(self)

    def __str__(self):
        return self.name.title()

class Disposition:
    STANDING = 'standing'
    SITTING = 'sitting'
    LAYING = 'laying'
    SLEEPING = 'sleeping'
    INCAPACITATED = 'incapacitated'

class Attack:

    def __init__(self, aggressor, attackname):
        self.aggressor = aggressor
        self.success = False
        self.hitroll = 0
        self.damroll = 0
        self.defroll = 0

        self.aggressor.dispatch('attackstart', attack=self)

        # initial rolls for attack/defense
        hit_roll = aggressor.getAttribute('hit') + self.getAttributeModifier(aggressor, 'dex')
        def_roll = self.getAttributeModifier(aggressor.target, 'dex') / 2
        def_roll += 5 - aggressor.target.race.size

        # determine dam type from weapon
        weapons = aggressor.getWieldedWeapons()
        try:
            damType = weapons[0].damageType
        except IndexError:
            damType = aggressor.race.damType

        # get the ac bonus from the damage type
        try:
            ac = aggressor.target.getAttribute('ac_'+damType) / 100
        except AttributeError:
            ac = 0

        self.aggressor.dispatch('attackmodifier', attack=self)

        # roll the dice and determine if the attack was successful
        roll = uniform(hit_roll/2, hit_roll) - uniform(def_roll/2, def_roll) - ac

        self.success = roll > 0
        if self.success:
            isHit = "hits"
            dam_roll = aggressor.getAttribute('dam') + self.getAttributeModifier(aggressor, 'str')
            dam_roll = uniform(dam_roll/2, dam_roll)
        else:
            isHit = "misses"
            dam_roll = 0

        # update the room on the attack progress
        verb = Actor.getDamageVerb(dam_roll)
        ucname = str(aggressor).title()
        tarname = str(aggressor.target)
        aggressor.room.announce({
            aggressor: "("+attackname+") Your "+verb+" attack "+isHit+" "+tarname+".",
            aggressor.target: ucname+"'s "+verb+" attack "+isHit+" you.",
            "*": ucname+"'s "+verb+" attack "+isHit+" "+tarname+"."
        })

        #need to do this check again here, can't have the actor dead before the hit message
        if roll > 0: 
            aggressor.target.curhp -= dam_roll
            aggressor.target.normalizestats()

        aggressor.dispatch('attackresolution', attack=self)
    
    def getAttributeModifier(self, actor, attributeName):
        return (actor.getAttribute(attributeName) / Actor.MAX_STAT) * 4

class Ability(Observer, room.Reporter):

    def __init__(self):
        self.name = "an ability"
        self.level = 0
        self.affects = []
        self.costs = {}
        self.delay = 0
        self.type = "" # skill or spell
        self.hook = ""
        self.aggro = False
        self.messages = {}
        super(Ability, self).__init__()
    
    def tryPerform(self, invoker, args):
        try:
            receiver = utility.match_partial(args[-1], invoker.room.actors)
        except IndexError:
            receiver = invoker
        if self.applyCost(invoker):
            invoker.delay_counter += self.delay + 1
            if self.rollsSuccess(invoker, receiver):
                self.perform(invoker, receiver, args)
            else:
                receiver.room.announce(self.getMessages('fail', invoker, receiver))
        else:
            invoker.notify("You do not have enough energy to do that.")

    def perform(self, invoker, receiver, args):
        import factory
        from affect import Affect

        for affectname in self.affects:
            factory.new(Affect(), affectname).start(receiver)

    def rollsSuccess(self, invoker, receiver):
        return True # chosen by coin toss, guaranteed to be random
    
    def applyCost(self, invoker):
        for attr, cost in self.costs.iteritems():
            curattr = getattr(invoker, 'cur'+attr)
            cost *= curattr if cost > 0 and cost < 1 else 1
            if curattr < cost:
                return False
        for attr, cost in self.costs.iteritems():
            curattr = getattr(invoker, 'cur'+attr)
            cost *= curattr if cost > 0 and cost < 1 else 1
            setattr(invoker, 'cur'+attr, curattr-cost)
        return True
    
    def __str__(self):
        return self.name;

class Race:
    SIZE_TINY = 1
    SIZE_SMALL = 2
    SIZE_NORMAL = 3
    SIZE_LARGE = 4
    SIZE_GIGANTIC = 5

    def __init__(self):
        self.name = "critter"
        self.size = self.SIZE_NORMAL
        self.movementCost = 1
        self.isPlayable = False
        self.damType = "bash"
        self.proficiencies = {}
        self.attributes = Attributes()
        self.abilities = []
        self.affects = []
    
    def addProficiency(self, proficiency, level):
        try:
            self.proficiencies[proficiency].level += level
        except KeyError:
            import factory
            from proficiency import Proficiency
            self.proficiencies[proficiency] = factory.new(Proficiency(), proficiency)
            self.proficiencies[proficiency].level = level

    def __str__(self):
        return self.name
