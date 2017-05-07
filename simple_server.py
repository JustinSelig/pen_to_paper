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

def turnOffMotors():
	mh.getMotor(1).run(Adafruit_MotorHAT.RELEASE)
	mh.getMotor(2).run(Adafruit_MotorHAT.RELEASE)
	mh.getMotor(3).run(Adafruit_MotorHAT.RELEASE)
	mh.getMotor(4).run(Adafruit_MotorHAT.RELEASE)


class SimpleServer(object):
	def __init__(self, left, right, servo):
		self.servo = servo
		self.left = left
		self.right = right

	def pen_down(self):
		self.servo.start(20/10)
		time.sleep(.25)
		self.servo.ChangeDutyCycle(0)
		print "pen down"

	def tick_right(self, direction):
		print "tick right"
		if direction == INCREASE:
			tick(self.right, Adafruit_MotorHAT.FORWARD)
			self.total_right += 1
		elif direction == DECREASE:
			tick(self.right, Adafruit_MotorHAT.BACKWARD)
			self.total_right -= 1

if __name__ == '__main__':
	GPIO.cleanup()
	# create a default object, no changes to I2C address or frequency
	mh = Adafruit_MotorHAT()

	atexit.register(turnOffMotors)

	stepper_left = mh.getStepper(200, 1)          # 200 steps/rev, motor port #1
	stepper_right = mh.getStepper(200, 2)         # 200 steps/rev, motor port #1
	stepper_left.setSpeed(200)            # 30 RPM
	stepper_right.setSpeed(200)           # 30 RPM

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

	#try:
	server = msgpackrpc.Server(SimpleServer(stepper_left, stepper_right, p))
	server.listen(msgpackrpc.Address("localhost", 18801))
	server.start()
	GPIO.cleanup()

	#except:
	#	server.stop()
	#	server.close()


