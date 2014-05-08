import os, sys, pygame, math
from Player import Player

def main():
	# basic init
	os.environ['SDL_VIDEO_CENTERED'] = '1'
	pygame.init()

	# general vars
	white = 255, 255, 255
	black = 0, 0, 0
	size = width, height = 640, 480
	screen = pygame.display.set_mode(size)
	view = screen.get_rect()
	clock = pygame.time.Clock()
	buf = pygame.Surface(size, pygame.SRCALPHA, 32)

	# game elements
	player = Player(320, 200, 32, 32)
	levelcolor = pygame.image.load('background3.png')
	levelcolor = levelcolor.convert_alpha()
	levelgray = grayscale('background3.png')
	level = levelcolor.get_rect()
	pxa_color = pygame.PixelArray(levelcolor)

	# optimize images
	Player.img = Player.img.convert_alpha()

	# mouse cursor
	pygame.mouse.set_cursor(*pygame.cursors.broken_x)

	# game loop
	while True:

		# quit on window close or escape key
		for event in pygame.event.get():
			if event.type == pygame.QUIT \
			   or (event.type == pygame.KEYDOWN \
			   and event.key == pygame.K_ESCAPE):
				pygame.quit()
				sys.exit()

		# create pixel array of individual pixels
		pxa_gray  = pygame.PixelArray(levelgray)

		handleKeys(player, level, pxa_color)
		handleMouse(player, view, pxa_color, pxa_gray)
		updateView(player, level, view)

		'''
		# blit onto smaller colorbuf
		colorbuf.fill(0) # clear the buffer
		colorbuf.blit(levelcolor, (0,0), view) # copy color buf into it
		uncovercolor(colorbuf, player, view) # uncover 'seen'
		'''

		# delete pxarray to unlock surface
		del pxa_gray
			
		#draw screen
		buf.fill(black)
		buf.blit(levelgray, (0,0), view)
		colorvision(buf, pxa_color, player, view)
		player.display(buf, view)
		screen.blit(buf, (0,0))
		pygame.display.flip()

		#do all this at 40 fps
		clock.tick(40)

def handleKeys(player, level, pxarray):
	"moves player checking alpha values for collisions"
	# the alpha channel are highest 8 bits of the 32bit color
	keys = pygame.key.get_pressed()
	horiz_center = player.left + 16
	vert_center = player.top + 16

	# shift enables run
	running = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
	player.setRun(running)

	# move left and right with array keys
	if keys[pygame.K_LEFT] and player.left > 0 and \
	  pxarray[player.left][vert_center] >> 24 < 5:
		player.moveLeft()
	if keys[pygame.K_RIGHT] and player.right < level.w and \
	  pxarray[player.right][vert_center] >> 24 < 5:
		player.moveRight()

	# space jumps only if on ground
	if player.jumping == False and keys[pygame.K_SPACE] and \
	  pxarray[horiz_center][player.bottom + 2] >> 24 > 250:
		player.jumping = True
		player.dy = -5
		player.py += player.dy
		player.y = player.py

	# stop jumping when we release space
	if not keys[pygame.K_SPACE]:
		player.jumping = False
		if player.dy < 0: # no longer holding space down
			player.dy = 0

	# stop jumping when hit the ceiling
	if pxarray[horiz_center][player.top + 2] >> 24 > 250:
		player.jumping = False
		if player.dy < 0:
			player.dy = 0
	
	#move player down or up based on (small) obstacles in pxarray
	if pxarray[horiz_center][player.bottom] >> 24 < 5: # drop if no ground
		player.py += player.dy
		player.dy += 0.33
		player.y = player.py
	else: # we're on the ground
		player.dy = 0
		# move up by walking if 16 > change > 2 (half height)
		for up in range(player.bottom - 1, player.bottom - 16, -1):
			if pxarray[horiz_center][up] >> 24 < 5:
				break
		if (player.bottom - 2) > up > (player.bottom - 16):
			player.py = up -32
			player.y = player.py

