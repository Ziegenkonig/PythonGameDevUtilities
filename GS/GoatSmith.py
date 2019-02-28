import tdl
import math
import textwrap
from random import randint
from random import randrange
from Rooms import Rect
from Rooms import Circle
from Rooms import HTunnel
from Rooms import VTunnel
from GameSettings import *
from Items import *

####################################################################################

####################################################################################
#Classes
####################################################################################

class GameObject:
	#this is a generic object: the player, a monster, an item, the stairs...
	#it's always represented by a character on screen.
	def __init__(self, x, y, char, name, color, blocks=False, fighter=None, ai=None, item=None):
		self.name = name
		self.blocks = blocks

		self.x = x
		self.y = y
		self.char = char
		self.color = color

		self.fighter = fighter
		if self.fighter:  #let the fighter component know who owns it
			self.fighter.owner = self
 
		self.ai = ai
		if self.ai:  #let the AI component know who owns it
			self.ai.owner = self

		self.item = item
		if self.item:  #let the Item component know who owns it
			self.item.owner = self 
 
	def move(self, dx, dy):
		#move by the given amount
		if not is_blocked(self.x + dx, self.y + dy):
			self.x += dx
			self.y += dy
 
	def move_towards(self, target_x, target_y):
		#vector from this object to the target, and distance
		dx = target_x - self.x
		dy = target_y - self.y
		distance = math.sqrt(dx ** 2 + dy ** 2)
 
		#normalize it to length 1 (preserving direction), then round it and
		#convert to integer so the movement is restricted to the map grid
		dx = int(round(dx / distance))
		dy = int(round(dy / distance))
		self.move(dx, dy)

	def distance_to(self, other):
		#return the distance to another object
		dx = other.x - self.x
		dy = other.y - self.y
		return math.sqrt(dx ** 2 + dy ** 2)

	def draw(self):
		#draw the character that represents this object at its position
		if FOG_OF_WAR:
			if (self.x, self.y) in visible_tiles:
				con.draw_char(self.x, self.y, self.char, self.color)
		else:
			con.draw_char(self.x, self.y, self.char, self.color)
 
	def clear(self):
		#erase the character that represents this object
		con.draw_char(self.x, self.y, ' ', self.color, bg=None)

	def send_to_back(self):
		#make this object be drawn first, so all others appear above it if they're in the same tile.
		global objects
		objects.remove(self)
		objects.insert(0, self)


class Fighter:
	#combat-related properties and methods (monster, player, NPC).
	def __init__(self, hp, defense, power, death_function=None):
		self.max_hp = hp
		self.hp = hp
		self.defense = defense
		self.power = power
		self.death_function = death_function

	def take_damage(self, damage):
		#apply damage if possible
		if damage > 0:
			self.hp -= damage
		#check for death. if there's a death function, call it
		if self.hp <= 0:
			function = self.death_function
			if function is not None:
				function(self.owner)

	def attack(self, target):
		#a simple formula for attack damage
		damage = self.power - target.fighter.defense
 
		if damage > 0:
			#make the target take some damage
			message(self.owner.name.capitalize() + ' attacks ' + target.name + ' for ' + str(damage) + ' hit points.')
			target.fighter.take_damage(damage)
		else:
			message(self.owner.name.capitalize() + ' attacks ' + target.name + ' but it has no effect!')


class BasicMonster:
	#AI for a basic monster.
	def take_turn(self):
		#a basic monster takes its turn. If you can see it, it can see you
		monster = self.owner
		if (monster.x, monster.y) in visible_tiles:
 
			#move towards player if far away
			if monster.distance_to(player) >= 2:
				monster.move_towards(player.x, player.y)
 
			#close enough, attack! (if the player is still alive.)
			elif player.fighter.hp > 0:
				monster.fighter.attack(player)


