# dlab_stuff

A selection of the more interesting scripts prepared for my research project and a workshop I taught on Python and the Raspberry Pi.

We designed a plug and play DAQ using the Raspberry Pi, with support for Bluetooth, local Wifi, and internet data transfer.  We
approached the problem by segmenting the program into a user interaction class, a data management class, a hierarchy of sensor classes, and an overall driver. Data was collected concurrently by each sensor object in its own thread, controlled by the main
driver with thread-safe event objects.

The Raspberry Pi workshop was directed at high school students intersted in computer modeling and research.  The workshop tasked the students with creating a weather console, which displays real-time weather data and radar alongside an elevation map for a zip code.  We used the National Map website's LIDAR datasets and the Beautiful Soup library to create a simple desktop app.
