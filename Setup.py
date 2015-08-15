#Description:		This class manages the sensor hierarchy and the process of gathering
#			necessary information from the user.  This includes pin, sampling rate,
#			and any other information required for instantiating a sensor object.
#
#Usage:			This class will be instatiated and used by Main.py.  The only sections
#			that should be modified are the models in the __init__ method and their
#			entries in the makeSensor method.  See each respectively for templates
#			and further instructions on how to add support for a new sensor.
#			
#
#Last Modified By:	Stephen Longofono
#			Onofognol@ku.edu
#			7:30 PM | 08-04-2015
#
#Created By:		Stephen Longofono
#			Onofognol@ku.edu
#			9AM | 07-14-2015



import string
import os
import subprocess
#from collections import OrderedDict
from types import ListType, NoneType
import time

class Setup():

	def __init__(self):
		temp = raw_input("Are there any pins you don't want the PNP to check? (y/n): ")
		if temp.lower() == 'y':
			self.omits = []
			while temp.lower() == 'y':
				try:
					self.omits.append(int(raw_input("Enter a pin to omit: ")))
					temp = raw_input("Do you have any more pins to omit? (y/n): ")
				except:
					print "Enter integer values only."
		else:
			self.omits = []
			
		self.customs = {}
		self.extraPins = {}
		self.lastSensor = None
		print "Building class dictionaries . . . \n\n"

		self.myDict = {}

		#These hold all sensors of the supported protocols
		self.GPIO = {}
		self.I2C = {}
		self.Uart = {}


		#Each of these lists is a value of the above dicts, separated here by type of
		#sensor
	
		#'Temperature Sensors'
		self.GPIOTempSensors = []
	
		#'Infrared & Proximity Sensors'
		self.GPIOIRSensors = []
	
		#'Force & Piezo Sensors'
		self.GPIOForceSensors = []
	
		#'Photosensors'
		self.GPIOPhotoSensors = []
	
	
		#Here, the supported sensors are added to the lists
		# Adding a new sensor entails adding the model as a string to the appropriate
		# dictionary entry.  In general, you should be adding to the GPIO sensor 
		# dictionaries, until support for I2C and Uart is added

		self.GPIOTempSensors.append("DS18B20")
		self.GPIOTempSensors.append("One_Wire_General")
		self.GPIOTempSensors.append("Thermocouple_General")
		self.GPIOTempSensors.append("Thermistor_General")
		self.GPIOIRSensors.append("HC_SR501")
		self.GPIOIRSensors.append("IR_General")
		self.GPIOForceSensors.append("Piezo_General")
		self.GPIOForceSensors.append("Force_Transducer_General")
		self.GPIOPhotoSensors.append("Photoresistor_General")
	
	
		################################
	
		#'Temperature Sensors'
		self.I2CTempSensors = []
	
		#'Infrared & Proximity Sensors'
		self.I2CIRSensors = []
	
		#'Force & Piezo Sensors'
		self.I2CForceSensors = []
	
		#'Photoresistors'
		self.I2CPhotoSensors = []
	
		self.I2CTempSensors.append("Thermocouple_General")
		self.I2CTempSensors.append("Thermistor_General")
		self.I2CIRSensors.append("IR_General")
		self.I2CForceSensors.append("Piezo_General")
		self.I2CForceSensors.append("Force_Transducer_General")
		self.I2CPhotoSensors.append("Photoresistor_General")
	
	
		###############################
	
	
		#'Temperature Sensors'
		self.UartTempSensors = []
	
		#'Infrared & Proximity Sensors'
		self.UartIRSensors = []
	
		#'Force & Piezo Sensors'
		self.UartForceSensors = []
	
		#'Photoresistors'
		self.UartPhotoSensors = []
	
	
		self.UartTempSensors.append("Thermocouple_General")
		self.UartTempSensors.append("Thermistor_General")	
		self.UartIRSensors.append("IR_General")
		self.UartForceSensors.append("Piezo_General")
		self.UartForceSensors.append("Force_Transducer_General")
		self.UartPhotoSensors.append("Photoresistor_General")
	
		##############################
	
		#Now that all the lists are populated, they are added to the protocol dicts...
		
		self.GPIO['Force & Piezo Sensors'] = self.GPIOForceSensors
		self.GPIO['Infrared & Proximity Sensors'] = self.GPIOIRSensors
		self.GPIO['Photosensors'] = self.GPIOPhotoSensors
		self.GPIO['Temperature Sensors'] = self.GPIOTempSensors
	
		self.I2C['Force & Piezo Sensors'] = self.I2CForceSensors
		self.I2C['Infrared & Proximity Sensors'] = self.I2CIRSensors
		self.I2C['Photosensors'] = self.I2CPhotoSensors
		self.I2C['Temperature Sensors'] = self.I2CTempSensors
	
		self.Uart['Force & Piezo Sensors'] = self.UartForceSensors
		self.Uart['Infrared & Proximity Sensors'] = self.UartIRSensors
		self.Uart['Photosensors'] = self.UartPhotoSensors
		self.Uart['Temperature Sensors'] = self.UartTempSensors
	
	
		#Finally, the main dict keys are set to point at the other dicts
	
		self.myDict['GPIO'] = self.GPIO
		self.myDict['I2C'] = self.I2C
		self.myDict['Uart'] = self.Uart
	
	def rebuild(self, myDict):
		sensorObjects = []
		for a, b in myDict.iteritems():
			#reversed because we loaded them up as key:value::pin:model
			print "Creating a %s sensor on pin %s..." % (b,a)
			self.makeSensor(b, int(a), True)
			sensorObjects.append(self.lastSensor)
			print "Success..."
			
		return sensorObjects
			

	def printAllSensors(self, myDict):
	
		print "\n"
		for a, b in myDict.iteritems():
		
			print a, b
			print "\n"
	
	
	#This method is used to do some basic filtering of user input by type
	#pass in the list and it will print each element along with a number
	#
	#pass "int" or "float" to guarantee those types, otherwise you will get a string
	
	def getChoice(self, myList, myType):
		
		print "\n"
	
		if type(myList) is ListType:	
			for i in range (0, len(myList)):
				print str(i) + " " + str(myList[i]) + "\n"
	
		else:
			print myList.keys()
	
		notDone = True
	
		while notDone:
			if myType == "int":
				try:
					x = int(raw_input("Enter an integer value: "))
					notDone = False
				except:
					print "You must enter an integer.\n"
	
			elif myType == "float":
				try:
					x = float(raw_input("Enter a float value: "))
					notDone = False
				except:
					print "You must enter a float (Number with a decimal point).\n"
			else:
					x = raw_input("Enter your choice: ")
					try:
						assert(x in myList)
						notDone = False
					except:
						print "That is not in the list.  Please enter a choice in the list as shown.	\n"				
					
				
		print "\nYou chose: " + str(x) + "\n"
		return x
	
	#Add new options here, and  be sure to modify the switch-case in Main.py
	def menu(self):

		choices = ["Stop data collection", "Start/Resume data collection", "Add a sensor", "Disconnect a sensor", "Disconnect all sensors", "Transmit data files", "List all supported sensors", "Quit", "List all connected sensors", "Nevermind..."] 
		result = self.getChoice(choices, "int")
		return result

	def selectInterface(self, myDict):
		print "\n\nSelect the hardware interface for your sensor:\n"
		x = self.getChoice(myDict, "")
		return myDict[x]
	
	def selectSensorType(self, myDict):
		print "\n\nSelect the type of sensor:\n"
		x = self.getChoice(myDict, "")
		
		return myDict[x]
		
	def selectModel(self, myList):
	
		print "\n\nSelect the model of your sensor:\n"
		temp = myList
		temp.append('None of these')
		
		x = self.getChoice(temp, "int")
		if x == len(myList)-1:
			return None
		return myList[x]

	#This method uses the three previous methods to navigate and extract a choice from the sensor hierarchy.
	#Make sure self.lastSensor gets populated!
	def addSensor(self, pin, filepath):
	
		interface = self.selectInterface(self.myDict)
		sensorType = self.selectSensorType(interface)
		model = self.selectModel(sensorType)
		self.makeSensor(model, pin, filepath)
		
		return self.lastSensor			
		
	
	#Add in support for new sensors here after you have written the class in full.
	#Be sure to write static methods if necessary, or omit that part of the template
	#
	# At the bottom is a template for a generic sensor.  It is particularly important
	# that self.lastSensor be populated with a sensor object.  We have used the 
	# convention of specs() as the name for each sensor's static method.  This method
	# should return three lists, the last two of which may be the value None.
	# The first list returned should the parameters, in order, which are required
	# to instantiate the particular model of sensor.
	
	def makeSensor(self,model, pin, filepath, DEBUG=False):
		
		#Add in a new case for your sensor's model here

		if model == "DS18B20":
			if pin != 4:
				print "Error! This sensor should only be used on pin four!"
				self.lastSensor = None
				return
			#get sensor class
			import DS18B20
			#run static methods to get specific info from user in a list
			mySpecifics, customs, extras = DS18B20.specs()
			if DEBUG:
				print mySpecifics
				print customs
				print extras
			#instantiate with the list items returned
			temp = DS18B20.DS18B20(mySpecifics[0], 4, filepath)
			if DEBUG:
				print temp
				print type(temp)		
			self.lastSensor = temp
			if len(customs) > 0:
				self.customs[temp.model] = customs
			if len(extras) > 0:
				self.extraPins[temp.model] = extras
	
		if model == "HC_SR501":
			import HC_SR501
			mySpecifics, customs, extras = HC_SR501.specs()
			temp = HC_SR501.HC_SR501(pin, mySpecifics[0], filepath)
			if DEBUG:
				print mySpecifics
				print customs
				print extras
				print temp
				print type(temp)
			self.lastSensor = temp
			if len(extras) > 0:
				self.extraPins[temp.model] = extras
			if len(customs) > 0:
				self.customs[temp.model] = customs
				

		if model == "HC_SR04":
			self.lastSensor = None
			

#		
#		TEMPLATE
#		 if model == "modelNum":
#				import the model class
#				run the static method to collect model-specific params
#				instantiate using the params
#				assign self.lastSensor to the created object
#			if this sensor uses more than one pin, and has its extraPins populated, load it into setup's
#			dictionary
#	
#			if len(extras) > 0:
#				self.extraPins[temp.model] = extras
#		
#			if this sensor uses a custom file type, and has its customs populated, load it into setup's
#			dictionary
#
#			if len(customs) > 0:
#				self.customs[temp.model] = customs
#
#		If you need an  example of how best to collect the customs and pins, see the General sensor classes'
#		specs() method.  We did not finish implementing them, but they are there as examples.  In this case, you will
#		need to add an optional parameter to the instantiation to populate it with the pins given by the user.
#
#		Make sure the last parameter in each sensor is the file path where the data files should be populated
#