class Tile:
	#a tile of the map and its properties
	def __init__(self, blocked, block_sight = None):
		self.blocked = blocked
 
		self.tunnel = False

		#by default, if a tile is blocked, it also blocks sight
		if block_sight is None: block_sight = blocked
		self.block_sight = block_sight

		self.explored = False

####################################################################################

####################################################################################
#Misc
####################################################################################

def center(self):
	center_x = (self.x1 + self.x2) // 2
	center_y = (self.y1 + self.y2) // 2
	return (center_x, center_y)


def intersect(self, other):
	#returns true if this rectangle intersects with another one
	return (self.x1 <= other.x2 and self.x2 >= other.x1 and
			self.y1 <= other.y2 and self.y2 >= other.y1)


def create_floor(x, y):
	my_map[x][y].blocked = False
	my_map[x][y].block_sight = False


def is_blocked(x, y):
	#first test the map tile
	if my_map[x][y].blocked:
		return True
 
	#now check for any blocking objects
	for obj in objects:
		if obj.blocks and obj.x == x and obj.y == y:
			return True
 
	return False

def player_death(player):
		#the game ended!
		global game_state
		message('You died!')
		game_state = 'dead'
	 
		#for added effect, transform the player into a corpse!
		player.char = '%'
		player.color = (255,255,255)
 
def monster_death(monster):
	#transform it into a nasty corpse! it doesn't block, can't be
	#attacked and doesn't move
	message(monster.name.capitalize() + ' is dead!')
	monster.char = '%'
	monster.color = (255,255,255)
	monster.blocks = False
	monster.fighter = None
	monster.ai = None
	monster.name = 'remains of ' + monster.name
	monster.send_to_back()
 
####################################################################################

####################################################################################
#Create/Fill Rooms
####################################################################################

#Decides which create_room function to use
def create_room(room):

	if isinstance(room, Rect):
		create_basic_room(room)
	elif isinstance(room, Circle):
		create_enchant_room(room)


def fill_room(room):

	if isinstance(room, Rect):
		fill_basic_room(room)
	elif isinstance(room, Circle):
		fill_enchant_room(room)


def create_basic_room(room):
	global my_map
	#go through the tiles in the rectangle and make them passable
	for x in range(room.x1 + 1, room.x2):
		for y in range(room.y1 + 1, room.y2):
			my_map[x][y].block_sight = False

def fill_basic_room(room):
	global my_map

	for x in range(room.x1 + 1, room.x2):
		for y in range(room.y1 + 1, room.y2):
			my_map[x][y].blocked = False


def create_enchant_room(room):
	global my_map

	#Begin Midpoint Circle Algorithm
	#Origin
	y0 = room.center_y
	x0 = room.center_x
	#
	radius = room.r;
	f = 1 - radius
	#
	ddf_x = x0+1
	ddf_y = -2 * radius
	#Starting Point
	origin_x = room.center_x
	x = 0
	y = room.r

	create_circ_tunnel(x0 + radius, x0 - radius, y0)
	while x < y:
		if f >= origin_x: 
			y -= 1
			ddf_y += 2
			f += ddf_y
		x += 1
		ddf_x += 2
		f += ddf_x   

		create_circ_tunnel(x0 + x, x0 - x, y0 + y)
		create_circ_tunnel(x0 + x, x0 - x, y0 - y)
		create_circ_tunnel(x0 + y, x0 - y, y0 + x)
		create_circ_tunnel(x0 + y, x0 - y, y0 - x)

def fill_enchant_room(room):
	global my_map

	#Begin Midpoint Circle Algorithm
	#Origin
	y0 = room.center_y
	x0 = room.center_x
	#
	radius = room.r;
	f = 1 - radius
	#
	ddf_x = x0+1
	ddf_y = -2 * radius
	#Starting Point
	origin_x = room.center_x
	x = 0
	y = room.r

	fill_circ_tunnel(x0 + radius, x0 - radius, y0)
	while x < y:
		if f >= origin_x: 
			y -= 1
			ddf_y += 2
			f += ddf_y
		x += 1
		ddf_x += 2
		f += ddf_x   

		fill_circ_tunnel(x0 + x, x0 - x, y0 + y)
		fill_circ_tunnel(x0 + x, x0 - x, y0 - y)
		fill_circ_tunnel(x0 + y, x0 - y, y0 + x)
		fill_circ_tunnel(x0 + y, x0 - y, y0 - x)
		

