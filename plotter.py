#!/usr/bin/python
import argparse
import math
import msgpackrpc
import socket
import time

# 762 508 508 0 10
INCREASE = 1
DECREASE = -1 

# DISTANCE_PER_TICK = 1
DISTANCE_PER_TICK = 0.59817 # mm
SLEEP_TIME = .001

SCALE_FACTOR = 4
X_OFFSET = 0
Y_OFFSET = 0

client = None
dist = 0
right_distance = 0
left_distance = 0
right_x = 0
right_y = 0
left_x = 0
left_y = 0
curr_x = 0
curr_y = 0
pl_y =  pr_x = 0

def parse_args():
  parser = argparse.ArgumentParser(description='Process some integers.')
  parser.add_argument('distance', metavar='D', type=float, help='Distance between motors')
  parser.add_argument('left', metavar='L', type=float, help='Length of left string')
  parser.add_argument('right', metavar='R', type=float, help='Length of right string')
  parser.add_argument('x', metavar='x', type=float, help='Length of right string')
  parser.add_argument('y', metavar='y', type=float, help='Length of right string')
  parser.add_argument('-H', '--host', default='localhost', help="Host")
  parser.add_argument('-F', '--file', default='localhost', help="Host")
  return parser.parse_args()
  
# calulates angle opposite of side c in radians
def law_of_cos(a, b, c):
  return math.acos((a**2 + b**2 - c**2)/(2* a * b))

def calculate_motor_pts(d, l, r):
  right_angle = law_of_cos(d, r, l)
  left_angle = law_of_cos(d, l, r)
  # print math.degrees(right_angle)
  # print math.degrees(left_angle)
  r_y = math.sin(right_angle) * r
  r_x = math.cos(right_angle) * r
  l_y = math.sin(left_angle) * l
  l_x = -math.cos(left_angle) * l
  return [(r_x, r_y), (l_x, l_y)]

def calc_distance(x1, y1, x2, y2):
  # print math.sqrt(((x2-x1)**2) + ((y2-y1)**2))
  return math.sqrt(((x2-x1)**2) + ((y2-y1)**2))

def calc_left_distance(x,y):
  global right_x, left_x, right_y, left_y
  # if (x > right_x or x < left_x or y > right_y):
  #   return -1
  # else:
  return calc_distance(x, y, left_x, left_y)

def calc_right_distance(x,y):
  global right_x, left_x,right_y
  # if (x > right_x or x < left_x or y > right_y):
  #   return -1
  # else:
  return calc_distance(x, y, right_x, right_y)

# given current and desired distance returns number of ticks
def distance_to_ticks(curr, desired):
  # print "curr: {}, desired {}".format(curr, desired)
  # print ((desired - curr) * (1/DISTANCE_PER_TICK))
  return round((desired - float(curr)) * (1.0/DISTANCE_PER_TICK))

def tick_right(desired):
  global right_distance, client
  if (right_distance < desired):
    # print "o"
    # sock.sendto("o", (UDP_IP, UDP_PORT))
    client.call('tick_right', INCREASE)
  else:
    # print "l"
    # sock.sendto("l", (UDP_IP, UDP_PORT))
    client.call('tick_right', DECREASE)

def tick_left(desired):
  global left_distance, sock
  if (left_distance < desired):
    # print "i"
    client.call('tick_left', INCREASE)
  else:
    # print "k"
    client.call('tick_left', DECREASE)


