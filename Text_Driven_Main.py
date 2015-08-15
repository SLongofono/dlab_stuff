#Description:       This is the "Main" file for the communicator module software
#
#Usage:             This file will be automatically called by a system script
#		                at boot, though it can be called directly with no arguments
#		                via the command line: python Main.py
#
#                   The following lines should be changed to reflect your local
#		                environment:
#       
#                   Line 59 : Change this path to the path where your 
#		                communicator module software will reside.
#                   Line 219: Change this email address to the one used to set
#		                up the SSMTP and Mpack utilities
#                   Line 220: Change this to the password associated with the
#		                RPi email account
#
# 
#Last Modified By:  Stephen Longfono
#                   Onofognol@ku.edu
#                   12PM | 06/01/2015
#
#Created By:        Stephen Longofono
#                   Onofognol@ku.edu
#                   10AM | 03/01/2015
#
#Adapted from code written by Jesse Merrit on September 8, 2012
#Retrieved from his repository at https://github.com/jes1510/raspberry-gpio-email
#Provided under the GNU General Public License and modified here for personal educational purposes.
#
#
import string
import urllib
import time
import imaplib
import email
import sys
import traceback
import smtplib
import os
import select
import subprocess
from subprocess import Popen
import signal
from datetime import datetime
import ConfigParser
import email.mime.application
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
import ImageCapture
import AddressHandler
import Maintenance
import TTS
#import email.encoders
#import email.mime.text
#import email.mime.base

if sys.platform == 'linux2' :
	import syslog

class mailError(Exception): pass

class Configuration():

	def __init__(self):
		self.configFile = ConfigParser.SafeConfigParser()
		self.configFile.read('/home/pi/jarviss2015/control.cfg')        #Change this to your local path
		self.whiteList = {}
		self.whiteList = self.configFile.get('Email', 'WhiteList').split(' ') #delimit on space
		self.returnAddy = {}
		self.returnAddy = self.configFile.get('Email', 'Carrier').split(' ')
		self.sleepTime = self.configFile.getint('Email','Interval')
		self.approvedSubject = self.configFile.get('Email','Subject')
		self.verbose = self.configFile.get('Configuration','Verbose')
		self.displayTime = self.configFile.get('Configuration', 'DisplayTime')
		self.warningTime = self.configFile.get('Configuration', 'WarningTime')
		self.holdTime = self.configFile.get('Configuration','HoldTime')
		self.debounceTime = 5.0
		self.transitTime = self.configFile.get('Configuration','TransitTime')
		self.tempDirectory = self.configFile.get('Configuration','TempDirectory')

def timedQuery():
	timeout = 30
	start = time.time()
	sys.stdin.flush()
	while(True):
		timer = timeout - (time.time() - start)
		read, write, exce = select.select([sys.stdin], [], [], timeout)
		if read:
			message = sys.stdin.readline()
			sys.stdin.flush()
			print "Sending: " + message + "\n"
			return message
		if timer < 0:
			print "Timeout, exiting...\n\n"
			break
		
	return "--No reply or timed out--"

def stripPunctuation(message):
	message = message.translate(None, string.punctuation)
	return message

#subprocess launch reference## def execCmd(cmd):
#	print "Executing: " + cmd + "..."
#	output = subprocess.Popen(cmd,close_fds=True, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0]
#	return

def leave():
	sys.exit(0)

class Mailmanager():

	def __init__(self, login, password):
		self.login = login
		self.password = password
	
		self.mail = imaplib.IMAP4_SSL('imap.gmail.com')
		self.mail.login(login,password)
	
	def getMail(self):
		self.mail.list()
		status, msgs = self.mail.select()
		if status == 'OK':
			result, data = self.mail.uid('search',None, "(UNSEEN)")
			if data[0] != '':
				time.sleep(0.1)
				latest_email_uid = data[0].split()[-1]
				result, data = self.mail.uid('fetch', latest_email_uid, '(RFC822)')
				raw_email = data[0][1]   
				message = email.message_from_string(raw_email)
				name, sender = self.get_sender(message)
				subj = email.utils.parseaddr(message['Subject'])[1]
				text = self.getBody(message) 
				return name, sender, subj, text
			
			else :
				return 0,0,0,0
		else :
			raise mailError('Bad status from server')

	def stop(self) :
		self.mail.close()
		self.mail.logout()        
		
		
	def sendEmail(self, recipient, subject, message) :           
		smtpserver = smtplib.SMTP("smtp.gmail.com",587)
		smtpserver.ehlo()
		smtpserver.starttls()
		smtpserver.ehlo
		smtpserver.login(login, password)
		msg = email.MIMEMultipart.MIMEMultipart('mixed')	
			
		msg['From'] = login
		msg['To'] = recipient
		msg['Subject'] = subject
		
		#msgText = MIMEText('<b>%s</b><br><img src="cid:"' + config.pictureName + '"><br>' % message, 'html')   
		msg.attach(MIMEText(message))   # Added, and edited the previous line
		
		try :
			numList = sender.split('.')
			number = numList[1]
			assert int(number)
									
		except :  
			try :
				attachment = config.tempDirectory + '/' + config.pictureName
				fp = open(attachment, 'rb')                                                
				img = MIMEImage(fp.read())
				fp.close()
				msg.attach(img)
				
			except Exception, detail :
				pass
		#header = 'To:' + recipient + '\n' + 'From: ' + login + '\n' + 'Subject: ' + subject+ ' \n'
		#msg = header + '\n '+ message + '\n\n'   
		smtpserver.sendmail(login, recipient, msg.as_string())
		smtpserver.quit()
		#os.system("rm " + attachment)
		

	def get_sender(self,email_message) :
		sender = email.utils.parseaddr(email_message['From'])    
		name = sender[0]
		addr = sender[1]
		return name, addr

	def getBody(self, email_message_instance):
		maintype = email_message_instance.get_content_maintype()
		if maintype == 'multipart':
			for part in email_message_instance.get_payload():
				if part.get_content_maintype() == 'text':
					return part.get_payload()

		elif maintype == 'text':
			return email_message_instance.get_payload()