#creates horizontal tunnel
def create_h_tunnel(x1, x2, y):
	global my_map
	for x in range(min(x1, x2), max(x1, x2) + 1):
		my_map[x][y].blocked = False
		my_map[x][y].block_sight = False
		my_map[x][y].tunnel = True

def create_circ_tunnel(x1, x2, y):
	global my_map
	for x in range(min(x1, x2), max(x1, x2) + 1):
		my_map[x][y].block_sight = False
		my_map[x][y].tunnel = True

def fill_circ_tunnel(x1, x2, y):
	global my_map
	for x in range(min(x1, x2), max(x1, x2) + 1):
		my_map[x][y].blocked = False


#creates vertical tunnel
def create_v_tunnel(y1, y2, x):
	global my_map
	#vertical tunnel
	for y in range(min(y1, y2), max(y1, y2) + 1):
		my_map[x][y].blocked = False
		my_map[x][y].block_sight = False
		my_map[x][y].tunnel = True

####################################################################################

####################################################################################
#Make Map and Related Functions
####################################################################################


def make_map():
	global my_map
 
	#fill map with "blocked" tiles
	my_map = [[ Tile(True)
		for y in range(MAP_HEIGHT) ]
			for x in range(MAP_WIDTH) ]
	
	rooms = []
	num_rooms = 0


	for r in range(MAX_ROOMS):
		
		#Create new room
		new_room = decideRoomType()

		#Checks for intersections and axis conflictions
		failed = isValidRoom(new_room, rooms)
 
		if not failed:
			#this means there are no intersections, so this room is valid
 
			#"paint" it to the map's tiles
			create_room(new_room)
 
			#center coordinates of new room, will be useful later
			(new_x, new_y) = new_room.center()
 
			if num_rooms == 0:
				#this is the first room, where the player starts at
				player.x = new_x
				player.y = new_y
 
			else:
				#all rooms after the first:
				#connect it to the previous room with a tunnel
 
				#center coordinates of previous room
				prev_room = rooms[num_rooms-1]
				(prev_x, prev_y) = prev_room.center()

				#pathfinding for the new tunnel, also draws the tunnel
				tunnel_pathfind(prev_x, prev_y, new_x, new_y, new_room, prev_room)

				#Fill previous room so that it is no longer a valid path to take for tunnels
				fill_room(prev_room)
				place_objects(prev_room)

			#finally, append the new room to the list
			rooms.append(new_room)
			num_rooms += 1
			if r == MAX_ROOMS-1:
				fill_room(new_room)

#Decides which room type to make randomly, returns a room
def decideRoomType():
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
def isValidRoom(new_room, rooms):
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

####################################################################################

####################################################################################
#Tunnel Pathfinding
####################################################################################

#Used in tunnel_pathfind AStar instantiation, determines what blocks can be traversed by tunnels
def cost_to_move(x, y):
	if my_map[x][y].blocked == False and my_map[x][y].tunnel != True:
		return 0.0;
	else:
		return 1.0;

def tunnel_pathfind(x1, y1, x2, y2, room1, room2):

	x = x1
	y = y1

	tunnel_search = tdl.map.AStar(MAP_WIDTH, MAP_HEIGHT, cost_to_move, 0.0)

	tunnel_path = tunnel_search.get_path(x1, y1, x2, y2)

	tunnel_path.insert(0, (x1, y1))
	draw_tunnels(tunnel_path) 

	#Disable draw_tunnels, enable this to turn tunnels into spaghetti
	# for tile in tunnel_path:
	# 	my_map[tile[0]][tile[1]].blocked = False
	# 	my_map[tile[0]][tile[1]].block_sight = False

