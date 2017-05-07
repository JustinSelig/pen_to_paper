#!/usr/bin/python
from Adafruit_MotorHAT import Adafruit_MotorHAT, Adafruit_DCMotor, Adafruit_StepperMotor
import time
import atexit
import threading
import random
import argparse
import math
import msgpackrpc
import socket
import RPi.GPIO as GPIO
PWM_PIN = 22

INCREASE = 1
DECREASE = -1

def stepper_worker(stepper, numsteps, direction, style):
  stepper.step(numsteps, direction, style)

def tick(stepper, direction, steps=1):
  worker = threading.Thread(target=stepper_worker, args=(stepper, steps, direction, Adafruit_MotorHAT.DOUBLE))
  worker.start()
  while worker.isAlive():
    pass

def tick_async(stepper, direction, steps=1):
  worker = threading.Thread(target=stepper_worker, args=(stepper, steps, direction, Adafruit_MotorHAT.DOUBLE))
  worker.start()
  return worker

class PlotterInterface(object):
  def __init__(self, left, right, servo):
    self.left = left
    self.right = right
    self.total_left = 0
    self.total_right = 0
    self.servo = servo

  def pen_down(self):
    self.servo.start(20/10)
    time.sleep(.25)
    self.servo.ChangeDutyCycle(0)
    print "pendown"

  def pen_up(self):
    self.servo.start(15/10)
    time.sleep(.25)
    self.servo.ChangeDutyCycle(0)
    print "penup"

  def tick_right(self, direction):
    if direction == INCREASE:
      tick(self.right, Adafruit_MotorHAT.FORWARD) 
      self.total_right += 1
    elif direction == DECREASE:
      tick(self.right, Adafruit_MotorHAT.BACKWARD) 
      self.total_right -= 1

  def tick_left(self, direction):
    if direction == INCREASE:
      tick(self.left, Adafruit_MotorHAT.BACKWARD) 
      self.total_left += 1
    elif direction == DECREASE:
      tick(self.left, Adafruit_MotorHAT.FORWARD) 
      self.total_left -= 1

  def tick(self, left, right):
    worker1 = threading.Thread()
    worker2 = threading.Thread()
    # Left
    if left == INCREASE:
      worker1 = tick_async(self.left, Adafruit_MotorHAT.BACKWARD) 
      self.total_left += 1
    elif left == DECREASE:
      worker1 = tick_async(self.left, Adafruit_MotorHAT.FORWARD) 
      self.total_left -= 1

    # Right
    if right == INCREASE:
      worker2 = tick_async(self.right, Adafruit_MotorHAT.FORWARD) 
      self.total_right += 1
    elif right == DECREASE:
      worker2 = tick_async(self.right, Adafruit_MotorHAT.BACKWARD) 
      self.total_right -= 1

    while (worker1.isAlive()) or (worker2.isAlive()):
      pass

  def reset(self):
    pass
    print "Resetting...(%s, %s)" % (self.total_left, self.total_right)
    if self.total_left > 0:
      tick(self.left, Adafruit_MotorHAT.FORWARD, steps=self.total_left)
    else:
      tick(self.left, Adafruit_MotorHAT.BACKWARD, steps=-self.total_left)

    if self.total_right > 0:
      tick(self.right, Adafruit_MotorHAT.BACKWARD, steps=self.total_right)
    else:
      tick(self.right, Adafruit_MotorHAT.FORWARD, steps=-self.total_right)
    
    self.total_left = self.total_right = 0

def turnOffMotors():
  mh.getMotor(1).run(Adafruit_MotorHAT.RELEASE)
  mh.getMotor(2).run(Adafruit_MotorHAT.RELEASE)
  mh.getMotor(3).run(Adafruit_MotorHAT.RELEASE)
  mh.getMotor(4).run(Adafruit_MotorHAT.RELEASE)


if __name__ == '__main__':
  # create a default object, no changes to I2C address or frequency
  mh = Adafruit_MotorHAT()

  atexit.register(turnOffMotors)

  stepper_left = mh.getStepper(200, 1)  	# 200 steps/rev, motor port #1
  stepper_right = mh.getStepper(200, 2)  	# 200 steps/rev, motor port #1
  stepper_left.setSpeed(200)  		# 30 RPM
  stepper_right.setSpeed(200)  		# 30 RPM

  st1 = threading.Thread(target=stepper_worker, args=(stepper_left, 400, Adafruit_MotorHAT.FORWARD, Adafruit_MotorHAT.DOUBLE))
  st1.start()

  st2 = threading.Thread(target=stepper_worker, args=(stepper_right, 400, Adafruit_MotorHAT.BACKWARD, Adafruit_MotorHAT.DOUBLE))
  st2.start()

  # Wait for it to center
  while st1.isAlive() or st2.isAlive():
   time.sleep(1)

  # Configure input pins with internal pull up resistors
  GPIO.setmode(GPIO.BCM)
  GPIO.setup(PWM_PIN, GPIO.OUT)
  
  # Set to 50Hz
  p = GPIO.PWM(PWM_PIN, 10)

  server = msgpackrpc.Server(PlotterInterface(stepper_left, stepper_right, p))
  server.listen(msgpackrpc.Address("localhost", 18801))
  server.start()
