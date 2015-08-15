# Description:		This is the entry point for the JARVIS software.  It interacts with 
#			all the helper classes and manges their interactions.
#
# Usage:		Run as su to start a JARVIS module.  The first line after the imports
#			is a boolean flag for DEBUG mode.  This will toggle messages throughout
#			the software to give a play-by-play of what is going on in the program.
#
#			Before using this software, update the config file to include the file
#			paths you wish to use.  It is also recommended that you compare your
#			current config file to the original (JARVIS.cfg) to make sure you
#			have all the sections required.
#
#			Bluetooth functionality depends on having a Bluetooth FTP app installed
#			on your external device.  The app we used successfully is available on
#			the Google play store:
#
#				"Bluetooth File Transfer"
#				Medieval Software
#				http://www.medieval.it
#
#			There are more detailed instructions in the BluetoothClient.py file,
#			but basically you will need to connect to the device ahead of time
#			using the RPi's Bluetooth manager.  Both client and server need to
#			have each other set as a trusted connection.
#
# Created By:		Stephen Longofono
#			Onofognol@ku.edu
#			8 AM | 08/03/2015
#
# Last Modified By:	Stephen Longofono
#			Onofognol@ku.edu
#			11 AM | 08/10/2015
#
#

import RPi.GPIO as GPIO
import time
import sys
import Setup
import ConfigFileAccess
import traceback

#import GPIOQuery
import SensorInterface
import DataManager
import threading
from types import ListType, NoneType


DEBUG = True
############
#
#Initializations, check dependencies
#Setup init
#GPIO init with results
#Print instructions (button press to signal setup)
#
#Main loop
#
#GPIO.query
#Setup if not None return
#otherwise, wait for interrupt
#
#except KeyBoardInterrupt:
#	Setup menu
#
#
#Initializations

# Thread method to poll the physical button
def btn(myButton, myKill, pin):
		
	while not myKill.is_set():
		if GPIO.input(pin):
			myButton.set()
			time.sleep(2)
			myButton.clear()
		time.sleep(0.2)



def updateConfigSensor(config, sensor, DEBUG):

	myDict = {}
	myDict['model'] = sensor.model
	myDict['customs'] = sensor.customs
	for a,b in myDict.iteritems():
		if DEBUG:
			print "%s, %s" %(a,b)
		config.varWrite(str(sensor.pin), a, b)
	if DEBUG:
		print "Config updated: Sensors!"
		print "Current Pin Lists:"
		print "Frees: "
		print config.varRead('Pins', 'freepins', 'list')
		print "Allows: "
		print config.varRead('Pins', 'allowed','list')


def updateConfigPins(config, frees, allPins, DEBUG):
	if DEBUG:
		print "Updating pins..."
		print "You passed in:\nFree:"
		print frees
		print "All:"
		print allPins

	fpin = ""
	apin = ""
	
	for i in frees:
		fpin += (str(i) + " ")

	for i in allPins:
		apin += (str(i) + " ")

	config.varWrite('Pins', 'freepins', fpin)
	config.varWrite('Pins', 'allowed', apin)
	if DEBUG:
		print "Config updated: Pins!"
		print "Updated to:"
		print "Free Pins:"
		print myConfig.varRead("Pins", "freePins", "list")
		print "Allowed Pins:"
		print myConfig.varRead("Pins", "allowed", "list")

if DEBUG:
	print "Instantiating: "
	print "Setup..."
mySetup = Setup.Setup()
if DEBUG:
	print "[ OK ]\n\n"
	print "Config Parser..."
myConfig = ConfigFileAccess.Configuration()
if DEBUG:
	print "[ OK ]\n\n"
	print "Reading in email address..."
email = myConfig.varRead('Init', 'email', 'str')
if DEBUG:
	print "[ OK ]\n\n"
	print "Reading in data directory..."