def draw_tunnels(path):
	
	if len(path) > 0:
		initial_point = path[0]
		final_point = path[len(path)-1]

		if randint(0,1):
			create_v_tunnel(initial_point[1], final_point[1], initial_point[0])
			create_h_tunnel(initial_point[0], final_point[0], final_point[1])
		else:
			create_h_tunnel(initial_point[0], final_point[0], initial_point[1])
			create_v_tunnel(initial_point[1], final_point[1], final_point[0])

####################################################################################

####################################################################################
#Enemy / Object Placement
####################################################################################

def place_objects(room):
	#choose random number of monsters
	num_monsters = randint(0, MAX_ROOM_MONSTERS)

	for i in range(num_monsters):
		#choose random spot for this monster
		x = randint(room.x1, room.x2)
		y = randint(room.y1, room.y2)
		
		if not is_blocked(x, y):
			if randint(0, 100) < 80:  #80% chance of getting an orc
				#create an orc
				fighter_component = Fighter(hp=10, defense=0, power=3, death_function=monster_death)
				ai_component = BasicMonster()
 
				monster = GameObject(x, y, 'o', 'orc', (66, 134, 244),
					blocks=True, fighter=fighter_component, ai=ai_component)
			else:
				#create a troll
				fighter_component = Fighter(hp=16, defense=1, power=4, death_function=monster_death)
				ai_component = BasicMonster()
 
				monster = GameObject(x, y, 'T', 'troll', (187, 65, 244),
					blocks=True, fighter=fighter_component, ai=ai_component)
 
			objects.append(monster)

	#choose random number of items
	num_items = randint(0, MAX_ROOM_ITEMS)
 
	for i in range(num_items):
		#choose random spot for this item
		x = randint(room.x1+1, room.x2-1)
		y = randint(room.y1+1, room.y2-1)
 
		#only place it if the tile is not blocked
		if not is_blocked(x, y):
			#create a healing potion
			item_component = Item()
			item = GameObject(x, y, '!', 'healing potion', (255,0,0), item=item_component)
 
			objects.append(item)
			item.send_to_back()  #items appear below other objects

####################################################################################

####################################################################################
#FOV / Rendering / Key Handling
####################################################################################

def is_visible_tile(x, y):
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

def render_all():
	global fov_recompute, visible_tiles

	if fov_recompute and FOG_OF_WAR:
		#recompute FOV if needed (the player moved or something)
		fov_recompute = False
		visible_tiles = tdl.map.quickFOV(player.x, player.y,
										 is_visible_tile,
										 fov=FOV_ALGO,
										 radius=TORCH_RADIUS,
										 lightWalls=FOV_LIGHT_WALLS)

		#go through all tiles, and set their background color according to the FOV
		for y in range(MAP_HEIGHT):
			for x in range(MAP_WIDTH):
				visible = (x, y) in visible_tiles
				wall = my_map[x][y].block_sight
				if not visible:
					if my_map[x][y].explored:
						#it's out of the player's FOV
						if wall:
							con.draw_char(x, y, None, fg=None, bg=color_dark_wall)
						else:
							con.draw_char(x, y, None, fg=None, bg=color_dark_ground)
				else:
					#it's visible
					if wall:
						con.draw_char(x, y, None, fg=None, bg=color_light_wall)
						my_map[x][y].explored = True
					else:
						con.draw_char(x, y, None, fg=None, bg=color_light_ground)
					my_map[x][y].explored = True
	#For debugging purposes, disables the fog of war
	else:
		visible_tiles = tdl.map.quickFOV(player.x, player.y,
										 is_visible_tile,
										 fov=FOV_ALGO,
										 radius=TORCH_RADIUS,
										 lightWalls=FOV_LIGHT_WALLS)

		for x in range(MAP_WIDTH):
			for y in range(MAP_HEIGHT):
				wall = my_map[x][y].block_sight
				if wall:
					con.draw_char(x, y, None, fg=None, bg=color_dark_wall)
				else:
					con.draw_char(x, y, None, fg=None, bg=color_dark_ground)


	#draw all objects in the list
	for obj in objects:
		if obj != player:
			obj.draw()
	player.draw()
 
	#blit the contents of "con" to the root console and present it
	root.blit(con, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0)

	#prepare to render the GUI panel
	panel.clear(fg=(255,255,255), bg=(0,0,0))

	#show the player's stats
	render_bar(1, 1, BAR_WIDTH, 'HP', player.fighter.hp, player.fighter.max_hp,(255,255,255), (255,0,0))

	#display names of objects under the mouse
	panel.draw_str(1, 4, 'Examining:', bg=None, fg=(255,255,255))
	panel.draw_str(2, 5, get_names_under_mouse(), bg=None, fg=(255,255,255))

	#blit the contents of "panel" to the root console
	root.blit(panel, 0, PANEL_Y, SCREEN_WIDTH, PANEL_HEIGHT, 0, 0)


