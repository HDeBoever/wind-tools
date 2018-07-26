# Analyse wind and other relevant data by looking at data stored in Pandas dataframes.
# Created by Henri De Boever on 2018/05/11

# General Approach:
# Generate windspeed and wind direction data for all the stations for which we have data for.
# Store the data for a certain date (or date range) in a pandas dataframe that could then be plotted onto
# a map using a Basemap. A simpler version could be attempted where we overlay the graphs of multiple
# stations on the same plot.

from collections import OrderedDict
from datetime import datetime, date, timedelta
from mpl_toolkits.basemap import Basemap, cm
import matplotlib.pyplot as plt
import os.path as path
import datetime as dt
import numpy as np
import pandas as pd
import sys, os, shutil


# Globally declared lists containing station data
# -----------------------------------------------------------------------------------------------
# Latitude and Longitude of significant places
lats = [49.3502777777778, 49.9519444444444, 49.9984722222222, 49.4666666666667,
49.4666666666667, 48.4244027777778, 49.2089111111111, 49.8046111111111, 48.5476944444444, 49.4675, 49.0544444444444,
49.2166666666667, 49.0544444444444, 49.3303888888889, 49.8345555555556, 49.8345555555556, 49.3372222222222,
49.1058958333333, 48.7750222222222, 48.7833333333333, 49.4579966666667, 49.4866111111111, 48.3950555555556,
49.0039111111111, 49.2953527777778, 49.1947222222222, 49.2953527777778, 49.1947222222222,
49.2752777777778, 48.4134166666667, 48.4130725, 48.6472222222222, 48.7839075, 49.4666666666667,
48.42278, 48.29798, 49.08222, 48.37669, 48.43197, 49.34, 49.92, 48.57492, 49.48778, 49.78321,
49.31658, 48.92111, 49.38331]

lons = [-124.160277777778, -125.273055555556, -125.195472222222, -124.683333333333,
-124.9, -123.2251, -123.808891666667, -124.525222222222, -123.237033333333, -123.9125, -123.87,
-123.95, -123.933333333333,-123.264666666667, -124.496805555556, -124.500277777778, -124.393888888889,
-123.3033675, -123.128077777778, -123.05, -123.7152625, -124.434944444444, -123.304908333333,
-123.133344444444, -123.121869444444, -123.183888888889, -123.188611111111, -123.187236111111,
-123.25, -123.32525, -123.325004722222, -123.425833333333, -123.044745, -123.916666666667,
-123.3875, -123.5314, -125.7725, -123.921, -123.4393, -123.72, -125, -123.5299, -123.2995, -123.1612,
-124.9268, -125.5411, -126.5431]

station_names = ['BALLENAS ISLAND', 'CAMPBELL RIVER A', 'CAPE MUDGE CS', 'CHROME ISLAND',
'COMOX A', 'DISCOVERY ISLAND', 'ENTRANCE ISLAND', 'GRIEF POINT', 'KELP REEFS', 'MERRY ISLAND LIGHTSTATION', 'NANAIMO A',
'NANAIMO DEPARTURE BAY', 'NANAIMO HARBOUR', 'POINT ATKINSON', 'POWELL RIVER', 'POWELL RIVER A', 'QUALICUM BEACH AIRPORT',
'SANDHEAD CS', 'SATURNA CAPMON CS', 'SATURNA ISLAND CAMPBELL SCIENTIFIC', 'SECHELT AUT', 'SISTERS ISLAND', 'TRIAL ISLAND',
'TSAWWASSEN FERRY AUTO', 'VANCOUVER HARBOUR CS', 'VANCOUVER INTL A', 'VANCOUVER JERICHO', 'VANCOUVER SEA ISLAND CCG',
'VANCOUVER UBC', 'VICTORIA GONZALES CS', 'VICTORIA GONZALES HTS', 'VICTORIA INTL A', 'SATURNA ISLAND CS', 'MERRY ISLAND',
'VICTORIA HARBOUR A', 'RACE ROCKS', 'TOFINO A', 'SHERINGHAM POINT', 'ESQUIMALT HARBOUR', 'HALIBUT BANK BUOY',
'SENTRY SHOAL BUOY', 'MALAHAT', 'HOWE SOUND PAM ROCKS', 'SQUAMISH AIRPORT', 'PORT ALBERNI AUT', 'AMPHITRITE POINT', 'ESTEVAN POINT CS']

