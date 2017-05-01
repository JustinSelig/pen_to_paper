import math
import msgpackrpc
import pygame
import random
import sys
import socket
import time
import threading

from math import cos, sin, pi, sqrt, atan2
from pygame.locals import *

screen_size_x = 1920
screen_size_y = 1080

DIST_PER_TICK = 1

d2r = pi/180

# https://gist.github.com/xaedes/974535e71009fa8f090e
class Geometry(object):
    
    @staticmethod
    def circle_intersection(circle1, circle2):
        '''
        @summary: calculates intersection points of two circles
        @param circle1: tuple(x,y,radius)
        @param circle2: tuple(x,y,radius)
        @result: tuple of intersection points (which are (x,y) tuple)
        '''
        x1,y1,r1 = circle1
        x2,y2,r2 = circle2
        # http://stackoverflow.com/a/3349134/798588
        dx,dy = x2-x1,y2-y1
        d = sqrt(dx*dx+dy*dy)
        if d > r1+r2:
            return None # no solutions, the circles are separate
        if d < abs(r1-r2):
            return None # no solutions because one circle is contained within the other
        if d == 0 and r1 == r2:
            return None # circles are coincident and there are an infinite number of solutions

        a = (r1*r1-r2*r2+d*d)/(2*d)
        h = sqrt(r1*r1-a*a)
        xm = x1 + a*dx/d
        ym = y1 + a*dy/d
        xs1 = xm + h*dy/d
        xs2 = xm - h*dy/d
        ys1 = ym - h*dx/d
        ys2 = ym + h*dx/d

        return (xs1,ys1),(xs2,ys2)

class Simulator:
    CIRCLE_COLOR = (220, 220, 220)
    LINE_COLOR = (0, 0, 0)

    def __init__(self, screen):
        self.starting_radius = screen_size_x/2 + 20
        self.left = self.starting_radius
        self.right = self.starting_radius
        print self.starting_radius
        self.screen = screen
        self.dots = set()
        self.is_pen_down = False

    def calc_intersect(self):
        intersect = Geometry.circle_intersection((0, 0, self.left), (screen_size_x, 0, self.right))
        if intersect:
            if len(intersect) > 1:
                return sorted(intersect, key=lambda tup: tup[1])[1]
            else:
                return intersect
        else:
            return None

    def pen_down(self):
        self.is_pen_down = True

    def pen_up(self):
        self.is_pen_down = False


    def tick_right(self, direction):
        self.right += DIST_PER_TICK * direction

    def tick_left(self, direction):
        self.left += DIST_PER_TICK * direction


    def tick(self, left, right):
        self.left += DIST_PER_TICK * left
        self.right += DIST_PER_TICK * right

    def reset(self):
        self.left = self.starting_radius
        self.right = self.starting_radius
        self.dots = set()

    def update(self):
        pygame.draw.circle(self.screen, Simulator.CIRCLE_COLOR, (0, 0), self.left, 1)
        pygame.draw.circle(self.screen, Simulator.CIRCLE_COLOR, (screen_size_x, 0), self.right, 1)

        intersect = self.calc_intersect()
        if intersect:
            pygame.draw.aaline(self.screen, Simulator.LINE_COLOR, (0,0), intersect, 10)
            pygame.draw.aaline(self.screen, Simulator.LINE_COLOR, (screen_size_x,0), intersect, 10)
            if self.is_pen_down:
                (x, y) = intersect
                self.dots.add((int(x), int(y)))

            for dot in self.dots:
                pygame.draw.circle(self.screen, (255,0,0), dot, 1, 1)

class SimulatorInterface(object):
    def __init__(self, simulator):
        self.simulator = simulator

    def pen_down(self):
        self.simulator.pen_down()

    def pen_up(self):
        self.simulator.pen_up()

    def tick_right(self, direction):
        self.simulator.tick_right(direction)

    def tick_left(self, direction):
        self.simulator.tick_left(direction)


    def tick(self, left, right):
        self.simulator.tick(left, right)

    def reset(self):
        self.simulator.reset()


def receiver(simulator):
    server = msgpackrpc.Server(SimulatorInterface(simulator))
    server.listen(msgpackrpc.Address("localhost", 18800))
    server.start()

def main():
    pygame.init()
    screen = pygame.display.set_mode((screen_size_x, screen_size_y), 0, 32)
    simulator = Simulator(screen)
    

    t = threading.Thread(target=receiver, args=(simulator,))
    t.start()

    while True:
     
        screen.fill((255, 255, 255))
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
        simulator.update()
        pygame.display.update()
        time.sleep(0.001)

if __name__ == '__main__':
    main()
