from mpl_toolkits.mplot3d import Axes3D     #For 3D plotting
import matplotlib.pyplot as plot            #displays figures and plots
import numpy as np                          
from scipy.interpolate import griddata
import os

print "Loading data into plotter . . \n"

header = open("LIDARheader.txt", "r")
temp = header.readLine()
header.close()
extrema = temp.split(' ')
maxes = []
mins = []

for i in range(0,3):
    maxes.append(extrema[i])

for i in range(3,6):
    mins.append(extrema[i])

#If you decide to process LIDAR data on your own, the laspy module has a header
#method that provides information about the data within.  I have left this here
#for reference.  The supplied LIDARheader.txt file was prepared using the 
#maximum and minimum values specified by the laspy.header method
#input = laspy.file.File("KS.las", mode="r")
#maxes = input.header.max
#mins = input.header.min

#Here, we load our raw data into numpy arrays
xVals = np.loadtxt("xVals.txt")
yVals = np.loadtxt("yVals.txt")
zVals = np.loadtxt("zVals.txt")


# define grid.

print "Interpolating . . .\n"

#Here, we set up the interval (xi, yi) of our graph and use meshgrid to
#interpolate in 2 dimensions.  By using the extrema from our header file,
#we will ensure that the graph has no unused space.
xi = np.linspace( mins[0],maxes[0],100)
yi = np.linspace(mins[1],maxes[1],100)
X,Y = np.meshgrid(xi,yi)

#Here, we used the gridata method, our raw values, and our 2D interpolation
#to map a third dimension.  The method of nearest points will use the values
#of the nearest points to extrapolate points along the meshgrid.  They are then
#connected with straight lines.
Z = griddata((xVals, yVals), zVals, (X,Y), method='nearest')

print "Plotting and converting . . \n"

fig=plot.figure()
ax = fig.add_subplot(111, projection = '3d')
ax.plot_surface(X,Y,Z,rstride=6,cstride=6,cmap='hot')
#ax.plot_wireframe(X,Y,Z,rstride=6, cstride=6, cmap='hot')

#Here, we place a label to provide context for our plot.  Each dataset was
#centered at the latitude and longitude of the zip code provided.
#xytext sets the position of the label, here designated as (0, 1) with respect
#to pixels measured from the lower left hand side
#easting is chosen by you, based on the dataset you retrieved.

easting = "Center at 39N, 40W"
plot.annotate(easting, xy=(0,0), xytext=(0,1), textcoords="figure pixels")

#matplotlib uses .png images by default, but Tkinter will need another format
#We use ImageMagick to convert our plot appropriately
plot.savefig('plot.png')
sysReturn = os.system("convert plot.png plot.gif")
sysReturn = os.system("convert plot.gif -resize 50% plot.gif")