# ------------------------------------------------------------------------------------------------

# A helper function that calculates the distance between given lat/long pairs taking into account
# the curvature of the earth using the haversine formula: http://en.wikipedia.org/wiki/Earth_radius#Mean_radius
def great_circle_distance(start_lat, start_long, end_lat, end_long):
	# Mean Equatorial Radius of Earth in metres
	earth_radius = 6378100
	# Convert to radians
	start_lat = np.radians(start_lat)
	start_long = np.radians(start_long)
	end_lat = np.radians(end_lat)
	end_long = np.radians(end_long)

	# Calculate distance with the haersine formula implementation
	d_lat = end_lat - start_lat
	d_long = end_long - start_long
	a = np.sin(d_lat/2)**2 + np.cos(start_lat) * np.cos(end_lat) * np.sin(d_long/2)**2
	c = 2 * np.arcsin(np.sqrt(a))
	return (earth_radius * c)

# This function returns an ordered dict containing each station's distance to all others
# Not currently being used by the program, but may be useful at a later time
def generate_distances():

	station_distances = {}
	# initialize an n x n matrix
	distances_matrix = [[np.nan for i in range(len(station_names))] for i in range(len(station_names))]
	# Set the distances from any station to itself to be 0
	for i in range(0, len(distances_matrix)):
		distances_matrix[i][i] = 0
	for i in range(0, len(distances_matrix)):
		for j in range(0, len(distances_matrix)):
			# using the great circle formula, get the distances for each station to all the others
			# round the result to two digits after the decimal
			distances_matrix[i][j] = round(great_circle_distance(lats[i], lons[i], lats[j], lons[j]), 2)
			station_distances[station_names[i], station_names[j]] = distances_matrix[i][j]

	# station_distances contains the names of stations as the key, and the value is the distance in meters between both stations
	return station_distances

# A helper function that takes in a list of vector data by station name
# and returns a sanitized version of the station name associated with its data for further processing
# This function is called by generate_SWAN_input(), idw_interpolation() and plot_map()
def get_data_from_vector(vector_list):

	data = []
	for item in vector_list:
		name = item[0]
		wind_speed = item[1]
		wind_direction = item[2]
		tokens = name.split('_')
		# Get rid of the station_id or the climate_id in the name
		tokens.pop()
		name = ' '.join(tokens)
		name = name.replace("_"," ").upper()
		data.append((name, wind_speed, wind_direction))
	return data

# Testing creating a dictionary from the global station names and coordinates, this function is not currently being called anywhere
def create_station_dict():
	station_locations = {}
	for index, station in enumerate(station_names):
		station_locations[station] = (lats[index], lons[index])
	print(station_locations)
	return station_locations

# A helper function that takes time in YYYY-MM-DD hh:mm and returns YYYYMMHH.hhmmss
def convert_time_to_ISO(time):
	iso_time = time.replace('-', '').replace(':', '').replace(' ', '.')
	iso_time = iso_time + "00"
	return iso_time

