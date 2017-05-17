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
import os

PWM_PIN = 22
INCREASE = 1
DECREASE = -1

#HOSTNAME = "128.253.17.173"
HOSTNAME = 'localhost'
PORT = 18803

def stepper_worker(stepper, numsteps, direction, style):
	stepper.step(numsteps, direction, style)

def tick(stepper, direction, steps=1):
	worker = threading.Thread(target=stepper_worker, args=(stepper, steps, direction, Adafruit_MotorHAT.DOUBLE))
	worker.start()
	#i=0
	while worker.isAlive():
		#print "working"+str(i)
		#i=i+1
		pass

def tick_async(stepper, direction, steps=1):
	try:
		worker = threading.Thread(target=stepper_worker, args=(stepper, steps, direction, Adafruit_MotorHAT.INTERLEAVE))
		worker.start()
		print threading.active_count()
		return worker
	except:
		print "moving too fast - too many threads generated - please wait to continue"

def tick_step(stepper, direction, steps=10):
	stepper.step(steps, direction, style)

def turnOffMotors():
	mh.getMotor(1).run(Adafruit_MotorHAT.RELEASE)
	mh.getMotor(2).run(Adafruit_MotorHAT.RELEASE)
	mh.getMotor(3).run(Adafruit_MotorHAT.RELEASE)
	mh.getMotor(4).run(Adafruit_MotorHAT.RELEASE)

"""
global move_queue 

def move_dispatch():
	#global move_queue
	move_queue = [(1,0),(1,0)] #initialize as empty
	while True:
		print move_queue
		time.sleep(0.5)
		if move_queue:
			(dx, dy) = move_queue.pop(0)
			print dx, dy
			if (dx>=0):
				tick_async(self.right, Adafruit_MotorHAT.FORWARD, dx)
			else:
				tick_async(self.right, Adafruit_MotorHAT.BACKWARD, abs(dx))
			if (dy>=0):
				tick_async(self.left, Adafruit_MotorHAT.FORWARD, dy)
			else:
				tick_async(self.left, Adafruit_MotorHAT.BACKWARD, abs(dy))
"""


