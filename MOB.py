import pygame

class MOB(pygame.Rect):
	"""Basic Movable Object Super Class"""

	def __init__(self, x, y, w, h):
		pygame.Rect.__init__(self, x, y, w, h)

		# Precision x and y
		self.px = 0.0
		self.py = 0.0

		# delta x and y (speed)
		self.dx = 0.0
		self.dy = 0.0

