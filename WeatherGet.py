import urllib2
from urllib import urlretrieve
from bs4 import BeautifulSoup
import re               #for splitting string with regex
import os

#Change this to your zip code for now.  Later on, this can be populated with
#command line arguments when it is called from the WConsole.py program
zip = "66049"

#The mobile website is more simple and less likely to change.  Mobile phones
#vary in software, platform, and ability, so the site itself is limited to
#only basic html for compatibility.
url = "http://m.wund.com/cgi-bin/findweather/getForecast?brand=mobile&query=" + zip

print "Connecting to wunderground . . .\n"

page = urllib2.urlopen(url)

soup = BeautifulSoup(page)

print "Writing raw data to testDump file . . .\n"

temp = open("testDump.txt", "w")
temp.write(soup.prettify().encode('UTF-8'))#best method name ever
temp.close()

print "Parsing weather data . . .\n"

#This is a simple way to catch problems.  Typically, the OS will return
#a zero if everything went well when a command was executed.  This
#setup allows us to catch the number returned and see if anything went
#wrong.

#
sysReturn = os.system("python strip.py")
if sysReturn != 0:
	print "Oops, check the testDump.txt file for unusual data....\n"

#Below is another way to catch problems.  Some things within the try: section
#have the potential to crash the program.  The except: section will only
#run if something goes wrong.  Here, we use some built-in features of exceptions
#to print what went wrong.

try:
	print "Retrieving radar image . . .\n"
	for link in soup.find_all('a'):#grab all tags with the a keyword
	
	    #if any of these have a 'href' tag, check if it is the link to the radar
		if "feature=zoomradar" in str(link.get('href')):
			#print our the link
			imageUrl = "http://m.wund.com" + str(link.get('href'))
			print imageUrl
	
	page2 = urllib2.urlopen(imageUrl)
	soup2 = BeautifulSoup(page2)
	
	#grab all 'img' tags
	for link in soup2.find_all('img'): 
	
	    # if the link source has "radblast"
		if "radblast" in str(link.get('src')):
			theImage = str(link.get('src'))
    
    #Finally, we use our url to download the image.  It is converted to .gif
    #format and resized for our GUI.
	urlretrieve(theImage, "radar.gif")
	sysReturn = os.system("convert radar.gif -resize 75% radar.gif")


except Exception as err:
	print "Something blew up\n"
	print type(err)
	print err.args
	print err