filepath = myConfig.varRead('Init', 'datadir', 'str')
if DEBUG:
	print "[ OK ]\n\n"
	print "Reading in SD card directory..."
SDDir = myConfig.varRead('Init', 'sddir', 'str')
if DEBUG:
	print "[ OK ]\n\n"
	print "Instantiating Data Manager..."
DataMan = DataManager.DataManager(None, email, filepath, SDDir, DEBUG)
if DEBUG:
	print "[ OK ]\n\n"
	print "Reading in pin lists..."

activeSensors = []
activeNames = []
customFileTypes = []
allPins = [4,17,27,22,5,6,13,19,18,23,24,25,12,20,21]
prev = False
for i in allPins:
	if myConfig.hasSection(str(i)):
		prev = True
if prev:
	usePrev = raw_input("There is a previous state available, would you like to use it? (y/n):")
else:
	usePrev = 'nope'

if usePrev.lower() == 'y':
	freePins = myConfig.get_frees()
	allPins = myConfig.get_allows()
	checkList = []
	for i in allPins:
		if i in freePins:
			pass
		else:
			checkList.append(i)

	#get all occupied pins in their own list (fancy code golf edition)
	checkList = list(set(allPins)-set(freePins))
	rebuildDict = {}
	if DEBUG:
		print "All Pins: "
		print freePins
		print "Free Pins: "
		print allPins
		print "Checklist:"
		print checkList

	for i in checkList:
		if DEBUG:
			print "Pin: %d" %(int(i))
			print "Strings in config: " + str(myConfig.hasSection(i))
			print "Ints in config: " + str(myConfig.hasSection(int(i)))

		if myConfig.hasSection(i):
		 	rebuildDict[i] = myConfig.varRead(i, 'model', 'str')
			
	if DEBUG:
		print "Rebuilding with:"
		for a, b in rebuildDict.iteritems():
			print "%s : %s" %(a,b)
	activeSensors = mySetup.rebuild(rebuildDict)
	for i in activeSensors:
		print i
		print type(i)
		activeNames.append(i.Name)
	
else:
	myConfig.cleanUp(allPins)
	allPins = [4,17,27,22,5,6,13,19,18,23,24,25,12,20,21]
	myConfig.cleanUp(allPins)
	updateConfigPins(myConfig, allPins, allPins, DEBUG)
	freePins = [4,17,27,22,5,6,13,19,18,23,24,25,12,20,21]
	#NOTE - can't implicitly create a deep copy by freePins = allPins
	if DEBUG:
		print "All pins set to: "
		print allPins
		print "Free pins set to: "
		print freePins

#myGPIO = GPIOQuery.GPIOQuery(allPins, freePins)

if DEBUG:
	print "[ OK ]\n\n"
	print "Setup was successful"

# Intialize thread to watch for button press

button = threading.Event()
button.clear()
buttKill = threading.Event()
btnpin = 26 
GPIO.setmode(GPIO.BCM)
GPIO.setup(btnpin, GPIO.IN)
btnThread = threading.Thread(target=btn, args=(button, buttKill, btnpin))
btnThread.start()

#if DEBUG:
#	print "Checking button thread..."
#	print "Press the button in:"
#	for i in range (0,3):
#		print (3-i)
#		time.sleep(1)
#	if button.is_set():
#		print "Button press detected..."
#		time.sleep(3)
#		if button.is_set():
#			print "FAIL - Event failed to toggle"
#		else:
#			print "[ OK ]\n\n"

if mySetup.omits:
	if DEBUG:
		print mySetup.omits

	for i in mySetup.omits:
		print "Omitting pin %d" %(i)
		if i > 0:
			allPins.remove(i)
	
print "Press the input button to access the setup menu"

keepGoing = True

#Main loop

