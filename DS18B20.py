#Description:	    	This is a sensor class for the DS18B20 temperature
#   			sensor from Dallas Semiconductor
#
#Usage:		        This class uses the sensor interface class to interact
#			with the main architecture.  This will be instatitated
#	        	by the setup class and passed back to Main, which will
#			use the inherited methods to initiate and end data
#       		collection threads associated with this sensor object.
#						
#		        Calling getData() will kill any active threads and
#			begin a new one.  Eventually, this class will need to
#		    	be modified to accomodate this sensor's ability to
#   			stack many sensors on the same pin.
#
#Last Modified By:	Stephen Longofono
#			Onofognol@ku.edu
#			11 AM | 07/13/2015
#
#Created By:		Stephen Longofono
#			Onofognol@ku.edu
#			11 AM | 06/22/2015

import TempSensorGPIO
import threading
import time
import datetime
import string
import os
import subprocess

class DS18B20(TempSensorGPIO.TempSensorGPIO):

	#Parent constructor for reference
	#
	#def __init__(self, name, model, units, protocol, message, pin, pnp):
	#
	
	def __init__(self, sample, pin, filepath):
		
		#Messages and other specific implementation detail here
		msg = "\n\nInstructions:\nOpen /boot/config.txt and append:\n    dtoverlay=w1-gpio\n\nPrecautions:\nThis sensor MUST have a 4.7k Ohm resistor connecting the Vcc and data lines.  Connect this resistor before attaching the leads to the GPIO pins.\n"
		
		#Calls constructor of parent classes, from left to right
		#In this case, the temperature class properties are populated with the values
		#passed.  Pin is None and pnp is true because we are overriding the 
		#manual GPIO interaction; This sensor is plug and play with Raspian.
		super(DS18B20, self).__init__("Dallas", "DS18B20", "Degrees Celsius", "GPIO", msg, pin, True, sample)
		os.system("sudo modprobe w1-gpio")
		os.system("sudo modprobe w1-therm")
		temp = open("/boot/config.txt", "r")
		setting = "dtoverlay=w1-gpio, gpiopin=4"
		self.customs = None
		self.extraPins = None
		self.filepath = filepath
		if setting in temp.read():
			print "config ok"
		else:
			print "\nConfig Error!\nYou need to add the following to /boot/config.txt:\n\ndtoverlay=w1-gpio,gpiopin=4\n\nThen reboot and try again.\nIf you have already done so, make usre that you are setting up your DS18B20 with the data line on pin 4"	
		temp.close()
		#Find devices here since multiple are possible
		#TODO - Check agains config to distinguish between multiples
		#self.device = os.system("ls -l /sys/bus/w1/devices | grep 28-00000* ")
		self.device = "28-000000999999"
		

		#Failsafe for incorrectly connected device, put me back once RPI is setup
		#TODO testme
		#if self.device == None:
			#raise IOError

		#create a global switch visible across threads
		self.onOff = threading.Event()

		#list of threads associated with this object
		self.myThreads = []


	def getDeviceNum(self):
	
		#Get the list of devices
		devices = subprocess.Popen(['ls', '/sys/bus/w1/devices'], shell=False, stdout=subprocess.PIPE)
		currentDevices = devices.communicate()[0].split('\n')
		
		#remove the last index (stderr)
		currentDevices.pop()
	
		#remove non-temp sensors
		for item in currentDevices:
			if str(item)[0:2] != '28':
				currentDevices.remove(item)	
	
		#Many other devices
		#for i in range (0, len(myExistingDevInConfig)):
		#	if myExistingDevInConfig[i] in currentDevices:
		#		currentDevices.remove(myExistingDevInConfig[i])
		
		#single other device
		if myExistingDevInConfig in currentDevices:
			list.remove(myExistingDevInConfig)			

		#If this happens here, something went awry
		if len(currentDevices) > 1:
			print len(currentDevices)
			raise IOError("There are more than one device with the Dallas prefix in /sys/bus/w1/devices")

		return currentDevices[0]


	#Here, we override the getData method, because this specific sensor
	#has pnp capabilities built in to Raspian.  Otherwise, this method should
	#call the parent method using the parent pin, or be omitted entirely.
	def getData(self):

		if len(self.myThreads) == 0:
			temp = self.onOff
			thread = threading.Thread(target=self.readThread, args=(temp, self.filepath))
			thread.setDaemon(True)
			self.myThreads.append(thread)
			thread.start()

		else:
			self.onOff.set()
			time.sleep(2)
			
			while len(self.myThreads) > 0:
				self.myThreads.pop()

			self.onOff.clear()
			temp = self.onOff
			thread = threading.Thread(target=self.readThread, args=(temp, self.filepath))
			thread.setDaemon(True)
			self.myThreads.append(thread)
			thread.start()

		

	def readThread(self, onOff, filepath):

		#generate some pseudorandom numbers
		UUID = str(time.clock()**(0.5))
		
		#grab the last four
		UUID = UUID[len(UUID)-4:]
		
		#TODO make this path a parameter of __init__, passed in from Main and
		#populated from the config file.

		dataDir = filepath
		
		#All this sensor's data files will be identified as such:
		fileName = dataDir + "DS18B20_" + UUID + ".txt"
		dataFile = open(fileName, "a")
		myDev = str(self.getDeviceNum())

		try:
			while(not onOff.is_set()):

				#exploit the fact that unix treats everything as a file
				output = "/sys/bus/w1/devices/" + myDev + "/w1_slave"
				tempFile = open(output, "r")
				rawText = tempFile.read()
				tempFile.close()

				#Grab the second line, ninth space-delimited value
				rawData = rawText.split("\n")[1].split(" ")[9]
		
				#Grab everything after 't='
				temp = float(rawData[2:])

				#Adjust for resolution
				temp = temp/1000
				dataFile.write(str(temp) + " " + self.Units)
				dataFile.write(" " + str(datetime.datetime.now()) + "\n")
				time.sleep(self.sampleRate)  #Change this later to a user-defined sample rate

		except:
			#Error handling/loggin here
			pass

		finally:
			dataFile.close() 

	def kill(self):
		self.onOff.set()
		time.sleep(2)
			
		while len(self.myThreads) > 0:
			self.myThreads.pop()

		self.onOff.clear()

#Catch this number in the setup class, and use it to populate the sample
	#interval in the __init__ method

def specs():
	notDone = True
	placeHolderList = []
	while notDone:
		try:
			x = float(raw_input("Enter the sampling interval in seconds (Ex. 0.5 for a half second between samples): "))
			notDone = False
		except:
			print "\nYou must enter a number.\n"
	myList = []
	myList.append(float(x))
	return myList, placeHolderList, placeHolderList
