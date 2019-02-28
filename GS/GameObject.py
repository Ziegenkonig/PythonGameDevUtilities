class GameObject:
	#this is a generic object: the player, a monster, an item, the stairs...
	#it's always represented by a character on screen.
	def __init__(self, x, y, char, color, map_gen, con):
		self.x = x
		self.y = y
		self.char = char
		self.color = color
		self.map_gen = map_gen
		self.con = con
 
	def move(self, dx, dy):
		#move by the given amount
		if not self.map_gen.getMyMap()[self.x + dx][self.y + dy].blocked:
			self.x += dx
			self.y += dy
 
	def draw(self):
		#draw the character that represents this object at its position
		if (self.x, self.y) in self.map_gen.getVisibleTiles():
			self.con.draw_char(self.x, self.y, self.char, self.color)
 
	def clear(self):
		#erase the character that represents this object
		self.con.draw_char(self.x, self.y, ' ', self.color, bg=None)