class SimpleServer(object):
	def __init__(self, left, right, servo):
		self.servo = servo
		self.left = left
		self.right = right
		self.total_right = 0
		self.total_left = 0
		self.move_queue = []
		self.move_thread = threading.Thread(target=self.move_dispatch)
		self.move_thread.start()
		#self.move_queue_lock = threading.Lock()
		self.is_paused = False

	#zeros the plotter based on its current total x and y position
	def zero(self):
		pass

	#moves to specified x, y coordinate based on current position
	def move_to(self, x, y):
		pass

	#tells plotter approximately where its head is based on input
	def calibrate(self, x, y):
		pass

	def quit(self):
		turnOffMotors()
		#self.stop()
		GPIO.cleanup()
		#self.close()
		os._exit(0)
		quit()

	def pause(self):
		self.is_paused = not self.is_paused

	def pen_down(self):
		self.servo.start(20/10)
		time.sleep(.25)
		self.servo.ChangeDutyCycle(0)
		print "pen down"

	def tick_right(self, direction):
		print "tick right"
		if direction == INCREASE:
			print "calling tick"
			tick_async(self.right, Adafruit_MotorHAT.FORWARD)
			self.total_right += 1
		elif direction == DECREASE:
			tick_async(self.right, Adafruit_MotorHAT.BACKWARD)
			self.total_right -= 1

	def tick_left(self, direction):
		if direction == INCREASE:
			tick_async(self.left, Adafruit_MotorHAT.BACKWARD)
			self.total_left += 1
		elif direction == DECREASE:
			tick_async(self.left, Adafruit_MotorHAT.FORWARD)
			self.total_left -= 1

	#not currently used
	def move1(self, dx, dy):
		#bounds check
		#if self.total_left>2500 or self.total_left<-2500 or self.total_right>2500 or self.total_right<-2500:
		#	return -1

		if (dx>=0):
			tick(self.right, Adafruit_MotorHAT.FORWARD, dx)
		else:
			tick(self.right, Adafruit_MotorHAT.BACKWARD, abs(dx))
		if (dy>=0):
                        tick(self.left, Adafruit_MotorHAT.FORWARD, dy)
                else:
                        tick(self.left, Adafruit_MotorHAT.BACKWARD, abs(dy))


	#spawns thread to push dx,dy to move queue so that client is free to continue reading input
	#figure out how to notify client that out of bounds
	def move(self, dx, dy):
		#if self.total_left>2500 or self.total_left<-2500 or self.total_right>2500 or self.total_right<-2500:
		#	return -1
		#global move_queue
		#with self.move_queue_lock:
		##self.move_queue.append((dx, dy))
		#print 'appended to queue'
		#print self.move_queue
		t = threading.Thread(target=self.push, args=(dx,dy))
		t.start()
		print 'in move'
		print self.total_right, self.total_left


	def push(self, dx, dy):
		self.move_queue.append((dx,dy))
		print 'in push'

	#unused
	def move_dispatch1(self):
        	while True:
        	        print self.move_queue
        	        time.sleep(0.1)
        	        if self.move_queue:
        	        	(dx, dy) = self.move_queue.pop(0)
        	        	#print dx, dy
				self.move1(dx, dy)

	def move_dispatch(self):
		while True:
			#time.sleep(0.1)
			#print self.move_queue
			#with self.move_queue_lock:
			if self.move_queue and (not self.is_paused):
				(dx, dy) = self.move_queue.pop(0)
				print 'dx, dy: ', dx, dy
				if (dx>=0):
					#tick_step(self.right, Adafruit_MotorHAT.FORWARD, dx)
					right_worker = threading.Thread(target=stepper_worker, args=(self.right, dx, Adafruit_MotorHAT.FORWARD, Adafruit_MotorHAT.SINGLE))
					self.total_left += dx
				else:
					#tick_step(self.right, Adafruit_MotorHAT.BACKWARD, abs(dx))
					right_worker = threading.Thread(target=stepper_worker, args=(self.right, abs(dx), Adafruit_MotorHAT.BACKWARD, Adafruit_MotorHAT.SINGLE))
					self.total_left += dx
				if (dy>=0):
					#tick_step(self.left, Adafruit_MotorHAT.FORWARD, dy)
                                        left_worker = threading.Thread(target=stepper_worker, args=(self.left, dy, Adafruit_MotorHAT.FORWARD, Adafruit_MotorHAT.SINGLE))
					self.total_right += dy
				else:
					#tick_step(self.left, Adafruit_MotorHAT.BACKWARD, abs(dy))
					left_worker = threading.Thread(target=stepper_worker, args=(self.left, abs(dy), Adafruit_MotorHAT.BACKWARD, Adafruit_MotorHAT.SINGLE))
					self.total_right += dy
				#worker1 = threading.Thread(target=stepper_worker, args=(stepper, steps, direction, Adafruit_MotorHAT.DOUBLE))
				#worker2 = threading.Thread(target=stepper_worker, args=(stepper, steps, direction, Adafruit_MotorHAT.DOUBLE))
				right_worker.start()
				left_worker.start()

				while right_worker.isAlive() or left_worker.isAlive():
					#print 'in while'
					time.sleep(0.05)
					pass


				 

if __name__ == '__main__':
	GPIO.cleanup()
	# create a default object, no changes to I2C address or frequency
	mh = Adafruit_MotorHAT()

	atexit.register(turnOffMotors)

	stepper_left = mh.getStepper(1, 1)          # 200 steps/rev, motor port #1
	stepper_right = mh.getStepper(1, 2)         # 200 steps/rev, motor port #1
	stepper_left.setSpeed(200000000)            # 30 RPM
	stepper_right.setSpeed(200000000)           # 30 RPM

	"""
	st1 = threading.Thread(target=stepper_worker, args=(stepper_left, 400, Adafruit_MotorHAT.FORWARD, Adafruit_MotorHAT.DOUBLE))
	st1.start()

	st2 = threading.Thread(target=stepper_worker, args=(stepper_right, 400, Adafruit_MotorHAT.BACKWARD, Adafruit_MotorHAT.DOUBLE))
	st2.start()
	"""

	#st3 = threading.Thread(target=move_dispatch)
	#st3.start()
	#st3.join()

	"""
	# Wait for it to center
	while st1.isAlive() or st2.isAlive():
		time.sleep(1)
	"""

	# Configure input pins with internal pull up resistors
	#UNCOMMENT TO USE SERVO FOR PEN TIP!
	#GPIO.setmode(GPIO.BCM)
	#GPIO.setup(PWM_PIN, GPIO.OUT)

	# Set to 50Hz
	#p = GPIO.PWM(PWM_PIN, 10)
	
	#try:
	server = msgpackrpc.Server(SimpleServer(stepper_left, stepper_right,1))#, p))
	server.listen(msgpackrpc.Address(HOSTNAME, PORT))
	server.start()
	GPIO.cleanup()

	#except:
	#	server.stop()
	#	server.close()


