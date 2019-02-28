import tdl
from random import randint

#Contains all the functions required for generating rooms
class RoomGenerator:

	def __init__(self, my_map):
		self.my_map = my_map

	#Decides which create_room function to use
	def create_room(self, room):

		if isinstance(room, Rect):
			self.create_basic_room(room)
		elif isinstance(room, Circle):
			self.create_enchant_room(room)


	def fill_room(self, room):

		if isinstance(room, Rect):
			self.fill_basic_room(room)
		elif isinstance(room, Circle):
			self.fill_enchant_room(room)


	def create_basic_room(self, room):
		global my_map
		#go through the tiles in the rectangle and make them passable
		for x in range(room.x1 + 1, room.x2):
			for y in range(room.y1 + 1, room.y2):
				self.my_map[x][y].block_sight = False


	def fill_basic_room(self, room):
		global my_map

		for x in range(room.x1 + 1, room.x2):
			for y in range(room.y1 + 1, room.y2):
				self.my_map[x][y].blocked = False


	def create_enchant_room(self, room):
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

		self.create_circ_tunnel(x0 + radius, x0 - radius, y0)
		while x < y:
			if f >= origin_x: 
				y -= 1
				ddf_y += 2
				f += ddf_y
			x += 1
			ddf_x += 2
			f += ddf_x   

			self.create_circ_tunnel(x0 + x, x0 - x, y0 + y)
			self.create_circ_tunnel(x0 + x, x0 - x, y0 - y)
			self.create_circ_tunnel(x0 + y, x0 - y, y0 + x)
			self.create_circ_tunnel(x0 + y, x0 - y, y0 - x)


	def fill_enchant_room(self, room):
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

		self.fill_circ_tunnel(x0 + radius, x0 - radius, y0)
		while x < y:
			if f >= origin_x: 
				y -= 1
				ddf_y += 2
				f += ddf_y
			x += 1
			ddf_x += 2
			f += ddf_x   

			self.fill_circ_tunnel(x0 + x, x0 - x, y0 + y)
			self.fill_circ_tunnel(x0 + x, x0 - x, y0 - y)
			self.fill_circ_tunnel(x0 + y, x0 - y, y0 + x)
			self.fill_circ_tunnel(x0 + y, x0 - y, y0 - x)
			

	#creates horizontal tunnel
	def create_h_tunnel(self, x1, x2, y):
		global my_map
		for x in range(min(x1, x2), max(x1, x2) + 1):
			self.my_map[x][y].blocked = False
			self.my_map[x][y].block_sight = False
			self.my_map[x][y].tunnel = True


	def create_circ_tunnel(self, x1, x2, y):
		global my_map
		for x in range(min(x1, x2), max(x1, x2) + 1):
			self.my_map[x][y].block_sight = False
			self.my_map[x][y].tunnel = True


	def fill_circ_tunnel(self, x1, x2, y):
		global my_map
		for x in range(min(x1, x2), max(x1, x2) + 1):
			self.my_map[x][y].blocked = False


	#creates vertical tunnel
	def create_v_tunnel(self, y1, y2, x):
		global my_map
		#vertical tunnel
		for y in range(min(y1, y2), max(y1, y2) + 1):
			self.my_map[x][y].blocked = False
			self.my_map[x][y].block_sight = False
			self.my_map[x][y].tunnel = True

	def draw_tunnels(self, path):
		
		if len(path) > 0:
			initial_point = path[0]
			final_point = path[len(path)-1]

			print('Started At: (' + str(initial_point[0]) + ', ' + str(initial_point[1]) + ')')
			print('Ended At: (' + str(final_point[0]) + ', ' + str(final_point[1]) + ')')

			if randint(0,1):
				self.create_v_tunnel(initial_point[1], final_point[1], initial_point[0])
				self.create_h_tunnel(initial_point[0], final_point[0], final_point[1])
			else:
				self.create_h_tunnel(initial_point[0], final_point[0], initial_point[1])
				self.create_v_tunnel(initial_point[1], final_point[1], final_point[0])

class HTunnel:
	#a rectangle on the map. used to characterize a room.
	def __init__(self, x1, x2, y):
		self.x1 = x1
		self.y1 = y
		self.x2 = x2
		self.y2 = y
 
	def center(self):
		center_x = (self.x1 + self.x2) // 2
		center_y = (self.y1 + self.y2) // 2
		return (center_x, center_y)
 
	def intersect(self, other):
		#returns true if this rectangle intersects with another one
		return (self.x1 <= other.x2 and self.x2 >= other.x1 and
				self.y1 <= other.y2 and self.y2 >= other.y1)

class VTunnel:
	#a rectangle on the map. used to characterize a room.
	def __init__(self, x, y1, y2):
		self.x1 = x
		self.y1 = y1
		self.x2 = x
		self.y2 = y2
 
	def center(self):
		center_x = (self.x1 + self.x2) // 2
		center_y = (self.y1 + self.y2) // 2
		return (center_x, center_y)
 
	def intersect(self, other):
		#returns true if this rectangle intersects with another one
		return (self.x1 <= other.x2 and self.x2 >= other.x1 and
				self.y1 <= other.y2 and self.y2 >= other.y1)


class Rect:
	#a rectangle on the map. used to characterize a room.
	def __init__(self, x, y, w, h):
		self.x1 = x
		self.y1 = y
		self.x2 = x + w
		self.y2 = y + h
		self.w = w
		self.h = h
 
	def center(self):
		center_x = (self.x1 + self.x2) // 2
		center_y = (self.y1 + self.y2) // 2
		return (center_x, center_y)

	def dist_from_center_x(self):
		return self.x2 - self.x1

	def dist_from_center_y(self):
		return self.y2 - self.y1
 
	def intersect(self, other):
		#returns true if this rectangle intersects with another one
		return (self.x1 <= other.x2 and self.x2 >= other.x1 and
				self.y1 <= other.y2 and self.y2 >= other.y1)

class Circle:
	#a circle on the map. used to characterize a room.
	def __init__(self, x, y, r):
		self.center_x 	= x
		self.center_y 	= y
		self.x1 		= x - r
		self.y1 		= y - r
		self.x2			= x + r
		self.y2			= y + r
		self.r 			= r
		self.w 			= r*2+2
		self.h 			= r*2+2
		
	def center(self):
		return (self.center_x, self.center_y)

	def dist_from_center_x(self):
		return self.r

	def dist_from_center_y(self):
		return self.r

	def intersect(self, other):
		#returns true if this circle intersects with another object
		return (self.x1 <= other.x2+1 and self.x2 >= other.x1-1 and
				self.y1 <= other.y2+1 and self.y2 >= other.y1-1)