# opens a file and writes wind X-comps and wind Y-comps to a text file in the format that SWAN can read
def generate_SWAN_input(points, vector_data, time):

	print("\nFormatting data for SWAN for time %s ..." % (time))
	x_components = []
	y_components = []
	filename = "swan_input_data"
	with open(filename, "a") as f:
		# get the ISO time from the input time
		iso_time = convert_time_to_ISO(time)
		# Check if the file is empty
		if(os.stat(filename).st_size != 0):
			# if not empty, write a new line before appending a new time step
			f.write('\n' + iso_time)
		else:
			# if it is empty, then start writing at the top of the file
			f.write(iso_time)

		# Find the distance from all the stations to that point
		data = get_data_from_vector(vector_data)

		iterator = 0
		for item in points:
			#print(item)
			point_lat = item[0]
			point_long = item[1]
			point_wind_speed = 0
			point_wind_direction = 0
			inverse_distance_sum = 0
			data_with_distances = []
			distances_from_stations_to_point = []

			# Compute the distances
			for i in range(0, len(station_names)):
				distance = great_circle_distance(lats[i], lons[i], point_lat, point_long)
				distances_from_stations_to_point.append((station_names[i], round(distance, 2)))

			#print(distances_from_stations_to_point)
			# Combine both lists to get the items that we need
			# It would be possible to add a distance restriction in this loop here
			for item in distances_from_stations_to_point:
				#print(item)
				for item2 in data:
					if(item[0] == item2[0]):
						# Convert metres to kilometres before appending
						data_with_distances.append((item2[0], item2[1], item2[2], (item[1]/1000)))
						break

			# Interpolation here: Calculate point wind speed and wind direction for a given unknown location
			temp1 = 0.0
			temp2 = 0.0
			for item in data_with_distances:
				# Get the sum of the inverse distance squared for each point
				# If the distance is less than 70kms, include the point
				if(item[3] <= 40):
					inverse_distance_sum += (1 / (item[3])**2)
				else:
					pass
			for item in data_with_distances:
				# If the distance is less than 70kms, include the point
				if(item[3] <= 40):
					if(not np.isnan(item[1])):
						temp1 = (item[1] / (item[3])**2)
						point_wind_speed = point_wind_speed + temp1
						#print("wind spd: %s" % str(point_wind_speed))
					if(not np.isnan(item[2])):
						temp2 = (item[2] / (item[3])**2)
						point_wind_direction = point_wind_direction + temp2
						#print("wind dir: %s" % str(point_wind_direction))
				else:
					pass
			try:
				#print(point_wind_speed/inverse_distance_sum, point_wind_direction/inverse_distance_sum)
				point_wind_speed = (point_wind_speed/inverse_distance_sum)
				point_wind_direction = (point_wind_direction/inverse_distance_sum)
				x_components.append(0.539957 * point_wind_speed * np.cos(np.deg2rad(-point_wind_direction * 10) - np.pi/2))
				y_components.append(0.539957 * point_wind_speed * np.sin(np.deg2rad(-point_wind_direction * 10) - np.pi/2))
			except ZeroDivisionError as e:
				point_wind_speed = 0
				point_wind_direction = 0
				x_components.append(0)
				y_components.append(0)
			iterator += 1

		y_dimension = int(np.absolute((points[-1][0] - points[0][0])/0.0625)) + 1
		x_dimension = int(np.absolute((points[-1][1] - points[0][1])/0.0625)) + 1
		print("Y DIM: %s" % y_dimension)
		print("X DIM: %s" % x_dimension)
		print(len(x_components), len(y_components), len(points))
		f.write("\nWIND_X\n")
		for i, x in enumerate(x_components):
			val = round(x, 2)
			if(i % x_dimension == 0 and i != 0):
				f.write('\n')
			f.write(str(val) + '\t')
		f.write("\nWIND_Y\n")
		for i, y in enumerate(y_components):
			val = round(y, 2)
			if(i % x_dimension == 0 and i != 0):
				f.write('\n')
			f.write(str(val) + '\t')
	print("Done\n")

