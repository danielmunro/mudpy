class Attack:
    """One attack object is created for each aggressor during an attack round
    to resolve all of that aggressor's attacks. The aggressor automatically
    targets the actor stored in aggressor.target.
    
    """

    def __init__(self, aggressor, attackname):
        self.aggressor = aggressor
        self.success = False
        self.hitroll = 0
        self.damroll = 0
        self.defroll = 0

        handled = self.aggressor.fire('attack_start', self)
        if handled:
            return

        # initial rolls for attack/defense
        hit_roll = aggressor.get_attribute('hit') + get_attr_mod(aggressor, 'dex')
        def_roll = get_attr_mod(aggressor.target, 'dex') / 2
        def_roll += 5 - aggressor.target.race.size

        # determine dam type from weapon
        weapons = aggressor.get_wielded_weapons()
        try:
            dam_type = weapons[0].damage_type
        except IndexError:
            dam_type = aggressor.race.dam_type

        # get the ac bonus from the damage type
        try:
            ac = aggressor.target.get_attribute('ac_'+dam_type) / 100
        except AttributeError:
            ac = 0

        self.aggressor.fire('attackmodifier', self)

        # roll the dice and determine if the attack was successful
        roll = random.uniform(hit_roll/2, hit_roll) - random.uniform(def_roll/2, def_roll) - ac

        self.success = roll > 0
        if self.success:
            is_hit = "hits"
            dam_roll = aggressor.get_attribute('dam') + get_attr_mod(aggressor, 'str')
            dam_roll = random.uniform(dam_roll/2, dam_roll)
        else:
            is_hit = "misses"
            dam_roll = 0

        # update the room on the attack progress
        verb = get_damage_verb(dam_roll)
        ucname = str(aggressor).title()
        tarname = str(aggressor.target)
        aggressor.get_room().announce({
            aggressor: "("+attackname+") Your "+verb+" attack "+is_hit+" "+tarname+".",
            aggressor.target: ucname+"'s "+verb+" attack "+is_hit+" you.",
            "all": ucname+"'s "+verb+" attack "+is_hit+" "+tarname+"."
        }, add_prompt = False)

        #need to do this check again here, can't have the actor dead before the hit message
        if roll > 0: 
            aggressor.target.curhp -= dam_roll

        aggressor.fire('attack_resolution', self)
