# A script to scrape wind readings from text files by Henri De Boever
# Read the file in, insert the data pertaining to each climateID into an OrderedDict
# Reformat it based on new parameters, then insert into a pandas dataframe


# Referred to as 'Data Type' in this script
#
# Additional helpful information:
# 070 : HLY15 wind run per hour U2A Anemometer
# 076 : HLY15 Wind Speed U2A Anemomenter
# 156 : HLY15 Wind direction (10s of degrees)
# 069 HLY15 wind direction 45B Anemometer (8 point)
# 210 Gust (Knots) U2A Anemometer


import pandas as pd
import numpy as np
import sys, os, re, shutil
from collections import OrderedDict

# A helper function that associates the name of a measurment location with its climateID
def get_station_names(climate_id):

	if climate_id == '1020590':
		return ('Ballenas_Island_1020590')
	if climate_id == '1021330':
		return ('Cape_Mudge_1021330')
	if climate_id == '102BFHH':
		return ('Entrance_Island_102BFHH')
	if climate_id == '1045100':
		return ('Merry_Island_Lightstation_1045100')
	if climate_id == '1106200':
		return ('Point_Atkinson_1106200')
	if climate_id == '1107010':
		return ('Sandhead_CS_1107010')
	if climate_id == '1017101':
		return ('Saturna_Island_CS_1017101')
	if climate_id == '1027403':
		return ('Sisters_Island_1027403')
	if climate_id == '1108290':
		return ('Tsawwassen_Ferry_1108290')
	if climate_id == '101G100':
		return ('Saturna_Island_Campbell_Scientific_101G100')
	if climate_id == '1108380':
		return ('Vancouver_Sea_Island_CCG_1108380')
	if climate_id == '1108291':
		return ('Tsawwassen_Ferry_AUTO_1108291')
	if climate_id == '1045101':
		return ('Merry_Island_1045101')
	if climate_id == '1043304':
		return ('Grief_Point_1043304')
	if climate_id == '1108447':
		return ('Vancouver_INTL_A_1108447')
	if climate_id == '1108395':
		return ('Vancouver_INTL_A_1108395')
	if climate_id == '1021830':
		return ('Comox_A_1021830')
	if climate_id == '1108446':
		return ('Vancouver_Harbour_CS_1108446')
	if climate_id == '1021332':
		return ('Cape_Mudge_CS_1021332')
	if climate_id == '1022689':
		return ('Entrance_Island_1022689')
	if climate_id == '1017099':
		return ('Saturna_Capmon_CS_1017099')

# Unpack the dictionary and store it into a pandas data frame
def store_data(dict):

	# climate_ids contains a list of the ids encountered in the files
	# Each ID is uniquely affiliated with one observation location
	climate_ids = []
	frames = []
	# Get a list of climate ids from the dictionary using a dict comprehension
	# Cast the set to list in order to do list comprehensions on it later
	climate_ids = list({key[0] for key, value in dict.items() if key[0] not in climate_ids})

	# Set this option to see more columns when printing pandas dfs for testing purposes
	pd.set_option('display.expand_frame_repr', False)

	df = pd.DataFrame(list(dict.items()), columns = ['Key', 'Values'])
	df['climate_id'], df['date/time'], df['Data Type'] = zip(*df.Key)
	print(df.Values)
	df['Data'] = df.Values
	print(df['Key'], df['Values'])
	del df['Key'], df['Values']
	# Populate each sub frame by selecting rows containing the correct climateID
	df1 = df.loc[df['climate_id'] == '1020590']
	df2 = df.loc[df['climate_id'] == '1021330']
	df3 = df.loc[df['climate_id'] == '102BFHH']
	df4 = df.loc[df['climate_id'] == '1045100']
	df5 = df.loc[df['climate_id'] == '1106200']
	df6 = df.loc[df['climate_id'] == '1107010']
	df7 = df.loc[df['climate_id'] == '1017101']
	df8 = df.loc[df['climate_id'] == '1027403']
	df9 = df.loc[df['climate_id'] == '1108290']
	df10 = df.loc[df['climate_id'] == '101G100']
	df11 = df.loc[df['climate_id'] == '1108380']
	df12 = df.loc[df['climate_id'] == '1108291']
	df13 = df.loc[df['climate_id'] == '1045101']
	df14 = df.loc[df['climate_id'] == '1043304']
	df15 = df.loc[df['climate_id'] == '1108447']
	df16 = df.loc[df['climate_id'] == '1108395']
	df17 = df.loc[df['climate_id'] == '1021830']
	df18 = df.loc[df['climate_id'] == '1108446']
	df19 = df.loc[df['climate_id'] == '1021332']
	df20 = df.loc[df['climate_id'] == '1022689']
	df21 = df.loc[df['climate_id'] == '1017099']

	frames.append(df1)
	frames.append(df2)
	frames.append(df3)
	frames.append(df4)
	frames.append(df5)
	frames.append(df6)
	frames.append(df7)
	frames.append(df8)
	frames.append(df9)
	frames.append(df10)
	frames.append(df11)
	frames.append(df12)
	frames.append(df13)
	frames.append(df14)
	frames.append(df15)
	frames.append(df16)
	frames.append(df17)
	frames.append(df18)
	frames.append(df19)
	frames.append(df20)
	frames.append(df21)

	# Store each DF in HDF5 format in the directory /weather_station_data
	path = os.getcwd()
	for frame in frames:
		# Set the key of the frame to be the date and time
		frame = frame.set_index("date/time")
		# Cast the type of the wind data to float to handle NaNs
		frame['Data'] = frame['Data'].astype(float)
		# Get the climate_id of the current frame
		curr_climate_id = frame['climate_id'].values[0]
		print("Current Climate ID: %s" % curr_climate_id)
		#del frame['climate_id']
		print(list(frame))
		print(frame.index)
		# Generate a filename
		filename = get_station_names(curr_climate_id)
		# Establish the path of the location where you want to store the files
		relative_path = path + "/processed/" + filename
		# Convert the frame to hdf5 format
		frame.to_hdf(filename, filename, append = True)
		# Move the file to its destination
		shutil.move(path + "/" + filename, relative_path)

