import pygame # Import Library and initialize pygame
from pygame.locals import *
import signal
import RPi.GPIO as GPIO
import time
import os

os.putenv('SDL_VIDEODRIVER', 'fbcon') # Display on piTFT
os.putenv('SDL_FBDEV', '/dev/fb1') #
os.putenv('SDL_MOUSEDRV', 'TSLIB') # Track mouse clicks on piTFT
os.putenv('SDL_MOUSEDEV', '/dev/input/touchscreen')

pygame.init()

size = width, height = 320, 240
WHITE = (255,255,255)
#pigame stuff
pygame.mouse.set_visible(False)
screen = pygame.display.set_mode(size)

my_font = pygame.font.Font(None, 20)
x,y=None,None
my_buttons = {'QUIT':(80, 180), 'Touch at: '+str(x)+','+str(y):(160,120)}

 
while True:
	time.sleep(0.1)
	prev_x, prev_y = x,y
	for event in pygame.event.get():
		if (event.type is MOUSEBUTTONDOWN):
			print True
			pos = pygame.mouse.get_pos()
			x,y = pos
			print "Touch at: " + str(x)+','+str(y)	
			my_buttons['Touch at: '+str(x)+','+str(y)] = my_buttons.pop('Touch at: '+str(prev_x)+','+str(prev_y))
			screen.fill((0,0,0))
			if y>140:
				if x<160:
					print "quit button pressed"
					pygame.quit()
					quit()
				else:
					print "outside of button pressed"
			prev_x, prev_y = x,y
	
	
	for my_text,  text_pos in my_buttons.items():
                text_surface = my_font.render(my_text, True, WHITE)
                rect = text_surface.get_rect(center=text_pos)
                screen.blit(text_surface, rect)
        pygame.display.flip()

