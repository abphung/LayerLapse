from pygame import *

class Button:

	def __init__(self, action, x, y, text):
		self.action = action
		self.rect = Rect(x, y, 200, 200)
		self.color = (200, 200, 200)
		self.font = font.SysFont('Comic Sans MS', 30)
		self.text = self.font.render(text, False, (128, 128, 0))

	def draw(self, screen, color):
		draw.rect(screen, color, self.rect)
		screen.blit(self.text, (self.rect.x, self.rect.y + self.rect.height/2))