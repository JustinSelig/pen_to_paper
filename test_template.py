import pygame # Import Library and initialize pygame
from pygame.locals import *
import signal
import RPi.GPIO as GPIO
import time
import os
import msgpackrpc
import random

INCREASE = 1
DECREASE = -1

HOSTNAME = "localhost"
PORT = 18803

#screen = pygame.display.set_mode((800,600))
global client

def draw_to_paper(dx, dy):
	global client
	#client.call('pen_down')
	client.call('tick_left', INCREASE)
	#for x in range(abs(dx)):
	#	client.call()

def move(dx, dy):
	global client
	client.call('move', dx, dy)

"""
Below code adapted from Stack Overflow post:
http://stackoverflow.com/questions/597369/how-to-create-ms-paint-clone-with-python-and-pygame/5900836
"""
def roundline(srf, color, start, end, radius=1):
	dx = end[0]-start[0]
	dy = end[1]-start[1]
	print dx, dy
	distance = max(abs(dx), abs(dy))
	for i in range(distance):
		x = int( start[0]+float(i)/distance*dx)
		y = int( start[1]+float(i)/distance*dy)
		pygame.draw.circle(srf, color, (x, y), radius)
	return (dx, dy)

def main():
	global client
	client = msgpackrpc.Client(msgpackrpc.Address(HOSTNAME, PORT)) #next, accept host as argument and port

	#uncomment below line to run on tft screen
	#os.putenv('SDL_VIDEODRIVER', 'fbcon') # Display on piTFT
	os.putenv('SDL_FBDEV', '/dev/fb1') #
	os.putenv('SDL_MOUSEDRV', 'TSLIB') # Track mouse clicks on piTFT
	os.putenv('SDL_MOUSEDEV', '/dev/input/touchscreen')

	pygame.init()

	size = width, height = 320, 240
	WHITE = (255,255,255)
	#pigame stuff
	pygame.mouse.set_visible(False)
	screen = pygame.display.set_mode(size)

	draw_on = False
	last_pos = (0, 0)
	color = (255, 128, 0)
	radius = 1

	movements = [(15,0),(5,0),(15,0),(5,0),(15,0),(5,0),(15,0),(15,0),(5,0),(5,0),(15,0),(15,0),(5,0),(15,0),(5,0),(15,0),(15,0)]
	for mov in movements:
		move(mov[0], mov[1])
		time.sleep(0.1)

	pygame.quit()

if __name__ == "__main__":
	main()