# This function handles occurences of invalid measurements on the form '-99999M'
# Input parameter is a list, output parameter is a list
# It replaces occurences with the equivalent number of NaNs in the same order as the invalid data was stored
def handle_invalid_data(line):
	values = []
	final_list = []
	for measurement in line:
		if('E' in measurement and '-99999M' in measurement):
			# Skip cases where the 2 edge cases appear
			continue
		elif('-99999M' in measurement):
			values = measurement.split('M')
			values = [measurement for measurement in values if measurement != '']
			values = [np.nan if measurement == '-99999' else measurement for measurement in values]
			for value in values:
				final_list.append(value)
		elif('E' in measurement):
			values = measurement.split('E')
			values = [measurement for measurement in values if measurement != '']
			for value in values:
				final_list.append(value)
		else:
			final_list.append(measurement)
	return final_list

# A helper function that is called in read_file. Returns a list of attributes for each line in the input file
# Looks at the first token in every line, and extablishes the climateID, date, and type for the data string
# e.g.
#   110838020130821156000007 -99999M-99999M000001 000006 000006 000011 000000...........
#
#   First 7 digits are the climateID, next 8 digits are the date, next 3 are the measurement type,
#   then the next 6 digits are the first measurement (km/h). Subsequent measurments are seperated by spaces.
def get_line_info(token):

	climateID = token[0:7]
	date = token[7:15]
	hyphenated_date = date[:4] + '-' + date[4:6] + '-' + date[6:]
	type = token[15:18]
	first_measurement = token[18:]
	return (climateID, hyphenated_date, type, first_measurement)

# Reads a file and inserts relevant info into an Ordered Dict
def read_file(filename):

	data = OrderedDict()
	line_data = []
	print("\nParsing %s for wind data:\n" % (filename))
	with open(filename) as f:
		for line in f:
			line = line.split(' ')
			id = get_line_info(line[0])[0]
			date = get_line_info(line[0])[1]
			type = get_line_info(line[0])[2]
			first_measurement = get_line_info(line[0])[3]
			line_data = line[1:]

			# Add the first measurement to the list
			line_data.insert(0, first_measurement)
			# Get rid of the newline character found in the last entry of the list by doing a list.pop()
			line_data.pop()
			# Deal with invalid data values using list comprehensions and a helper function
			line_data = handle_invalid_data(line_data)
			# Replace empty data points with NaN
			line_data = [np.nan if measurement == '' else measurement for measurement in line_data]
			# Get rid of the leading zeroes in each of the wind speed measurments
			line_data = [re.sub("^0+","", str(measurement)) if measurement != '000000' else '0' for measurement in line_data]
			# If the line length is less than 24, pad it with NaNs at the end
			while(len(line_data) < 24):
				# If the total line length is somehow under 24, append nan values
				line_data.append(np.nan)
			while(len(line_data) > 24):
				# Get rid of extra NaNs if the length is greater than 24
				line_data.pop()
			# Finally, insert the data into the dictionary and assign a time to the measurement based on order of appearance
			counter = 0
			for measurement in line_data:
				time = str(counter).zfill(2)
				date_time = date + " " + time + ":00"
				data[(id, date_time, type)] = measurement
				counter += 1

	return data

# The main function takes care of the overall program logic
def main(argv):

	file_contents = OrderedDict()
	if(len(argv) < 2):
		print("Not enough arguments. Please include the name of a all_stations_data.txt as a second argument parameter.")
		sys.exit(0)
	else:

		# Getting Hourly Data from a text file
		file_contents = read_file(argv[1])
		# Storing the data in /weather_station_data
		store_data(file_contents)
		# Quit the program once storage is complete
		sys.exit(0)

if __name__ == "__main__":
	   main(sys.argv)
