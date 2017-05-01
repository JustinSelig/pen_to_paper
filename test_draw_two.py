import pygame # Import Library and initialize pygame
from pygame.locals import *
import signal
import RPi.GPIO as GPIO
import time
import os
import sys

#os.putenv('SDL_VIDEODRIVER', 'fbcon') # Display on piTFT
os.putenv('SDL_FBDEV', '/dev/fb1') #
os.putenv('SDL_MOUSEDRV', 'TSLIB') # Track mouse clicks on piTFT
os.putenv('SDL_MOUSEDEV', '/dev/input/touchscreen')

pygame.init()
pygame.display.set_caption('Paintme')
size = width, height = 320, 240
WHITE = (255,255,255)
#pigame stuff
pygame.mouse.set_visible(False)
window = pygame.display.set_mode(size)
mouse = pygame.mouse
fpsClock=pygame.time.Clock()

canvas = window.copy()
#                     R    G    B
BLACK = pygame.Color( 0 ,  0 ,  0 )
WHITE = pygame.Color(255, 255, 255)
canvas.fill(WHITE)
while True:
	left_pressed, middle_pressed, right_pressed = mouse.get_pressed()
	for event in pygame.event.get():
		if event.type == QUIT:
			pygame.quit()
			sys.exit()
		elif left_pressed:
			pygame.draw.circle(canvas, BLACK, (pygame.mouse.get_pos()),5)
	window.fill(WHITE)
	window.blit(canvas, (0, 0))


	pygame.draw.circle(window, BLACK, (pygame.mouse.get_pos()), 5)
	pygame.display.update()