# A function that generates an inverse distance weighted interpolation on a given list of input points
def idw_interpolation(points, vector_data, time, projection):

	fig = plt.figure()
	fig = plt.figure(figsize = (11, 8))
	plt.title('Vancouver Island : Hourly Wind Data IDW Interpolation for %s' % (time))

	# draw coastlines, parallels and meridians
	frame_lat = [46, 52]
	frame_lon = [-129,-122]
	projection.drawcoastlines()
	projection.arcgisimage(service = 'ESRI_Imagery_World_2D', xpixels = 10000, verbose = True)
	projection.drawparallels(np.arange(frame_lat[0],frame_lat[1],0.5),labels = [1,0,0,0], color = 'white')
	projection.drawmeridians(np.arange(frame_lon[0],frame_lon[1],0.5),labels = [0,0,0,1], color = 'white')

	# Format the vector data into a more manageable format
	data = get_data_from_vector(vector_data)

	iterator = 0
	print("\nComputing inverse distance weighted wind speed interpolation for each coordinate provided ...\n")
	for item in points:
		point_lat = item[0]
		point_long = item[1]
		point_wind_speed = 0
		point_wind_direction = 0
		inverse_distance_sum = 0
		data_with_distances = []
		distances_from_stations_to_point = []

		progress_bar(iterator, len(points))
		iterator += 1

		# Find the distance from all the stations to that point
		for i in range(0, len(station_names)):
			distance = great_circle_distance(lats[i], lons[i], point_lat, point_long)
			distances_from_stations_to_point.append((station_names[i], round(distance, 2)))

		# Combine both lists to get the items that we need
		for item in distances_from_stations_to_point:
			#print(item)
			for item2 in data:
				if(item[0] == item2[0]):
					# Convert metres to kilometres
					data_with_distances.append((item2[0], item2[1], item2[2], (item[1]/1000)))
					break
		# Remove NaNs from data_with_distances
		for index, item in enumerate(data_with_distances):
			if(item[0] is np.nan or item[1] is np.nan):
				del data_with_distances[index]

		# Interpolate: Calculate point wind speed and wind direction for a given unknown location
		temp1 = 0.0
		temp2 = 0.0
		for item in data_with_distances:
			# Get the sum of the inverse distance squared for each point
			# If the distance is less than 70kms, include the point
			if(item[3] <= 40):
				inverse_distance_sum += (1 / (item[3])**2)
			else:
				pass
		for item in data_with_distances:
			# If the distance is less than 70kms, include the point
			if(item[3] <= 40):
				if(not np.isnan(item[1])):
					temp1 = (item[1] / (item[3])**2)
					point_wind_speed = point_wind_speed + temp1
					#print("wind spd: %s" % str(point_wind_speed))
				if(not np.isnan(item[2])):
					temp2 = (item[2] / (item[3])**2)
					point_wind_direction = point_wind_direction + temp2
					#print("wind dir: %s" % str(point_wind_direction))
			else:
				pass
		try:
			point_wind_speed = (point_wind_speed/inverse_distance_sum)
			point_wind_direction = (point_wind_direction/inverse_distance_sum)
			# projection.quiver(point_long, point_lat,
			#     0.539957 * point_wind_speed * np.cos(np.deg2rad(270 - (point_wind_direction * 10))),
			#     0.539957 * point_wind_speed * np.sin(np.deg2rad(270 - (point_wind_direction * 10))),
			#     width = 0.001, headwidth = 2.0, color = 'w')
			projection.barbs(point_long, point_lat,
				0.539957 * point_wind_speed * np.cos(np.deg2rad(-point_wind_direction * 10) - np.pi/2),
				0.539957 * point_wind_speed * np.sin(np.deg2rad(-point_wind_direction * 10) - np.pi/2),
				color = 'w', length = 4, sizes = dict(emptybarb = 0.20, spacing = 0.2, height = 0.25))
			point_long, point_lat = projection(point_long, point_lat)
		except ZeroDivisionError as e:
			continue

	print("\n")
	# Save the figure to the local directory 2 levels up
	root_dir = path.abspath(path.join(__file__ ,"../.."))
	relative_path = root_dir + "/results/"
	filename = "idw_interpolation_" + time + '.svg'
	plt.savefig(relative_path + filename, format = 'svg', dpi = fig.dpi)
	# Optionally display the figure to the user
	#plt.show()
	# Close the figure after having saved it to free RAM space on the current computer running this script
	plt.close(fig)

# Generate datetime objects between a given start and end time at a certain delta interval
def perdelta(start, end, delta):
	curr = start
	while curr <= end:
		yield curr
		curr += delta

# Returns a list with times generated by the perdelta helper function
def generate_list_of_times(start_time, end_time):

	dtfmt = "%Y-%m-%d %H:%M"
	start = dt.datetime.strptime(start_time, dtfmt)
	end = dt.datetime.strptime(end_time, dtfmt)

	# A slick list comprehension to get the generated times into a list in the format of our liking
	return [str(result.replace(second = 0, microsecond = 0))[:-3] for result in perdelta(start , end, timedelta(hours = 1))]

# This function generates a list of coordinates to be used in the IDW interpolation
# resolution is in fractions of degrees, other parameters are the start and end coordinates
def generate_list_of_coords(start_lat, start_long, end_lat, ent_long, resolution):
	# Generate a grid of coordinates to overlay on our map for the interpolation
	point_lats = np.arange(start_lat, end_lat, resolution)
	point_longs = np.arange(start_long, ent_long, resolution)
	return [(lat, long) for lat in point_lats for long in point_longs]

# A helper function to display progress bar while the frames are being read in
# Useful to show the execution order of the program for the user
def progress_bar(value, endvalue, bar_length = 25):
	percent = float(value) / endvalue
	arrow = '-' * int(round(percent * bar_length)-1) + '>'
	spaces = ' ' * (bar_length - len(arrow))
	sys.stdout.write("\rProgress: [{0}] {1}%".format(arrow + spaces, int(round(percent * 100))))
	sys.stdout.flush()