while(keepGoing):
	try:
		bool = button.is_set()
	
		#if x or bool:
		if bool and keepGoing:
			#if type(x) is ListType:
			#	print "Multiple state changes detected.  Please take care to specify the correct pin for each"
					
			choice = mySetup.menu()
			if DEBUG:
				print "Switchcase choice: %d" %(choice)
				print "Button: " + str(bool) + "\n"
				print "Keep Going flag: " + str(keepGoing) + "\n"
				
			if choice == 0:#Stop data collection
				for i in activeSensors:
					i.onOff.set()#issue stop event

			elif choice == 1:#Start data collection
				for i in activeSensors:
					i.onOff.clear()#clear stop event
					i.getData()

			elif choice == 2:#Add a sensor	
	
				if bool:
					print "Button Detected"
					print "Select the pin you wish to use:"
					if DEBUG:
						print "Creating sensor..."
					temp = mySetup.getChoice(freePins, 'int')
					activeSensors.append(mySetup.addSensor(freePins[temp], filepath))
					if DEBUG:
						print activeSensors[-1].Name + " created\n"
						print "\n\nAll sensors:"
						print activeSensors
					activeNames.append(activeSensors[-1].Name)
					
					if DEBUG:
						print activeNames
						print "[ OK ]\n\n"
						print "Updating lists and config..."
					#myGPIO.setPin(freePins[temp])
					freePins.pop(temp)
					if DEBUG:
						print "Current free pins in main:"
						print freePins
						print "Current allowed pins in main:"
						print allPins
					updateConfigSensor(myConfig, activeSensors[-1], DEBUG)
					updateConfigPins(myConfig, freePins, allPins, DEBUG)
					if DEBUG:
						print "[ OK ]\n\n"
											

				#elif type(x) is ListType:
				#	print "Sensors detected on the following pins: "
				#	for i in x:
				#		print i
				#	temp = raw_input("Do you want to use these pins? (y/n): ")
				#	if temp.lower()=='y':
				#		for i in x:
				#			print "Setting up sensor on pin %d" %(i)
				#			try:	
				#				activeSensors.append(mySetup.addSensor(i))
				#				activeNames.append(activeSensors[-1].Name())
				#				#myGPIO.setPin(i)
				#				freePins.pop(i)
				#				updateConfigSensor(myConfig, activeSensors[-1])
				#				updateConfigPins(myConfig, freePins, allPins)

				#			except:
				#				raise IOError("Failed to add sensor on pin " + str(i))
				#	else:
				#		print "Select the pin you wish to use:"
				#		temp = Setup.getChoice(freePins, 'int')
				#		try:
				#			activeSensors.append(mySetup.addSensor(freePins[temp]))
				#			activeNames.append(activeSensors[-1].Name())
				#			#myGPIO.setPin(freePins[temp])
				#			freePins.pop(temp)
				#			updateConfigSensor(myConfig, activeSensors[-1])
				#			updateConfigPins(myConfig, freePins, allPins)
				#	
				#		except:
				#			raise IOError("Failed to add sensor on pin " + str(freePins[temp]))
				#else:
				#	print "Sensor detected on pin %d" %(x)
				#	temp = raw_input("Do you want to use this pin? (y/n): ")
				#	if temp.lower() == 'y':
