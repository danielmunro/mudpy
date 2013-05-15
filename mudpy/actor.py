from __future__ import division
from . import debug, room, utility, server, factory, proficiency, \
                item, attributes, observer, command, affect
import time, random, os, pickle

__SAVE_DIR__ = 'users'
    
def get_damage_verb(dam_roll):
    if dam_roll < 5:
        return "clumsy"
    elif dam_roll < 10:
        return "amateur"
    elif dam_roll < 15:
        return "competent"
    else:
        return "skillful"

def get_default_attributes():
    a = attributes.Attributes()
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

def get_user_file(name):
    return os.path.join(os.getcwd(), __SAVE_DIR__, name+'.pk')

def load(name):
    user = None
    user_file = get_user_file(name)
    if os.path.isfile(user_file):
        with open(user_file, 'rb') as fp:
            user = pickle.load(fp)
    return user

class Actor(observer.Observer):
    MAX_STAT = 25

    def __init__(self):
        super(Actor, self).__init__()
        self.name = "an actor"
        self.long = ""
        self.description = ""
        self.level = 0
        self.experience = 0
        self.alignment = 0
        self.attributes = get_default_attributes()
        self.trainedAttributes = attributes.Attributes()
        self.curhp = self.attributes.hp
        self.curmana = self.attributes.mana
        self.curmovement = self.attributes.movement
        self.sex = "neutral"
        self.room = None
        self.abilities = []
        self.affects = []
        self.target = None
        self.inventory = item.Inventory()
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
        for p, prof in self.getProficiencies().iteritems():
            if(prof.name == proficiency):
                return prof
    
    def addProficiency(self, proficiency, level):
        proficiency = str(proficiency)
        try:
            self.proficiencies[proficiency].level += level
        except KeyError:
            self.proficiencies[proficiency] = factory.new(proficiency.Proficiency(), proficiency)
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
        modifier = random.uniform(0.05, 0.125)
        if self.disposition == Disposition.INCAPACITATED:
            modifier = -modifier
        elif self.disposition == Disposition.LAYING:
            modifier += random.uniform(0.01, 0.05)
        elif self.disposition == Disposition.SLEEPING:
            modifier += random.uniform(0.05, 0.1)
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
        if attributeName in attributes.Attributes.stats:
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
            self.room.actor_leave(self, direction)
            self.room = new_room
            self.room.actor_arrive(self, room.Direction.get_reverse(direction))
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
        corpse = item.Corpse()
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
            experience *= 1 + random.randint(0, leveldiff*2) / 100
        aligndiff = abs(self.alignment - killer.alignment) / 2000
        if aligndiff > 0.5:
            mod = random.randint(15, 35) / 100
            experience *= 1 + aligndiff - mod
        experience = random.uniform(experience * 0.8, experience * 1.2)
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

    def disposition_changed(self, args):
        pass

    def command_north(self, args):
        self.move("north")

    def command_south(self, args):
        self.move("south")

    def command_east(self, args):
        self.move("east")

    def command_west(self, args):
        self.move("west")

    def command_up(self, args):
        self.move("up")

    def command_down(self, args):
        self.move("down")

    def command_sit(self, args):
        self.disposition = Disposition.SITTING
        self.room.dispatch("disposition_changed", actor=self, changed=str(self).title()+" sits down and rest.")

    def command_wake(self, args):
        self.disposition = Disposition.STANDING
        self.room.dispatch("disposition_changed", actor=self, changed=str(self).title()+" stands up.")

    def command_sleep(self, args):
        self.disposition = Disposition.SLEEPING
        self.room.dispatch("disposition_changed", actor=self, changed=str(self).title()+" goes to sleep.")

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
            direction = random.choice([direction for direction, room in self.room.directions.iteritems() if room and room.area == self.room.area])
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
    def __init__(self):
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
        self.room.actor_leave(self)
        self.room = room.__ROOMS__[room.__START_ROOM__]
        self.room.actor_arrive(self)
        self.room.announce({
            self: "You feel a rejuvinating rush as you pass through this mortal plane.",
            "*": str(self).title()+" arrives in a puff of smoke."
        })
        self.notify("\n"+self.prompt())
    
    def updateDelay(self):
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

    def performAbility(ability):
        self.delay_counter += ability.delay+1
    
    def loggedin(self):
        # set the room
        try:
            new_room_id = getattr(self, 'room_id')
        except AttributeError:
            new_room_id = room.__START_ROOM__
        self.room = room.__ROOMS__[new_room_id]
        self.room.actor_arrive(self)

        # attach a listener to client input
        self.client.attach('input', self.check_input)

        # attach a listener to the server tick
        server.__instance__.heartbeat.attach('tick', self.tick)

        # attach listeners to client input for abilities
        for ability in self.getAbilities():
            ability.attach('perform', self.performAbility)
            def checkInput(args):
                if ability.name.startswith(args[1]):
                    ability.tryPerform(self, args[2:])
                    return True
            self.client.attach('input', checkInput)

        # look and prompt
        self.command_look()
        self.notify("\n"+self.prompt())

        debug.log('client logged in as '+str(self))

    def check_input(self, args):
        args = args['args']
        try:
            com = factory.new(command.Command(), factory.match(args[0], 'mudpy.command.Command')['wireframe'])
            com.try_perform(self, args)
            handled = True
        except factory.FactoryException:
            handled = False
        return handled

    def leaving(self, args):
        super(User, self).leaving(args)
        if not args['actor'] == self:
            self.notify(str(args['actor'])+" left heading "+args['direction']+".\n")

    def arriving(self, args):
        super(User, self).arriving(args)
        self.notify(str(args['actor'])+" arrived from the "+args['direction']+".\n")

    def moved(self, args):
        self.command_look()

    def disposition_changed(self, args):
        super(User, self).disposition_changed(args)
        if args['actor'] != self:
            self.notify(args['changed'])

    def save(self):
        client = self.client
        room = self.room
        self.client = None
        self.room = None
        self.room_id = room.get_full_id()
        with open(get_user_file(self.name), 'wb') as fp:
            pickle.dump(self, fp, pickle.HIGHEST_PROTOCOL)
        self.client = client
        self.room = room

    def command_look(self, args=[]):
        if len(args) <= 1:
            # room and exits
            msg = "%s\n%s\n\n[Exits %s]\n" % (self.room.name, self.room.description, "".join(direction[:1] for direction, room in self.room.directions.iteritems() if room))
            # items
            msg += self.room.inventory.inspection(' is here.')
            # actors
            msg += "\n".join(_actor.lookedAt().capitalize() for _actor in self.room.actors if _actor is not self)+"\n"
        else:
            lookingAt = utility.match_partial(args[0], self.inventory.items, self.room.inventory.items, self.room.actors)
            msg = lookingAt.description.capitalize()+"\n" if lookingAt else "Nothing is there."
        self.notify(msg)

    def command_affects(self, args):
        self.notify("Your affects:\n"+"\n".join(str(x)+": "+str(x.timeout)+\
                    " ticks" for x in self.affects))

    def command_sit(self, args):
        super(User, self).command_sit(args)
        self.notify("You sit down and rest.")

    def command_wake(self, args):
        super(User, self).command_wake(args)
        self.notify("You stand up.")

    def command_sleep(self, args):
        super(User, self).command_sleep(args)
        self.notify("You go to sleep.")

    def command_practice(self, args):
        if len(args) == 1:
            self.notify("Your proficiencies:\n" + \
                    "\n".join(name+": "+str(proficiency.level) \
                    for name, proficiency in self.getProficiencies().iteritems()))
        elif any(mob.role == Mob.ROLE_ACOLYTE for mob in self.room.mobs()):
            for p in self.getProficiencies():
                if p.find(args[1]) == 0:
                    self.getProficiency(p).level += 1
                    self.notify("You get better at "+p+"!")
                    return
                self.notify("You cannot practice that.")
        else:
            self.notify("No one is here to help you practice.")

    def command_quit(self, args):
        self.save()
        self.client.disconnect()

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
        roll = random.uniform(hit_roll/2, hit_roll) - random.uniform(def_roll/2, def_roll) - ac

        self.success = roll > 0
        if self.success:
            isHit = "hits"
            dam_roll = aggressor.getAttribute('dam') + self.getAttributeModifier(aggressor, 'str')
            dam_roll = random.uniform(dam_roll/2, dam_roll)
        else:
            isHit = "misses"
            dam_roll = 0

        # update the room on the attack progress
        verb = get_damage_verb(dam_roll)
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

class Ability(observer.Observer, room.Reporter):

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
        for affectname in self.affects:
            factory.new(affect.Affect(), affectname).start(receiver)

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
        return self.name

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
        self.attributes = attributes.Attributes()
        self.abilities = []
        self.affects = []
    
    def addProficiency(self, prof, level):
        prof = str(prof)
        try:
            self.proficiencies[prof].level += level
        except KeyError:
            self.proficiencies[prof] = factory.new(proficiency.Proficiency(), prof)
            self.proficiencies[prof].level = level

    def __str__(self):
        return self.name