# Loads an list of HDF5 files into memory. Takes a list of filenames provided by the user,
# and returns a list of data frames which is passed onto other functions for further processing
def load_files(filenames):
	# Set this option to see more columns when printing pandas df for debugging purposes
	pd.set_option('display.expand_frame_repr', False)

	print("\nLoading data files into the program ...\n")
	root_dir = path.abspath(path.join(__file__ ,"../.."))
	relative_path = root_dir + "/data/processed/"
	frames = []
	for index, filename in enumerate(filenames):
		# Search for the files in the data/processed directory
		temp_path = relative_path + filename
		frame = pd.read_hdf(temp_path, filename)
		#print(filename)
		if((filename != 'Halibut_Bank_Buoy_46146') and (filename != 'Sentry_Shoal_Buoy_46131')):
			# Get rid of the columns that we will not be using in this analysis
			try:
				del frame['Wind Spd Flag'], frame['Visibility (km)'], frame['Visibility Flag'], frame['Hmdx'], frame['Hmdx Flag']
				del frame['Dew Point Temp (°C)'], frame['Dew Point Temp Flag'], frame['Rel Hum (%)'], frame['Rel Hum Flag']
				del frame['Weather'], frame['Wind Chill'], frame['Wind Chill Flag'], frame['Year'], frame['Month'], frame['Day'], frame['Time']
				del frame['Stn Press Flag'], frame['Stn Press (kPa)'], frame['Wind Dir Flag'], frame['Temp Flag'], frame['Temp (°C)']
				#print(frame)
			except KeyError as e:
				# This is a text file DF. Get it into the same format as the Env.Can. df
				print(e)
				wind_speeds = frame.loc[((frame['Data Type'] == '070') | (frame['Data Type'] == '076'))]
				wind_speeds = wind_speeds.rename(columns = {'Data' : 'Wind Spd (km/h)'})
				wind_directions = frame.loc[((frame['Data Type'] == '156') | (frame['Data Type'] == '069'))]
				wind_directions = wind_directions.rename(columns = {'Data' : 'Wind Dir (10s deg)'})
				del wind_directions['Data Type'], wind_directions['climate_id']
				del wind_speeds['Data Type'], wind_speeds['climate_id']
				text_file_df = wind_speeds.join(wind_directions, how = 'inner', lsuffix = '_l')
				frame = text_file_df
				frame = frame[['Wind Dir (10s deg)','Wind Spd (km/h)']]
				#print(frame)
			frames.append((filename, frame))
			progress_bar(index + 1, len(filenames))
		else:
			# The Halibut_Bank_Buoy_46146 and Sentry_Shoal_Buoy_46131 files are already formatted correctly, so simply append them
			frames.append((filename, frame))
	print("\nDone\n")
	return frames

# Generate the needed plot for given stations
def plot_graphs(list_of_frames, argv, measurement_type):
	print("\nPlotting graph...")
	frames_to_plot = []
	for filename, frame in list_of_frames:
		dates = []
		# Convert all the string representations of the date to Python date objects
		for item in frame.index:
			# Try to assign a datetime object to item unless it already is a datetime object
			try:
				item = dt.datetime.strptime(item, '%Y-%m-%d %H:%M')
			except TypeError as e:
				pass
			dates.append(item)
		frame.index = dates

		try:
			# If the file was scraped from the text file, try to get only the data type that you want
			# The Env. Can. Tables will not have these attributes, hence the try except statement
			frame = frame.loc[frame['Data Type'] == measurement_type]
			# Rename the 'Data' column in the frame to the appropriate data label
			if(measurement_type == '076'):
				frame.rename(columns = {'Data':'Wind Spd (km/h)'}, inplace = True)
			elif(measurement_type == '156'):
				frame.rename(columns = {'Data':'Wind Dir (10s deg)'}, inplace = True)
		except KeyError as e:
			continue

		if(len(frame) == 0):
			print("One of the provided dataframes is empty. Please check the files that you have input into the program.")
			sys.exit(0)

		frames_to_plot.append(frame)

	fig, ax = plt.subplots()
	count = 1
	for index, item in enumerate(frames_to_plot):
		df = item
		#  Assignment ax = ax allows multiple plots to appear on the same graph
		if(measurement_type == '076'):
			df.plot(df.index, "Wind Spd (km/h)", ax = ax, label = argv[count])
		if(measurement_type == '156'):
			df.plot(df.index, "Wind Dir (10s deg)", ax = ax, label = argv[count])
		count += 1

	plt.xlabel('Time')
	if(measurement_type == '076'):
		plt.ylabel('Wind Speed (km/h)')
	if(measurement_type == '156'):
		plt.ylabel('Wind Direction (10s of degrees)')

	plt.show()