def handleMouse(player, view, pxa_color, pxa_gray):
	"handles mouse button events"
	# check mouse
	pos = pygame.mouse.get_pos()
	btn = pygame.mouse.get_pressed()
	clicked = False

	# player is 32x32, we want dx, dy from player center to mouse pos
	dx = pos[0] + view.x - player.x + 16
	dy = pos[1] + view.y - player.y + 16
	
	# find circle center (player edge)  normalize on hyp of 16px
	rad = 16
	hyp = math.hypot(dx, dy)
	div = hyp / rad
	dx = int(dx / div)
	dy = int(dy / div)
	circlex = player.x + 16 + dx
	circley = player.y + 16 + dy

	# on button 1 press we want to 'dig' by clearing the level in the 
	# direction of the mouse. We will do so by creating a semi circle 
	# with 32 diameter in the direction of the mouse, 16 px out from 
	# the player center (on player edge)
	if btn[0]:
		drawCircle(pxa_color, (circlex, circley), 16, 0)
		drawCircle(pxa_gray, (circlex, circley), 16, 0)
		clicked = True

	if btn[2]:
		drawCircle(pxa_color, (circlex, circley), 16, 0xFFFF00FF)
		drawCircle(pxa_gray, (circlex, circley), 16, 0xFFAAAAAA)
		clicked = True
		
	return clicked
					

def updateView(player, level, view):
	"keeps player in the center of the view, except at level edges"
	view.x = player.x - view.w / 2
	view.y = player.y - view.h / 2
	if view.x > level.w - view.w:
		view.x = level.w - view.w
	elif view.x < 0:
		view.x = 0
	
	if view.y > level.h - view.h:
		view.y = level.h - view.h
	elif view.y < 0:
		view.y = 0
			
def drawCircle(pxarray, pos, rad, color):
	"""Draws a circle on the pxarray, pos is expected to be a tuple with the
	x,y coordinates of the circle center. rad is the desired radius, and color
	a 32bit unsinged int holding ARGB values"""

	circlex = pos[0]
	circley = pos[1]

	# initialize circle data structure (map of lists)
	circle = {}
	for x in range(circlex - rad, circlex + rad + 1):
		circle[x] = [circley]

	# put circle outline into data structure
	y = rad
	for x in range(0, rad + 1):
		newy = int(math.sqrt(rad**2 - x**2))
		if newy != y:
			# shorter end makes it look more round
			end = newy
			if end < rad/2: end -= 1
			for y in range(y, end, -1):
				# the four quarters of the circle
				circle[circlex + x].append(circley + y) 
				circle[circlex + x].append(circley - y) 
				circle[circlex - x].append(circley + y) 
				circle[circlex - x].append(circley - y) 

	# the top and bottom pixel are not included in the outline?
	# (visual inspection showed this)
	circle[circlex].append(circley - rad)
	circle[circlex].append(circley + rad)

	# fill circle based on outline min / max
	for x in circle:
		for y in range(min(circle[x]), max(circle[x])):
			pxarray[x][y] = color
	
def grayscale(filename):
	'uses filename to load image file and return a grayscale version'
	img = pygame.image.load(filename)
	pxarray = pygame.PixelArray(img)
	rect = img.get_rect()
	mask = 0x000000FF
	for x in range(rect.w):
		for y in range(rect.h):
			color = pxarray[x][y]
			blue  = color & mask
			green = (color >> 8) & mask 
			red   = (color >> 16) & mask
			alpha = (color >> 24) & mask
			argb = 0xFFFFFFFF
			#if alpha > 128:
			gray  = int(0.299 * red + 0.587 * green + 0.114 * blue)
			argb  = (alpha << 24) + (gray << 16) + (gray << 8) + gray
			pxarray[x][y] = argb
	del pxarray
	return img

def colorvision(screen, pxa_color, player, view):
	pxa_screen = pygame.PixelArray(screen)
	pos = pygame.mouse.get_pos()

	for x in range(pos[0] - 50, pos[0] + 51):
		for y in range(pos[1] - 50, pos[1] + 51):
			pxa_screen[x][y] = pxa_color[x][y]
			
	'''
	# player is 32x32, we want dx, dy from player center to mouse pos
	dx = pos[0] + view.x - player.x + 16
	dy = pos[1] + view.y - player.y + 16

	if dx > dy:
		stepy = dy / float(dx)
		y = float(player.y + 16 - view.y)
		for x in range(player.x + 16 - view.x, pos[0]):
			pxa_screen[x][int(y)] = pxa_color[x][int(y)]
			y += stepy
	else:
		stepx = dx / float(dy)
		x = float(player.x + 16 - view.x)
		for y in range(player.y + 16 - view.y, pos[1]):
			pxa_screen[int(x)][y] = pxa_color[int(x)][y]
			x += stepx
	'''
if __name__ == '__main__': main()
