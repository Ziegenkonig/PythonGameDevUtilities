import random

empty_room = 	('_____\n' +
				 '|   |\n' +
				 '|___|')

rooms = [];


def drawRow(columns):
	row_top = ''
	row_middle = ''
	row_bottom = ''

	for columns in range(columns):
		room = Room()
		rooms.append(room)
		row_top =  row_top + '*' + room.top + '*'
		row_middle = row_middle + '*'  + room.middle + '*'
		row_bottom = row_bottom + '*'  + room.bottom + '*'
	
	print row_top
	print row_middle
	print row_bottom

def drawDungeon(grid):

	for rows in range(grid[0]):
		drawRow(grid[1])


grid = (10,10)
drawDungeon(grid)
print(str(rooms))