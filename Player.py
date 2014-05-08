import pygame
from MOB import MOB

class Player(MOB):
	"""Player Guy"""

	img = pygame.image.load('left-right.png')
	
	def __init__(self, x, y, w, h):
		MOB.__init__(self, x, y, w, h)
		self.px = x
		self.py = y

		self.dx = 0
		self.dy = 0

		# sprite is the area of the img spritesheet to display
		self.sprite = pygame.Rect(0,0,32,32)
		self.jumping = False

	def moveLeft(self):
		self.px -= 1.5 + self.dx
		self.x = self.px

		# select left moving sprite
		self.sprite.left = 0

	def moveRight(self):
		self.px += 1.5 + self.dx
		self.x = self.px

		#select right moving sprite
		self.sprite.left = 32

	def setRun(self, running):
		if running:
			if self.dx < 8:
				self.dx += 0.25
			else:
				self.dx = 8
		else:
			self.dx = 0

	def display(self, surface, view):
		x = self.x - view.x
		y = self.y - view.y
		surface.blit(Player.img, (x, y), self.sprite)
		