# This function iterates through all the dataframes provided
# and selects the rows that contain the time requested by the calling function.
def create_time_frame(dataframes, time):

	print("\n\nGetting a time frame for %s ...\n" % (time))
	#print(dataframes)

	time_data = []
	temp_frames = []
	# Iterate through the dataframes tuples to find rows that have that time as the key
	for item in dataframes:

		filename = item[0]
		frame = item[1]

		# Try to find a data point for the time for each frame
		try:
			# Assign a new frame to the resulting rows
			temp_frame = frame.loc[time]
			temp_frames.append((filename,temp_frame))
		except KeyError as e:
			#print(e)
			print("There is no data in %s.hdf for the provided time." % (filename))
			pass
	#print("Temp frames")
	#print(temp_frames)
	print("\nParsing for required data...")
	for name, frame in temp_frames:
		#print("File name: %s" % (name))
		#print(frame)
		try:
			wind_direction = frame.iat[1, 2]
			wind_speed = frame.iat[0, 2]
			#print(wind_speed, wind_direction)
			time_data.append((name, wind_speed, wind_direction))
			#print('\n')
			continue
		except TypeError as e:
			pass
			#print(e)
		try:
			wind_direction = frame.iloc[0]
			wind_speed = frame.iloc[1]
			#print(wind_speed, wind_direction)
			time_data.append((name, wind_speed, wind_direction))
			#print('\n')
		except TypeError as e:
			pass
			#print(e)
	print("\nDone")
	return time_data

# This function gets the station coordinates for the files passed into the program
# Returns a list which contains tuples (station_name, lat, long)
# This function currently relies on the specific order of the items in the coordinates and names lists
# Performance could later be improved by using a dictionary
def get_station_coords(dataframes):

	print("\nGetting coordinates for stations...\n")
	available_stations = []
	stations_with_coords = []
	for filename, frame in dataframes:
		#print(list(frame))
		tokens = filename.split('_')
		# Get rid of the station_id or the climate_id in the name
		tokens.pop()
		filename = ' '.join(tokens)
		filename = filename.replace("_"," ").upper()
		if(filename not in available_stations):
			available_stations.append(filename)
	#print(available_stations)

	# Get the coordinates for each station and associate them with the stations in the dataframes
	# Check the globally declared lists
	for index, station in enumerate(station_names):
		if(station in available_stations):
			stations_with_coords.append((station, lats[index], lons[index]))
		progress_bar(index, len(station_names))

	return stations_with_coords

# Instantiates a Basemap projection object. Uses data from globally declared lists lats and lons
# projection can then be passed to other functions which can populate it with data
def create_projection():

	print("Creating a projection centered on southern Vancouver Island ...")
	lat0 = np.mean(lats)
	lon0 = np.mean(lons)
	# create stereographic Basemap instance, centered around the area of interest
	projection = Basemap(projection='stere',lon_0 = lon0,lat_0 = lat0,lat_ts = lat0,
				llcrnrlon = -125.5, llcrnrlat = 48.5,
				urcrnrlon = -122.5, urcrnrlat = 50.25,
				rsphere = 6378100, resolution = 'f',
				area_thresh = 0.01, epsg = 4326)
	print("\nDone")
	return projection