class Commands() :
	
	def _getIP(self):
		whatismyip = 'http://automation.whatismyip.com/n09230945.asp'
		return urllib.urlopen(whatismyip).readlines()[0]

	def ip(self) :
		p = os.popen("ip addr show wlan0 | grep inet").readline().split()[1]
		ip = p.split('/')[0]
		#ip = self._getIP()
		#print ip     
		mailmanager.sendEmail(sender, 'Local IP', ip)
		time.sleep(5.0)

	def status(self) :      
		pass

config = Configuration()

if __name__ == '__main__' :
	config = Configuration()
	commands = Commands()

	timeCounter = 0

	state = 'off'    

	login = "email@email.com"   #Change this to the email account you configured for use with the SSMTP client
	password = "hashtagYOLO"           #This should be the password associated with that account
	
	mailmanager = Mailmanager(login, password)
	mail = mailmanager.mail
	camera = ImageCapture.ImageCapture()
	maint = Maintenance.Maintenance()
	speaker = TTS.TTS()
	
	try :
		
		while True:            
			time.sleep(3)
			number = 0
			
			try :
				name, sender, subj, text = mailmanager.getMail()     
				
				if text :                
					text = text.strip()
					text = text.lower()					
					
					try :
						numList = sender.split('.')
						number = numList[1]
						assert int(number)						
					except :
						pass                    
					
				if sender in config.whiteList or number in config.whiteList:  
					if text :
					
				                if 'speak:' in text :
							print sender + " sent a message:\n"
							print text
							text = text.replace("speak:", "")
							speaker.TTS_speak(text)
							
						elif 'picture' in text :
							print sender + " sent an image request\n"
							#out = os.system("fswebcam -c ~/.fswebcam.conf")
							#time.sleep(3)
							#out = os.system("mpack -s '''testing''' /home/pi/Desktop/pictures/lastcapture.jpg Stephjlong@gmail.com")
							print camera.getImage()
							if sender in config.whiteList:
								#temp = sender
								#if temp[0] == "1":
								#	temp = temp[1:len(temp)] #trim country code
								print camera.sendImage(sender)
							else:
								#temp = number
								#if temp[0] == "1":#trim country code
								#	temp = temp[1:len(temp)]
								print camera.sendImage(number)							


						elif 'listen' in text:
							print "Listening initiated...\n"
							print "Enter your reply: "
							message = timedQuery()
							if sender in config.whiteList:
								mailmanager.sendEmail(sender, "JARVIS_REPLY", message)
							else:
								addyHandler = AddressHandler.AddressHandler()
								carrier = ""
								for i in range(0, len(config.whiteList)):
									if config.whiteList[i] == number:
										carrier = config.returnAddy[i]
								replyAddy = addyHandler.getSMS(number, carrier)
								if replyAddy == None:
									mailmanager.sendEmail(sender, "JARVIS_REPLY", message)
								if replyAddy[0] == "1":
									replyAddy = replyAddy[1:len(replyAddy)]
								mailmanager.sendEmail(replyAddy, "JARVIS_REPLY", message)

						elif 'exit' in text:
							print "Exiting...\n"
							leave()

						elif 'getlog' in text:
							print "Sending Maintenance File...\n"
							maint.query()
							print "Sending Log File...\n"
							maint.sendReport()

						elif 'makeclean' in text:
							print "Resetting Logs...\n"
							maint.query()
							maint.cleanUp()
			
						elif 'reboot' in text: #NOTE - must have set up shutdown permissions for this to work
							out = os.system("sudo /sbin/reboot")
				

			except Exception, detail :
				maint.gmailFailed()				
				err = traceback.print_exc()
								
				try :
					#mailmanager.mail.close()
					timer(config.sleepTime)
					waitUntil(10, state=False)                    
					mailmanager.__init__(login, password)
					time.sleep(3)
					
				except Exception:
					pass
			time.sleep(.1)
	except mailError, detail:
		err = traceback.print_exc()
		print str(err)
		print "Something went wrong with gmail...\n"
		maint.gmailFailed(str(err))
		
	except SystemExit() :
		leave()
	except KeyboardInterrupt() :
		leave()