#						print "Setting up sensor on pin %c" %x
#						print "Setting up sensor on pin %d" %(x)
#						try:
#							activeSensors.append(mySetup.addSensor(x))
#							activeNames.append(activeSensors[-1].Name())
#							#myGPIO.setPin(x)
#							freePins.pop(x)
#							updateConfigSensor(myConfig, activeSensors[-1])
#							updateConfigPins(myConfig, freePins, allPins)
#								
#							except:
#								raise IOError("Failed to add sensor on pin " + str(x))
#					else:
#						print "Select the pin you wish to use:"
#						temp = mySetup.getChoice(freepins, 'int')
#						try:
#							activeSensors.append(mySetup.addSensor(freePins[temp]))
#							activeNames.append(activeSensors[-1].Name())
#							#myGPIO.setPin(freePins[temp])
#							freePins.pop(temp)
#							updateConfigSensor(myConfig, activeSensors[-1])
#							updateConfigPins(myConfig, freePins, allPins)								
#
#						except:
#							raise IOError("Failed to add sensor on pin " + str(freePins[temp]))
				
			elif choice == 3:#D/C a sensor
				print "Which sensor would you like to remove?"
				temp = mySetup.getChoice(activeNames, "int")
				#myGPIO.freePin(activeSensors[temp].pin)
				freePins.append(activeSensors[temp].pin)
				myConfig.varRemove(str(activeSensors[temp].pin), 'all')
				updateConfigPins(myConfig, freePins, allPins, DEBUG)
				activeSensors[temp].kill()
				activeSensors.pop(temp)
				activeNames.pop(temp)

			elif choice == 4:#D/C all sensors
				while len(activeSensors) > 0:
					#myGPIO.freePin(activeSensors[-1].pin)
					activeSensors[-1].kill()
					myConfig.cleanUp(allPins)
					activeSensors.pop()
					activeNames.pop()
					
				freePins = [4,17,27,22,5,6,13,18,19,23,24,25,12,20,21]
				updateConfigPins(myConfig, allPins, allPins, DEBUG)
						

			elif choice == 5:#Transmit data
				for i in range(0, len(activeSensors)):
					activeSensors[i].onOff.set()#Signal threads to stop.
				temp = mySetup.getChoice(["Bluetooth", "SD Directory", "Email"], "int")
				if temp == 0:#Bluetooth
					DataMan.transmit("BT")
				elif temp == 1:#SD directory
					DataMan.transmit("SD")
				else:#Email
					DataMan.transmit("")
	
				temp = raw_input("Do you want to delete the data collected? (y/n): ")
				if temp.lower() == 'y':
					DataMan.cleanup('out.tar.gz')
				for i in range(0, len(activeSensors)):
					activeSensors[i].onOff.clear()
				print "Data is not being collected..."
			
			elif choice == 6:#list all supported sensors
				print "\n\n_____GPIO SENSORS_____"
				for a,b in mySetup.GPIO.iteritems():
					print "%s : %s" %(a,b)
				print "\n\n_____I2C SENSORS_____"
				for a,b in mySetup.I2C.iteritems():
					print "%s : %s" %(a,b)
				print "\n\n_____Uart Sensors_____"
				for a,b in mySetup.Uart.iteritems():
					print "%s : %s" %(a,b)
				

			elif choice == 7:#Quit
				if DEBUG:
					print "Exiting..."
				buttKill.set()
				while len(activeSensors) > 0:
					if DEBUG:
						print "Sensors left: "
						print len(activeSensors)
					updateConfigPins(myConfig, freePins, allPins, DEBUG)
					activeSensors[-1].kill()
					activeSensors.pop()
				if DEBUG:
					print "All sensors removed"
					print "Ending main loop..."						
				#clean exit
				#myGPIO.freeAll()
				keepGoing = False
			elif choice == 8:#List active sensors
				print "Active sensors installed:"
				for i in activeNames:
					print i	
	
			elif choice == 9:#Nevermind...
				print "Doing nothing..."
				print "Press the input button to access the menu."
			else:
				print "Invalid selection.  Doing nothing."
				print "Press the input button to access the menu."
			
##Catches for main loop
	except Exception as err:
		
		if DEBUG:
			print "Error received.  Details:"
		print type(err)
		print err
		print err.args
		traceback.print_exc()
		print "If you were transmitting data files, send them manually to avoid accidentally deleting them.  You can then resume using the previous setup when you restart the program"
		buttKill.set()
		time.sleep(2)
		sys.exit(-1)
		#insert more specific errors here with apropriate handling
#End While

if DEBUG:
	print "\n\nClean teardown.\n\nExiting..."
else:
	print "Exiting..."