# This function takes a list which for each index contains a station name, the lat and the long for that station
# as the first argument, a list containing the measurments for each station at that time, the time, and a projection object
def plot_map(station_coords, vector_data, time, projection):

	fig = plt.figure()
	fig = plt.figure(figsize = (11, 8))
	plt.title('Vancouver Island : Hourly Wind Data by Station for %s' % (time))

	# draw coastlines, parallels and meridians
	frame_lat = [48.5, 50.5]
	frame_lon = [-125.5,-122.5]
	projection.drawcoastlines()
	projection.arcgisimage(service = 'ESRI_Imagery_World_2D', xpixels = 10000, verbose = True)
	projection.drawparallels(np.arange(frame_lat[0],frame_lat[1],0.5),labels = [1,0,0,0], color = 'white')
	projection.drawmeridians(np.arange(frame_lon[0],frame_lon[1],0.5),labels = [0,0,0,1], color = 'white')

	# Populate the vectors and associate each vector with the correct coordinates
	data = get_data_from_vector(vector_data)

	print("\nAdding barbs and wind vectors to the map ...")
	for index, item in enumerate(data):
		curr_station = item[0]
		curr_wind_speed = item[1]
		curr_wind_direction = item[2]
		for index, station in enumerate(station_names):
			# Set the correct LONG and LAT for each station in the requested dataset
			if(station == curr_station):
				#print(curr_station)
				#print("Wind Speed: %s\nWind Direction: %s\n" % (curr_wind_speed, curr_wind_direction))
				curr_longitude = lons[index]
				curr_latitude = lats[index]
				# Place the vector and the barb, don't forget to convert from cartesian coordinates to meteorological ones
				# as well converting the windspeed from km/h to knots for the barbs
				projection.quiver(curr_longitude, curr_latitude,
					0.539957 * curr_wind_speed * np.cos(np.deg2rad(270 - (curr_wind_direction * 10))),
					0.539957 * curr_wind_speed * np.sin(np.deg2rad(270 - (curr_wind_direction * 10))),
					width = 0.002, headwidth = 2.5, color = 'w')
				projection.barbs(curr_longitude, curr_latitude,
					0.539957 * curr_wind_speed * np.cos(np.deg2rad(-curr_wind_direction * 10) - np.pi/2),
					0.539957 * curr_wind_speed * np.sin(np.deg2rad(-curr_wind_direction * 10) - np.pi/2),
					color = 'w', length = 7)
				curr_longitude, curr_latitude = projection(curr_longitude, curr_latitude)
				break
		# Place the Points
		projection.plot(curr_longitude, curr_latitude, 'bo', markersize = 1)
		projection.scatter(curr_longitude, curr_latitude)
		# Place the Name
		plt.text(curr_longitude, curr_latitude, curr_station, color = 'w')

	# Save the figure to data
	# get the directory 2 levels up
	root_dir = path.abspath(path.join(__file__ ,"../.."))
	relative_path = root_dir + "/results/"
	filename = "wind_by_station_" + time + '.svg'
	plt.savefig(relative_path + filename, format = 'svg', dpi = fig.dpi)
	# Optionally display the figure to the user
	#plt.show()
	# Close the figure after having saved it to free RAM space on the current computer running this script
	plt.close(fig)
	print("\n")

# The main function handles higher level program logic
def main(argv):

	if(len(argv) < 2):
		print("Please include the filename(s) as program arguments.\nFiles should contain station data in hdf5 format: Station_Name_123456 where the number is the climate or station ID.")
		print("Filenames should be entered one at a time and be separated by spaces.\n")
		sys.exit(0)
	else:
		print('\n')
		# Generate a grid of coordinates to overlay on our map for the interpolation
		points = generate_list_of_coords(48.5, -125.5, 50.3125, -121.9375, 0.0625)
		# Get a list of hour intervals between the start and end times wanted
		times = generate_list_of_times("2000-12-14 21:00", "2000-12-15 15:00")
		# Generate the dict of station distances from one another
		station_distances = generate_distances()
		# Load the data in to the program from the hdf5 files
		dataframes = load_files(argv[1:])
		# Create a projection for the area of interest
		projection = create_projection()
		# Get the station coordinates for the files passed into the program
		coordinates = get_station_coords(dataframes)

		for time in times:
			# Get the data from the frames pertaining to certain time wanted
			vector_data = create_time_frame(dataframes, time)
			# Write the inteprpolated wind data to a text file for SWAN
			generate_SWAN_input(points, vector_data, time)
			# Generate a map by getting the inverse distance weighed interpolation of the data based on known values
			#idw_interpolation(points, vector_data, time, projection)
			# Generate a map with the known wind values at each station
			#plot_map(coordinates, vector_data, time, projection)

		# Uncomment the following code to get wind speed and wind direction over time graphs ------
		#plot_graphs(dataframes, argv, '076')
		#plot_graphs(dataframes, argv, '156')
		# -----------------------------------------------------------------------------------------

		# # Move the swan input data file to the appropriate folder
		# root_dir = path.abspath(path.join(__file__ ,"../.."))
		# print(root_dir)
		# relative_path = root_dir + "/results/"
		# print(relative_path)
		# shutil.move(str(root_dir + "/swan_input_data.txt", relative_path)
		sys.exit(0)

if __name__ == "__main__":
	main(sys.argv)
