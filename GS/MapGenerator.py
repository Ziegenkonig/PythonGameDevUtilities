import tdl
from random import randint
from random import randrange
from GameSettings import *
from Rooms import Rect
from Rooms import Circle
from Rooms import RoomGenerator
from GameObject import *

class Tile:
	#a tile of the map and its properties
	def __init__(self, blocked, block_sight = None):
		self.blocked = blocked
 
		self.tunnel = False

		#by default, if a tile is blocked, it also blocks sight
		if block_sight is None: block_sight = blocked
		self.block_sight = block_sight

		self.explored = False


class MapGenerator:

	def __init__(self, player, console, objects, root):
		self.root = root
		self.player = player
		self.room_gen = None
		self.con = console
		self.objects = objects

		self.fov_recompute = True
		self.visible_tiles = []


	def place_objects(self, room):
	    #choose random number of monsters
	    num_monsters = randint(0, MAX_ROOM_MONSTERS)
	 
	    for i in range(num_monsters):
	        #choose random spot for this monster
	        x = randint(room.x1, room.x2)
	        y = randint(room.y1, room.y2)
	 
	        if randint(0, 100) < 80:  #80% chance of getting an orc
	            #create an orc
	            monster = GameObject(x, y, 'o', (66, 134, 244))
	        else:
	            #create a troll
	            monster = GameObject(x, y, 'T', (187, 65, 244))
	 
	        objects.append(monster)


	def getVisibleTiles(self):

		return self.visible_tiles


	def getMyMap(self):
		global my_map

		return my_map


	def render_all(self):

		if self.fov_recompute:
			#recompute FOV if needed (the player moved or something)
			self.fov_recompute = False
			self.visible_tiles = tdl.map.quickFOV(self.player.x, self.player.y,
											 self.is_visible_tile,
											 fov=FOV_ALGO,
											 radius=TORCH_RADIUS,
											 lightWalls=FOV_LIGHT_WALLS)

			#go through all tiles, and set their background color according to the FOV
	        for y in range(MAP_HEIGHT):
	            for x in range(MAP_WIDTH):
	                visible = (x, y) in self.visible_tiles
	                wall = my_map[x][y].block_sight
	                if not visible:
	                	if my_map[x][y].explored:
			                #it's out of the player's FOV
			                if wall:
			                    self.con.draw_char(x, y, None, fg=None, bg=color_dark_wall)
			                else:
			                    self.con.draw_char(x, y, None, fg=None, bg=color_dark_ground)
	                else:
	                    #it's visible
	                    if wall:
	                        self.con.draw_char(x, y, None, fg=None, bg=color_light_wall)
	                        my_map[x][y].explored = True
	                    else:
	                        self.con.draw_char(x, y, None, fg=None, bg=color_light_ground)
	                    my_map[x][y].explored = True
	 
		#draw all objects in the list
		for obj in self.objects:
			obj.draw()
	 
		#blit the contents of "con" to the root console and present it
		self.root.blit(self.con, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0)


	def is_visible_tile(self, x, y):
	    global my_map
	 
	    if x >= MAP_WIDTH or x < 0:
	        return False
	    elif y >= MAP_HEIGHT or y < 0:
	        return False
	    elif my_map[x][y].blocked == True:
	        return False
	    elif my_map[x][y].block_sight == True:
	        return False
	    else:
	        return True


	def intersect(self, other):
		#returns true if this rectangle intersects with another one
		return (self.x1 <= other.x2 and self.x2 >= other.x1 and
				self.y1 <= other.y2 and self.y2 >= other.y1)


	def create_floor(self, x, y):
		my_map[x][y].blocked = False
		my_map[x][y].block_sight = False


	#Used in tunnel_pathfind AStar instantiation, determines what blocks can be traversed by tunnels
	def cost_to_move(self, x, y):
		if my_map[x][y].blocked == False and my_map[x][y].tunnel != True:
			return 0.0;
		else:
			return 1.0;

	def tunnel_pathfind(self, x1, y1, x2, y2, room1, room2):

		x = x1
		y = y1

		tunnel_search = tdl.map.AStar(MAP_WIDTH, MAP_HEIGHT, self.cost_to_move, 0.0)

		tunnel_path = tunnel_search.get_path(x1, y1, x2, y2)

		tunnel_path.insert(0, (x1, y1))
		self.room_gen.draw_tunnels(tunnel_path) 

		#Disable draw_tunnels, enable this to turn tunnels into spaghetti
		# for tile in tunnel_path:
		# 	my_map[tile[0]][tile[1]].blocked = False
		# 	my_map[tile[0]][tile[1]].block_sight = False

	def spawnPlayer(self, coords):
		self.player.x = coords[0]
		self.player.y = coords[1]


	def make_map(self):
		global my_map
	 
		#fill map with "blocked" tiles
		my_map = [[ Tile(True)
			for y in range(MAP_HEIGHT) ]
				for x in range(MAP_WIDTH) ]
		
		self.room_gen = RoomGenerator(my_map)

		rooms = []
		num_rooms = 0


		for r in range(MAX_ROOMS):
			
			#Create new room
			new_room = self.decideRoomType()

			#Checks for intersections and axis conflictions
			failed = self.isValidRoom(new_room, rooms)
	 
			if not failed:
				#this means there are no intersections, so this room is valid
	 
				#"paint" it to the map's tiles
				self.room_gen.create_room(new_room)
	 
				#center coordinates of new room, will be useful later
				(new_x, new_y) = new_room.center()
				print('Center of Ending Room: ' + str(new_room.center()))
	 
				if num_rooms == 0:
					#this is the first room, where the player starts at
					self.spawnPlayer((new_x, new_y))
	 
				else:
					#all rooms after the first:
					#connect it to the previous room with a tunnel
	 
					#center coordinates of previous room
					prev_room = rooms[num_rooms-1]
					(prev_x, prev_y) = prev_room.center()

					#pathfinding for the new tunnel, also draws the tunnel
					self.tunnel_pathfind(prev_x, prev_y, new_x, new_y, new_room, prev_room)

					#Fill previous room so that it is no longer a valid path to take for tunnels
					self.room_gen.fill_room(prev_room)

				#finally, append the new room to the list
				rooms.append(new_room)
				self.place_objects(new_room)
				num_rooms += 1
				if r == MAX_ROOMS-1:
					print('test')
					fill_room(new_room)


	#Decides which room type to make randomly, returns a room
	def decideRoomType(self):
		#setting random room type
		room_type = randint(0, 1)
		if (room_type == 0): #Room type circle
			#random width and height
			r = randint(ROOM_CIRC_MIN_SIZE, ROOM_CIRC_MAX_SIZE)
			#random position without going out of the boundaries of the map
			x = randint( (r), MAP_WIDTH-(r*2)-1 )
			y = randint( (r), MAP_HEIGHT-(r*2)-1 )

			new_room = Circle(x, y, r)
		elif (room_type == 1): #Room type square
			#random width and height
			w = randrange(ROOM_RECT_MIN_SIZE, ROOM_RECT_MAX_SIZE, 2)
			h = randrange(ROOM_RECT_MIN_SIZE, ROOM_RECT_MAX_SIZE, 2)
			#random position without going out of the boundaries of the map
			x = randint(0, MAP_WIDTH-w-1)
			y = randint(0, MAP_HEIGHT-h-1)

			new_room = Rect(x, y, w, h)

		return new_room;

	#Returns bool to make sure there are no collisions between rooms and that there are no axis conflictions
	def isValidRoom(self, new_room, rooms):
		#run through the other rooms and see if they intersect with this one
		failed = False
		for other_room in rooms:
			#Max width that the difference could be to start being valid
			max_width 		= ( max(other_room.w, new_room.w) // 2 ) + 1
			max_height 		= ( max(other_room.h, new_room.h) // 2 ) + 1
			#Difference between the two single-axis positions
			x_difference 	= new_room.center()[0]-other_room.center()[0]
			y_difference 	= new_room.center()[1]-other_room.center()[1]
			
			#What this ugly conditional is checking, is whether or not the room shares a close single-axis proximity to another
			#This results in very clean connections between each room
			if new_room.intersect(other_room):
				failed = True
				return failed;
			elif x_difference < max_width and x_difference >= 1:
				failed = True
				return failed;
			elif x_difference > -max_width and x_difference <= -1:
				failed = True
				return failed;
			elif y_difference < max_height and y_difference >= 1:
				failed = True
				return failed;
			elif y_difference > -max_height and y_difference <= -1:
				failed = True
				return failed;

