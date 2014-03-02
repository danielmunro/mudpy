import random
    
def get_damage_verb(dam_roll):
    """A string representation of the severity of damage dam_roll will cause.

    """

    if dam_roll < 5:
        return "clumsy"
    elif dam_roll < 10:
        return "amateur"
    elif dam_roll < 15:
        return "competent"
    else:
        return "skillful"

def get_attr_mod(actor, attribute_name):
    """Returns a small integer to be used in fight calculations."""

    return (actor.get_attribute(attribute_name) / actor.MAX_STAT) * 4

def round(aggressor, index = 0):
    """One attack object is created for each aggressor during an attack round
    to resolve all of that aggressor's attacks. The aggressor automatically
    targets the actor stored in aggressor.target.
    
    """

    success = False
    hitroll = 0
    damroll = 0
    defroll = 0
    if index < len(aggressor.attacks):
        attackname = aggressor.attacks[index]
    else:
        return

    handled = aggressor.fire('attack_start')
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

    aggressor.fire('attack_modifier')

    # roll the dice and determine if the attack was successful
    roll = random.uniform(hit_roll/2, hit_roll) - random.uniform(def_roll/2, def_roll) - ac

    success = roll > 0
    if success:
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

    aggressor.fire('attack_resolution')
    round(aggressor, index+1)
