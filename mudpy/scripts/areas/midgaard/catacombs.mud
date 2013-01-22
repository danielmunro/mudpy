area
name Midgaard Catacombs, terrain city, location indoors

randomhall
Midgaard Catacombs
The subterranean catacombs wind under the city of Midgaard, where many adventurers have met their fate.~
id 45, u Adelwine Manor:44, rooms 10, uProb 0, dProb .75, exit 46

mob
a kobold peon is carrying mining equipment
An ugly little kobold saunters around. He is hairy and smells like wet mold.~
movement_timeout 2, level 15, race kobold, name a kobold peon#, count 5
hp 35
#second attack

weapon
a crude mining pick lays here
A crude mining pick is here. It looks to be of kobold origin from the style and craftsmanship, or lack thereof.~
value 4, weight 3, level 3, material metal, weaponType flail, damageType pierce, verb pierce, repop 50
hit 1

equipment
a brass lantern
A brass lantern that once belonged to a kobold lies here.~
value 2, weight 1, level 1, material brass, position light, repop 10

item
a tin trinket
A small tin trinket is here.~
value 5, weight 1, material tin, repop 10

randomhall
Deep Within the Catacombs
You follow a tunnel narrowly carved through rock and dirt as it winds further under Midgaard.~
id 46, rooms 10, uProb 0, dProb .75, exit 47

mob
a kobold driver is here with whip in hand
A kobold driver is belting orders to the peons. He is responsible for keeping the mine going and won't tolerate slow downs.~
movement_timeout 2, level 18, race kobold, name a kobold driver#, count 5
hp 50
#dodge, second attack

equipment
a crude helmet
A crude kobold helmet is here, a simple piece of metal shaped into a helmet.~
position head, level 5, value 5, weight 6, material nickel
ac_slash -5, ac_bash -5, ac_pierce -5

room
Treasure Room of the Midgaard Catacombs
A room has been cut out of the rock walls and in the middle is a chest.~
id 47

container
a treasure chest
A heavy wooden chest, with cast-iron joints sits against the back wall.~
canOwn false

mob
a beastly kobold is here guarding the treasure
A hulking kobold is chained in place in order to protect the treasures in the mine shaft.~
race kobold, level 20, name a beastly kobold
hp 75
#dodge, second attack, third attack, trip
