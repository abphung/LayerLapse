import pygame
from pygame import *
from Tkinter import Tk
from tkFileDialog import askopenfilename
from button import Button

Tk().withdraw()
pygame.init()

grey = (128, 128, 128)
blue = (0, 0, 128) 

size = (800, 600)
screen = pygame.display.set_mode(size)
pygame.display.set_caption("LayerLapse")

clock = pygame.time.Clock()

#buttons
timelapse_button = Button(askopenfilename, 100, 200, "choose a timelapse")
song_button = Button(askopenfilename, 500, 200, "choose a song")
buttons = [timelapse_button, song_button]

running = True
while running:
	#handle events
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False
		elif event.type == pygame.MOUSEBUTTONUP:
			for button in buttons:
				if button.rect.collidepoint(mouse.get_pos()):
					filename = button.action()

	#draw
	screen.fill(grey)
	for button in buttons:
		button.draw(screen, blue)
	pygame.display.flip()
pygame.quit()