def handle_keys():
	global playerx, playery, fov_recompute, mouse_coord
 
	keypress = False
	for event in tdl.event.get():
		if event.type == 'KEYDOWN':
			user_input = event
			keypress = True
		if event.type == 'MOUSEMOTION':
			mouse_coord = event.cell
 
	if not keypress:
		return 'didnt-take-turn' 
 
	if game_state == 'playing':
		#movement keys
		if user_input.key == 'UP':
			player_move_or_attack(0, -1)
			fov_recompute = True

		elif user_input.key == 'DOWN':
			player_move_or_attack(0, 1)
			fov_recompute = True

		elif user_input.key == 'LEFT':
			player_move_or_attack(-1, 0)
			fov_recompute = True

		elif user_input.key == 'RIGHT':
			player_move_or_attack(1, 0)
			fov_recompute = True

		elif user_input.key == 'ENTER' and user_input.alt:
			#Alt+Enter: toggle fullscreen
			tdl.set_fullscreen(not tdl.get_fullscreen())

		elif user_input.key == 'ESCAPE':
			return 'exit'  #exit game

		elif user_input.text == 'g':
			#pick up an item
			for obj in objects:  #look for an item in the player's tile
				if obj.x == player.x and obj.y == player.y and obj.item:
					obj.item.pick_up(message, inventory, objects)
					break;
		elif user_input.text == 'i':
			#show the inventory
			inventory_menu('Press the key next to an item to use it, or any other to cancel.\n')

		else:
 
			return 'didnt-take-turn'


def get_names_under_mouse():
	global visible_tiles
 
	#return a string with the names of all objects under the mouse
	(x, y) = mouse_coord

	#create a list with the names of all objects at the mouse's coordinates and in FOV
	names = [obj.name for obj in objects
		if obj.x == x and obj.y == y and (obj.x, obj.y) in visible_tiles]

	names = ', '.join(names)  #join the names, separated by commas
	return names.capitalize()


#Determines whether player moves or attacks, who woulda thunk it
def player_move_or_attack(dx, dy):
	global fov_recompute
 
	#the coordinates the player is moving to/attacking
	x = player.x + dx
	y = player.y + dy
 
	#try to find an attackable object there
	target = None
	for obj in objects:
		if obj.fighter and obj.x == x and obj.y == y:
			target = obj
			break
 
	#attack if target found, move otherwise
	if target is not None:
		player.fighter.attack(target)
	else:
		player.move(dx, dy)
		fov_recompute = True


