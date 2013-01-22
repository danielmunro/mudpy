area
name Adelwine Manor, terrain city, location indoors

#########################
# Main floor
#########################

room
Adelwine Manor Foyer
Large windows in the arching foyer of the Adelwine manor let in some of the only light in the abandoned building. From here you can see a hall leading north, and it looks like there is movement but it's impossible to see anything.~
id 32, s midgaard:20, n 33

mob
a ghost of a servant boy is floating around
A ghost of a servant boy is here, looking for something useful to do.~
race human, movement_timeout 3, level 8, name a ghost of a servant boy, alignment -1000
hp 10

key
a brass key
A tarnished brass key is here.~
level 3, door_id 1

room
Adelwine Manor Sitting Room
Portraits of the previous owners of Adelwine Manor hang on the wall. Badly aged and decayed, their condition is a stark reminder of the age of the manor. The hallway has opened up to a sitting room, with a staircase leading up, presumably to the bedrooms.~
id 33, s 32, n 36, w 34, e 35

room
Sitting Room
A record player is set against crumblinging walls in this part of the room. It looks like there is a small pantry to the west.~
id 34, e 33, n 37, w 39

item
a decrepit record player
A very old, and very broken looking record player is set against the wall.~
canOwn false

mob
a ghost of a servant boy is floating around
A ghost of a servant boy is here, looking for something useful to do.~
race human, level 8, movement_timeout 3, name a ghost of a servant boy
hp 10

room
Sitting Room
This part of the room is too dark to make out any details.~
id 35, w 33, n 38

room 
Sitting Room
You are greeted by an empty room, with a window on the wall and a single chair in it. The chair is covered in a cloth.~
id 36, s 33, w 37, e 38

furniture
a leather bound chair
A leather bound chair is here, covered by a white linen cloth.~
material leather, regen .2

mob
a ghost of a servant boy is floating around
A ghost of a servant boy is here, looking for something useful to do.~
movement_timeout 3, level 8, race human, name a ghost of a servant boy
hp 10

room
Sitting Room
A boarded up window allows just enough light through to see severe damage to the flooring and walls.~
id 37, s 34, e 36

room
Sitting Room
This part of the room is empty except for a couch with a linen sheet over it.~
id 38, w 36, s 35

furniture
a leather bound couch
A leather bound couch is here, covered by a white linen sheet.~
canOwn false, material leather

mob
a ghost of a servant boy is floating around
A ghost of a servant boy is here, looking for something useful to do.~
movement_timeout 3, level 8, race human, name a ghost of a servant boy
hp 10

room
A small pantry
The pantry is loaded with food that has long gone bad. A stairway leads to the attic.~
id 39, e 34, u 40, d Midgaard Catacombs:45

food
a molded mushroom
A foul smelling mushroom seem to be left here from long ago.~
nourishment 0, value 1, level 5

#poison
#timeout 3~

mob
a ghost of a servant boy is floating around
A ghost of a servant boy is here, looking for something useful to do.~
movement_timeout 3, level 8, race human, name a ghost of a servant boy
hp 10

#
# Attic
#

room
Attic of Adelwine Manor
A narrow and dark hallway is here. It's hard to discern any details.~
id 40, d 39, n 41

mob
a ghost of Adelwine manor wanders here
A ghost of Adelwine manor is here, wandering the halls in the attic.~
movement_timeout 3, level 12, race human, name a ghost of Adelwine manor
hp 25

room
Attic of Adelwine Manor
You are surrounded by a narrow and dark hallway.~
id 41, s 40, w 42

door
a creaky wooden door
There is a creaky wooden door here.~
id 1, disposition locked

room
Attic of Adelwine Manor
A narrow dark hallway is here.~
id 42, e 41, w 43, door w 1

room
A Small Room in the Back of the Attic
A small room in the back of Adelwine manor attic is here.~
id 43, e 42, door e 1

room
A Musty Cellar
An old wooden staircase leads down a narrow passage. The slate gray rock walls are cool to the touch.~
id 44, u 39, d Midgaard Catacombs:45
#id 44, u 39, d 45, e 100~
