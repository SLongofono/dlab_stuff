import Tkinter as tk    #The GUI module
import os               #Allows system commands to be called

class Display(tk.Frame):
	def __init__(self, master=None):
		tk.Frame.__init__(self, master)
		self.grid()
		self.createWidgets()
	
	def createWidgets(self):
		self.quitButton = tk.Button(self, text='Quit',command=self.quit)
		self.quitButton.grid(padx=5, pady=5, row=14, column=2)
		self.pic = tk.PhotoImage(file="radar.gif")
		self.pic2 = tk.PhotoImage(file="plot.gif")
		self.can2 = tk.Canvas(self, width=326, height=326)
		self.can = tk.Canvas(self, width=326, height=326)

		#The anchor option below refers to how the image will be
		#positioned within the canvas.  Here, we have entered the 
		#coordinates of the exact center of the canvas. Anchor will 
		#center the image at these coordinates.
		self.can2.create_image(163,163,anchor=tk.CENTER, image =self.pic2)
		self.can.create_image(163,163, anchor=tk.CENTER, image=self.pic)

		#The grid manager determines the position and any padding
		#sticky option refers to what edge it will align with
		# from N,S,E,W.  Stretching is done by specifying two
		#attributes concatenated, eg E+W means stretch horizontally
		#rowspan means this object will overwrite 10 rows. This 
		# will stop the grid manager from expanding the entire row
		# to the size of the image
		self.can.grid(row=0, column=0, padx=5, sticky=tk.N, rowspan=6)
		self.can2.grid(row=6, column=0, padx=5, sticky=tk.N, rowspan=9)
		
		#Here, we add a label for the elevation plot. You may need to adjust 
		#the position of this widget based on the size of your images
		self.chartLabel = tk.Label(self, text=" Meters Above Sea Level ")
		self.chartLabel.grid(row=6, column=0) 
		self.buildTable()

	def buildTable(self):

		#make a new frame nested within our main one
		self.table = tk.Frame(self)
	
		#open our input file, whih was filled by weatherGet script
		input = open("tableDump.txt", "r")
		valuesList = []
		
		#while there are lines left to read, load them into a list
		for lastLine in input.readlines():
			valuesList.append(lastLine)
		input.close()
		
		#The first line of our file comes in handy here
		size = int(valuesList[0])

		#create text labels within our table frame and grid them
		#note that by specifiying self.table, the grid manager 
		#knows to arrange the labels within this inner frame
		
		
		#Here, I've added a word wrap for entries longer than 40 characters
		#This is a workaround to the behavior of the grid tool; it will stretch
		#the column to fit the text, which ditorts the whole GUI.  Instead,
		#if it finds a long entry, it sets the wrap flag to true and splits
		#the excess into the 'otherpart' string, and creates a separate label
		#for the excess text
		for i in range (1, size):
			myText = valuesList[i]
			otherPart = ""
			wrap = False
			
			if len(myText) > 40:
				otherPart = myText[39:]
				myText = myText[:39]
				wrap = True
			
			#The frame widget allows for borders to be specified.  By placing
			#each label in a frame with a thin border, the effect is a
			#table when they are all placed next to each other.
			temp = tk.Frame(self.table, borderwidth=1, relief=tk.SOLID)
			temp2 = tk.Label(temp, text=myText).grid(sticky=tk.W + tk.E)
			temp.grid(sticky=tk.W+tk.E)
			
			if wrap:
				temp = tk.Frame(self.table, borderwidth=1, relief=tk.SOLID)
				temp2 = tk.Label(temp, text=otherPart).grid(sticky=tk.W + tk.E)
				temp.grid(sticky=tk.W+tk.E)
					
		#grid our table frame into the main one
		self.table.grid(row=0, column=2, padx=25, pady=25, sticky=tk.E + tk.W, rowspan=15)

#Below is the code that runs our application.  You will need to change the 
#'myDir' variable to the path where you saved your programs and data.

myDir = "/home/pi/jarviss2015/BootCamp/WConsole/"

print "\nFetching weather data . . .\n"
output = "python " + myDir + "weatherGet.py"
sysReturn = os.system(output)

#This calls the script that processes the LIDAR data and outputs the x.txt,
#y.txt, and z.txt files.  We will not use it, but I left it here for reference
#so you know where it is called and how it fits in.
#print "\nReticulating LIDAR . . \n"
#output = "python " + myDir + "getLIDAR.py"
#sysReturn = os.system(output)

print "\nGenerating Elevation plot . . .\n"
output = "python " + myDir + "plot.py"
sysReturn = os.system(output)


#The final step is instantiating our display and showing it.
app=Display()
app.master.title('Weather Console')
app.mainloop()
