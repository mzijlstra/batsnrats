import os, sys, pygame, math

def main():
	# basic init
	os.environ['SDL_VIDEO_CENTERED'] = '1'
	pygame.init()

	# general vars
	white = 255, 255, 255
	size = width, height = 640, 480
	screen = pygame.display.set_mode(size)
	level = pygame.Surface((width, height))
	view = screen.get_rect()
	clock = pygame.time.Clock()

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

		level.fill(white)
		# create pixel array of individual pixels
		pxarray = pygame.PixelArray(level)
		drawSemi(pxarray)
		level = pxarray.make_surface()

		# delete pxarray to unlock surface
		del pxarray
			
		#draw screen
		screen.blit(level, (0,0), view)
		pygame.display.flip()

		#do all this at 40 fps
		clock.tick(40)

def drawSemi(pxarray):
	pos = pygame.mouse.get_pos()
	playerx = 320
	playery = 240
	dx = pos[0] - playerx
	dy = pos[1] - playery
	
	# find circle center (player edge)  normalize on hyp of 16px
	hyp = math.hypot(dx, dy)
	div = hyp / 16.0
	dx = int(dx / div)
	dy = int(dy / div)
	circlex = playerx + dx
	circley = playery + dy

	clear = 0xFFFF00FF
	#clear = 0

	# initialize circle data structure (map of lists)
	circle = {}
	for x in range(circlex - 16, circlex + 17):
		circle[x] = [circley]

	# put circle outline into data structure
	y = 16
	for x in range(0, 17):
		newy = int(math.sqrt(256 - x**2))
		if newy != y:
			# shorter end makes it look more round
			end = newy
			if end < 8: end -= 1
			for y in range(y, end, -1):
				# the four quarters of the circle
				circle[circlex + x].append(circley + y) 
				circle[circlex + x].append(circley - y) 
				circle[circlex - x].append(circley + y) 
				circle[circlex - x].append(circley - y) 

	# the top and bottom where not included?
	circle[circlex].append(circley - 16)
	circle[circlex].append(circley + 16)

	for x in circle:
		for y in range(min(circle[x]), max(circle[x])):
			pxarray[x][y] = clear


	'''
	# draw entire diameter
	startx = circlex - dy
	stopx = circlex + dy
	starty = circley + dx
	stopy = circley - dx
	dx2 = startx - stopx
	dy2 = starty - stopy

	# draw extremes of the diameter
	pxarray[startx][starty] = 0x00FF0000 #red
	pxarray[stopx][stopy] =   0x000000FF #blue

	xstep = -1
	if dx2 < 0:
		xstep = 1

	ystep = -1
	if dy2 < 0:
		ystep = 1

	if dy2 == 0:
		for x in range(startx, stopx, xstep):
			pxarray[x][starty] = clear
	elif dx2 == 0:
		for y in range(starty, stopy, ystep):
			pxarray[startx][y] = clear
	else:
		dy2pp = float(dy2) / dx2
		if dy < 0:
			dy2pp = -dy2pp

		newy = y = float(starty)
		x = startx
		for newx in range(startx, stopx, xstep):
			newy += dy2pp
			if int(newy) != int(y):
				ystep = 1
				if newy < y: ystep = -1
				for x in range(x, newx, xstep):
					pxarray[x][int((y))] = clear
				for y in range(int((y)), int((newy)), ystep):
					pxarray[x][y] = clear

	# angle from player's center to mouse
	rad = 0
	if dy != 0:
		rad = math.atan(float(abs(dx))/float(abs(dy)))
		if playerx < pos[0] and playery > pos[1]:
			pass # we have correct rad in first quadrant
		elif playerx > pos[0] and playery > pos[1]:
			rad = math.pi - rad # in the second quadrant
		elif playerx > pos[0] and playery < pos[1]:
			rad += math.pi # in the third quadrant
		elif playerx < pos[0] and playery < pos[1]:
			rad = math.pi * 2 - rad # in the fourth quadrant

	# start and stop angle of semi circle
	startRad = rad + math.pi / 2
	stopRad = rad - math.pi / 2

	# clear with fully transparent black (all zeros)
	#clear = 0x00000000 # yes I could have just used 0

	# outer corner of semi circle
	startx = int(round(circlex + 16 * math.cos(startRad)))
	starty = int(round(circley + 16 * math.sin(startRad)))
	pxarray[startx][starty] = clear

	'''

if __name__ == '__main__': main()