def move_to_pt(x, y):
  global right_distance, left_distance, dist, sock, curr_x, curr_y, pl_y, pr_x

  # Segment line into multiple motions to get smoother lines
  num_segments = int(calc_distance(curr_x, curr_y, x, y)/20)
  if num_segments == 0: 
    num_segments = 1

  # print int(calc_distance(curr_x, curr_y, x, y))

  dx = (x-curr_x)/num_segments
  dy = (y-curr_y)/num_segments

  # print dx
  # print dy



  for i in xrange(1, num_segments+1):
    # print "At {},{} segments.".format(i, num_segments)
    # Calculate end of current line segment   
    target_x = curr_x + dx
    target_y = curr_y + dy

    # print "segment (%s, %s) from  (%s, %s) with (%s, %s)" % (target_x, target_y, curr_x, curr_y, dx, dy)

    # print "X: %s ->, %s, Y: %s -> %s"  % (curr_x, target_x, curr_y, target_y)

    # curr_x = target_x
    # curr_y = target_y;

    # Calculate required lengths for end of current line segment
    new_right_dist = calc_right_distance(target_x, target_y)
    new_left_dist = calc_left_distance(target_x, target_y)

    # print "right distance is: {}, used to be {}".format(new_right_dist, right_distance)
    # print "left distance is: {}, used to be {}".format(new_left_dist, left_distance)
    
    ticks_right = abs(distance_to_ticks(right_distance, new_right_dist))
    ticks_left = abs(distance_to_ticks(left_distance, new_left_dist))
    total_ticks = max(ticks_left, ticks_right)
    # print "Right ticks: {}, left ticks {}". format(ticks_right, ticks_left)
    # tick_ratio = max(ticks_right, ticks_left)/min(ticks_right, ticks_left)

    left_accum = 0
    right_accum = 0
    for _ in xrange(int(total_ticks)):
      
      left_accum += ticks_left
      if (left_accum > total_ticks):
        left_accum -= total_ticks
        tick_left(new_left_dist)

      right_accum += ticks_right
      if (right_accum > total_ticks):
        right_accum -= total_ticks
        tick_right(new_right_dist)

      # print "%s, %s, %s" % (left_accum, right_accum, total_ticks)

      # time.sleep(SLEEP_TIME)
    right_distance += distance_to_ticks(right_distance, new_right_dist) * DISTANCE_PER_TICK
    left_distance += distance_to_ticks(left_distance, new_left_dist) * DISTANCE_PER_TICK
    # right_distance = new_right_dist
    # left_distance = new_left_dist

    s =  calculate_motor_pts(dist, left_distance, right_distance)
    (x_r, y_r) = s[0]
    (x_l, y_l) = s[1]
    print "mv: (%s, %s)" % (pr_x - x_r, pl_y - y_l)
    
    curr_x += pr_x - x_r
    curr_y += pl_y - y_l
    pr_x = x_r
    pl_y = y_l


def main():
  args = parse_args()
  global left_distance, right_distance, dist, client, pl_y, pr_x
  dist = args.distance
  left_distance = args.left
  right_distance = args.right
  motor_pts = calculate_motor_pts(dist, left_distance, right_distance)
  print motor_pts
  
  global right_x,right_y, left_x, left_y
  right_x= motor_pts[0][0]
  right_y = motor_pts[0][1]
  left_x = motor_pts[1][0]
  left_y = motor_pts[1][1]

  pl_y = left_y
  pr_x = right_x

  client = msgpackrpc.Client(msgpackrpc.Address(args.host, 18800))

  client.call('pen_up')
  client.call('reset')
  move_to_pt(0,0)
  time.sleep(3)
  # client.call('pen_down')
  with open(args.file) as f:
    lines = f.readlines()
    prev_token = "hello"
    for line in lines:
      tokens = line.split()
      # if (prev_token[0] != "G1" or prev_token[1] == "Z80"):
      #   client.call('pen_up')
      #   # print "PEN IS UP"
      # else:
      #   client.call('pen_down')
      #   # print "PEN IS DOWN"
      if (tokens[0] == "G1" and tokens[1][0] == "Z"):
        if tokens[1] == "Z114":
          client.call('pen_down')
          print "pen down"
        else:
          client.call('pen_up')
          print 'pen up'

      if (tokens[0] == "G1" and tokens[1][0] != "Z"):
        if len(tokens) >= 3:
          x_pt = (float(tokens[1][1:]) * SCALE_FACTOR) + X_OFFSET
          y_pt = -(float(tokens[2][1:]) * SCALE_FACTOR) + Y_OFFSET
          print "x: {}, y: {} ({}, {})".format(x_pt, y_pt, float(tokens[1][1:]), float(tokens[2][1:]))
          move_to_pt(x_pt, y_pt)
          
      prev_token = tokens

  # move_to_pt(args.x,args.y)
  # move_to_pt(50, 0)
  # move_to_pt(0, -50)
  # move_to_pt(-50, 0)
  # move_to_pt(0, 50)
  # move_to_pt(50, 0)
  # move_to_pt(50, -50)
  # move_to_pt(0, -50)
  # move_to_pt(0, 0)
  # move_to_pt(65, -130*.866)
  # move_to_pt(-65, -130*.866)
  # move_to_pt(0,0)
  print dist
  print left_distance
  print right_distance
  print calculate_motor_pts(dist, left_distance, right_distance)
  


if __name__ == '__main__':
  main()