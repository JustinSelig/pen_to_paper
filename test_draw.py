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
global color #line color

def draw_to_paper(dx, dy):
	global client
	#client.call('pen_down')
	client.call('tick_left', INCREASE)
	#for x in range(abs(dx)):
	#	client.call()

def move(dx, dy):
	global client
	#print 'calling move'
	#client.call('move', 5, 5)
	#print 'returning'
	client.call('move', 20*dx, 20*dy)
	if dx>0:
		dx = 5
	if dy>0:
		dy = 5
	if dx<0:
		dx = -5
	if dy<0:
		dy = -5
	#client.call('move', dx, dy)

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

#defines what to do on single mouse cliek
def single_click(position, screen):
	global client
	x_pos = position[0]
	y_pos = position[1]
	if y_pos <= 20:
		if x_pos <= 40:
			print 'quit'
			pygame.quit()
			client.call('quit')
			quit()
		elif x_pos <= 90:
			print 'clear'
			screen.fill((0,0,0))
			place_buttons(screen)
		elif x_pos <= 150:
			print 'pause'
			client.call('pause')
		elif x_pos <= 200:
			print 'color'
			global color
			color = (random.randrange(256), random.randrange(256), random.randrange(256))
		else:
			if x_pos >=269:
				#Up clicked
				print 'up'
				move(0,10)
				return
	if y_pos <= 45:
		if x_pos<=288 and x_pos>=265:
			#Left clicked
			print 'left'
			move(10,0)
			return
		if x_pos>=289:
			#right clicked
			print 'right'
			move(-10,0)
			return
	elif y_pos <= 55 and x_pos >= 288:
		print 'down'
		move(0,-10)
		return

def place_buttons(screen, color=(255,255,255)):
	my_buttons = {'QUIT | ':(20,10), 'CLEAR | ':(70,10), 'PAUSE | ':(130,10), 'COLOR':(180,10), 'R':(310,30), 'L':(270,30), 'U':(290,10), 'D':(290,50)}
	my_font = pygame.font.Font(None, 20)
	for my_text,  text_pos in my_buttons.items():
		text_surface = my_font.render(my_text, True, color)
		rect = text_surface.get_rect(center=text_pos)
		screen.blit(text_surface, rect)

def main():
	global client
	global color
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
	pygame.mouse.set_visible(True)
	screen = pygame.display.set_mode(size)
	#my_font = pygame.font.Font(None, 20)
	#my_buttons = {'QUIT | ':(20,10), 'CLEAR | ':(70,10), 'PAUSE | ':(130,10), 'COLOR':(180,10), 'R':(310,30), 'L':(270,30), 'U':(290,10), 'D':(290,50)}

	draw_on = False
	last_pos = (0, 0)
	color = WHITE #(255, 128, 0)
	radius = 1

	#for my_text,  text_pos in my_buttons.items():
	#	text_surface = my_font.render(my_text, True, WHITE)
	#	rect = text_surface.get_rect(center=text_pos)
	#	screen.blit(text_surface, rect)

	place_buttons(screen, WHITE)

	try:
		while True:
			#time.sleep(0.01)
			e = pygame.event.wait()
			if e.type == pygame.QUIT:
				raise StopIteration
			if e.type == pygame.MOUSEBUTTONDOWN:
				#color = (random.randrange(256), random.randrange(256), random.randrange(256))
				#pygame.draw.circle(screen, color, e.pos, radius)
				draw_on = True
				single_click(e.pos, screen)
			if e.type == pygame.MOUSEBUTTONUP:
				draw_on = False
			if e.type == pygame.MOUSEMOTION:
				if draw_on:
					pygame.draw.circle(screen, color, e.pos, radius)
					(motor_dx, motor_dy) = roundline(screen, color, e.pos, last_pos, radius)
					#draw_to_paper(motor_dx, motor_dy)
					move(motor_dx, motor_dy)
	        		last_pos = e.pos
			#if draw_on:
			#	navbar()

		#	for my_text,  text_pos in my_buttons.items():
		#		text_surface = my_font.render(my_text, True, WHITE)
		#		rect = text_surface.get_rect(center=text_pos)
		#		screen.blit(text_surface, rect)

			pygame.display.flip()

	except StopIteration:
		pass

	pygame.quit()

if __name__ == "__main__":
	main()