def render_bar(x, y, total_width, name, value, maximum, bar_color, back_color):
	#render a bar (HP, experience, etc). first calculate the width of the bar
	bar_width = int(float(value) / maximum * total_width)
 
	#render the background first
	panel.draw_rect(x, y, total_width, 1, None, bg=back_color)
 
	#now render the bar on top
	if bar_width > 0:
		panel.draw_rect(x, y, bar_width, 1, None, bg=bar_color)

	#finally, some centered text with the values
	text = name + ': ' + str(value) + '/' + str(maximum)
	x_centered = x + (total_width-len(text))//2
	panel.draw_str(x_centered, y, text, fg=(0,0,0), bg=None)

	y = 1
	for (line, color) in game_msgs:
		panel.draw_str(MSG_X, y, line, bg=None, fg=color)
		y += 1

def message(new_msg, color = (255,255,255)):
	#split the message if necessary, among multiple lines
	new_msg_lines = textwrap.wrap(new_msg, MSG_WIDTH)
 
	for line in new_msg_lines:
		#if the buffer is full, remove the first line to make room for the new one
		if len(game_msgs) == MSG_HEIGHT:
			del game_msgs[0]
 
		#add the new line as a tuple, with the text and the color
		game_msgs.append((line, color))
		#print the game messages, one line at a time


def menu(header, options, width):
	if len(options) > 26: raise ValueError('Cannot have a menu with more than 26 options.')

	#calculate total height for the header (after textwrap) and one line per option
	header_wrapped = []
	for header_line in header.splitlines():
		header_wrapped.extend(textwrap.wrap(header_line, width))
	header_height = len(header_wrapped)
	height = len(options) + header_height

	#create an off-screen console that represents the menu's window
	window = tdl.Console(width, height)
 
	#print the header, with wrapped text
	window.draw_rect(0, 0, width, height, None, fg=(255,255,255), bg=None)
	for i, line in enumerate(header_wrapped):
		window.draw_str(0, 0+i, header_wrapped[i])

	y = header_height
	letter_index = ord('a')
	for option_text in options:
		text = '(' + chr(letter_index) + ') ' + option_text
		window.draw_str(0, y, text, bg=None)
		y += 1
		letter_index += 1

	#blit the contents of "window" to the root console
	x = SCREEN_WIDTH//2 - width//2
	y = SCREEN_HEIGHT//2 - height//2
	root.blit(window, x, y, width, height, 0, 0)

	#present the root console to the player and wait for a key-press
	tdl.flush()
	key = tdl.event.key_wait()
	key_char = key.char
	if key_char == '':
		key_char = ' ' # placeholder

def inventory_menu(header):
	#show a menu with each item of the inventory as an option
	if len(inventory) == 0:
		options = ['Inventory is empty.']
	else:
		options = [item.name for item in inventory]
 
	index = menu(header, options, INVENTORY_WIDTH)

####################################################################################

####################################################################################
#INITIALIZATION
####################################################################################
root = tdl.init(SCREEN_WIDTH, SCREEN_HEIGHT, title="Droid-Smith", fullscreen=False)
con = tdl.Console(SCREEN_WIDTH, SCREEN_HEIGHT)
panel = tdl.Console(SCREEN_WIDTH, PANEL_HEIGHT)

fighter_component = Fighter(hp=30, defense=2, power=5, death_function=player_death)
player = GameObject(0, 0, '@', 'player', (255,255,255), blocks=True, fighter=fighter_component)
objects = [player]

#player starting position
player.x = 25
player.y = 23

make_map();

#a warm welcoming message!
message('Welcome!')

mouse_coord = (0, 0)

inventory = []

while not tdl.event.is_window_closed():
	render_all();
	
	tdl.flush()

	#Clear all objects each move
	for obj in objects:
		obj.clear()

	#handle keys and exit game if needed
	player_action = handle_keys()
	if player_action == 'exit':
		break;
	#let monsters take their turn
	if game_state == 'playing' and player_action != 'didnt-take-turn':
		for obj in objects:
			if obj.ai:
				obj.ai.take_turn()

####################################################################################