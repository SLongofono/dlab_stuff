import string
import re

#########
#This method 'normalizes' whitespace in a string.  It removes tabs and newlines,
#and replaces any blocks of spaces with a single space

def stripWhiteSpace(s):
	#replace tabs with nothing
	s = s.replace("\t", "")
	#replace newlines with nothing
	s = s.replace("\n", "")
	#replace adjacent spaces with a single space
	while "  " in s:
		s = s.replace("  ", " ")
	return s

#########
#This method removes html tags by systematically removing the indices between
#angle brackets.  It assumes that the input is valid html, implying that
#every open angle bracket has a matching close angle bracket.

def removeTags(s):
	notDone = True
	while(notDone):
		openBracket = s.find("<")
		closeBracket = s.find(">")
		if openBracket == -1:
			notDone = False
		else:
			s = s[0:openBracket] + s[(closeBracket + 1):len(s)]
			#remove all chars between brackets, inclusive
	return s

#########
#This method was prepared to parse the raw text from a specific table on the
#www.wunderground.com website.  The find method is used to locate the beginning
#of certain fields within the original table (in order), which are then used
#to delineate those fields and their data into a list of strings.

def weatherParse(s):
	
	#Abbreviations to help keep track of what we're looking at
	hum = s.find("Humidity")
	dew = s.find("Dew Point")
	win = s.find("Wind")
	winG = s.find("Wind Gust")
	pres = s.find("Pressure")
	con = s.find("Conditions")
	vis = s.find("Visibility")
	uv = s.find("UV")
	clo = s.find("Clouds")
	max = s.find("Yesterday's Maximum")
	min = s.find("Yesterday's Minimum")
	sun = s.find("Sunrise")
	set = s.find("Sunset")
	end = s.find("Moon")
	result = ""

	myList = []

    #The find method returns -1 if it can't find the argument.  Wind gust is not
    #always present, so we need to check if it is, and act accordingly
	if(winG == -1):
	    
	    #Each of our abbreviated names represents the index where that label
	    #begins.  Instead of trying to work out some way to separate the labels
	    #from the values, we simply split our string at the index of the next
	    #label.  This works so long as we know how many labels to expect and
	    #the order they are in.
	    
		myList.append(s[0:hum])
		myList.append(s[hum:dew])
		myList.append(s[dew:win])
		myList.append(s[win:pres])
		myList.append(s[pres:con])
		myList.append(s[con:vis])
		myList.append(s[vis:uv])
		myList.append(s[uv:clo])
		myList.append(s[clo:max])
		myList.append(s[max:min])
		myList.append(s[min:sun])
		myList.append(s[sun:set])
		myList.append(s[set:end])
	else:
		myList.append(s[0:hum])
		myList.append(s[hum:dew])
		myList.append(s[dew:win])
		myList.append(s[win:winG])
		myList.append(s[winG:pres])
		myList.append(s[pres:con])
		myList.append(s[con:vis])
		myList.append(s[vis:uv])
		myList.append(s[uv:clo])
		myList.append(s[clo:max])
		myList.append(s[max:min])
		myList.append(s[min:sun])
		myList.append(s[sun:set])
		myList.append(s[set:end])

	return myList
	
#Open the output file of our web scraper
x = open("testDump.txt", "r")
rawString = x.read()
x.close

#remove tags
rawString = removeTags(rawString)

#remove whitepace with re methods (\s refers to whitespace)
rawString = re.sub("\s", " ", rawString)

#remove excess space and anything re missed with our custom method
rawString = stripWhiteSpace(rawString)

#find our table values by using a unique nearby word
start = rawString.find("Observed")
end = rawString.find("Moon")
rawString = rawString[start:end]

# now trim off the excess since we have isolated what we want
start = rawString.find("Temperature")
rawString = rawString[start:]

# split it into a list, with a label and the corresponding value for each element
myList = weatherParse(rawString)

#Open a text file and write the number of entries as the first line
output = open("tableDump.txt", "w")
output.write(str(len(myList)) + "\n")

for item in myList:
	output.write(item)
	output.write("\n")

output.close()	

