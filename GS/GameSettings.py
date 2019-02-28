#This file is solely for game settings that need to be made available to all classes/functions in the game

SCREEN_WIDTH = 100
SCREEN_HEIGHT = 75
LIMIT_FPS = 20

playerx = SCREEN_WIDTH//2
playery = SCREEN_HEIGHT//2

MAP_WIDTH = 100
MAP_HEIGHT = 70
color_dark_wall = (0, 0, 100)
color_dark_ground = (50, 50, 150)

ROOM_RECT_MAX_SIZE = 12
ROOM_RECT_MIN_SIZE = 6
ROOM_CIRC_MAX_SIZE = 5
ROOM_CIRC_MIN_SIZE = 3
MAX_ROOMS = 500

FOG_OF_WAR = False
FOV_ALGO = 'PERMISSIVE'  #default FOV algorithm
FOV_LIGHT_WALLS = True
TORCH_RADIUS = 10

color_dark_wall = (0, 0, 100)
color_light_wall = (130, 110, 50)
color_dark_ground = (50, 50, 150)
color_light_ground = (200, 180, 50)

objects = []

MAX_ROOM_MONSTERS = 3
MAX_ROOM_ITEMS = 1

fov_recompute = True

game_state = 'playing'
player_action = None

#sizes and coordinates relevant for the GUI
BAR_WIDTH = 20
PANEL_HEIGHT = 7
PANEL_Y = SCREEN_HEIGHT - PANEL_HEIGHT

MSG_X = BAR_WIDTH + 2
MSG_WIDTH = SCREEN_WIDTH - BAR_WIDTH - 2
MSG_HEIGHT = PANEL_HEIGHT - 1		

#create the list of game messages and their colors, starts empty
game_msgs = []

INVENTORY_WIDTH = 50