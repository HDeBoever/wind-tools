'''
For flood hazard assessment we need to know the correlation between larger storm surge events and wind speed.
I'd like you to write a function that takes two data series as inputs.  Both these series should be indexed with a datetime stamp.
The function should find the peaks of the first series, then find the corresponding value in the second series.
If the corresponding value is a NaN, it should be ignored.

The function should return 3 arrays of size 1xN,
(1)  an array with the datetime stamp of the peaks,
(2) an array with the values of the peaks from Series1
and (3) an array with the corresponding values from Series2.
Extra points if you can add a threshold option.
That is, get the maximum value from Series2 that is within x hours of the peak in Series1.


June 22nd 2018

@author: Henri De Boever
'''

import matplotlib.pyplot as plt
from scipy.signal import find_peaks
import datetime as dt
import numpy as np
import pandas as pd
import sys ,os, shutil
import os.path as path

# A helper function to display progress bar while the frames are being read in
def progress_bar(value, endvalue, bar_length = 25):
	percent = float(value) / endvalue
	arrow = '-' * int(round(percent * bar_length)-1) + '>'
	spaces = ' ' * (bar_length - len(arrow))
	sys.stdout.write("\rPercent: [{0}] {1}%".format(arrow + spaces, int(round(percent * 100))))
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

		# Add logic here to handle the read .hdf5, or the read .csv based on file extension
		if(not temp_path.endswith('.csv')):
			frame = pd.read_hdf(temp_path, filename)
			# Get rid of the columns that we will not be using in this analysis
			try:
				del frame['Wind Spd Flag'], frame['Visibility (km)'], frame['Visibility Flag'], frame['Hmdx'], frame['Hmdx Flag']
				del frame['Dew Point Temp (°C)'], frame['Dew Point Temp Flag'], frame['Rel Hum (%)'], frame['Rel Hum Flag']
				del frame['Weather'], frame['Wind Chill'], frame['Wind Chill Flag'], frame['Year'], frame['Month'], frame['Day'], frame['Time']
				del frame['Stn Press Flag'], frame['Stn Press (kPa)'], frame['Wind Dir Flag'], frame['Temp Flag'], frame['Temp (°C)']
			except KeyError as e:
				#print(e)
				pass
		elif(temp_path.endswith('.csv')):
			frame = pd.read_csv(temp_path, filename, delimiter = ',', header = None, names = ['Date/Time', 'SLEV', 'N/A'])
			frame['Date/Time'] = pd.to_datetime(frame['Date/Time']).dt.strftime('%Y-%m-%d %H:%M')
			frame = frame.set_index('Date/Time')
			try:
				frame['SLEV'] =  pd.to_numeric(frame['SLEV'], errors='coerce')
			except:
				pass
			#print(frame.dtypes)
			del frame['N/A']
		frames.append((filename, frame))
		progress_bar(index + 1, len(filenames))
	print("\nDone\n")
	return frames

# This function takes a list of 2 dataframes as an argument and performs an inner join by matching the dataframe indices
def join_dataframes(dataframes):

	print('\nJoining dataframes...')
	df1 = dataframes[0][1]
	df2 = dataframes[1][1]
	df1.index.names = ['Date/Time']
	df2.index.names = ['Date/Time']
	# perform an inner join by default
	merged_df = df1.join(df2, how = 'inner')

	# Non Text File DF
	try:
		merged_df = merged_df.loc[(merged_df['Wind Dir (10s deg)'] >= 0) & (merged_df['Wind Dir (10s deg)'] <= 36)]
		merged_df['SLEV'] =  merged_df['SLEV'] * 100
	except KeyError as e:
		pass
		#print(e)
	# Text File DF, handle the different formatting
	try:
		# Get the text file into the same format as the env. can. dataframes
		wind_speeds = merged_df.loc[((merged_df['Data Type'] == '070') | (merged_df['Data Type'] == '076'))]
		wind_speeds = wind_speeds.rename(columns = {'Data' : 'Wind Spd (km/h)'})
		# Change the values here to get winds only from a certain direction
		wind_directions = merged_df.loc[((merged_df['Data Type'] == '156') | (merged_df['Data Type'] == '069')) & ((merged_df['Data'] >= 0) & (merged_df['Data'] <= 36))]
		wind_directions = wind_directions.rename(columns = {'Data' : 'Wind Dir (10s deg)'})
		del wind_directions['Data Type'], wind_directions['climate_id']
		del wind_speeds['Data Type'], wind_speeds['climate_id']
		merged__text_file_df = wind_speeds.join(wind_directions, how = 'inner', lsuffix = '_l')
		merged__text_file_df['SLEV'] = merged__text_file_df['SLEV'] * 100
		del merged__text_file_df['SLEV_l']
		#print(merged__text_file_df)
		return merged__text_file_df
	except KeyError as e:
		pass
		#print(e)
	return merged_df

# Helper function called by plot_windspeed_slev()
# A terribly commented threshold window finding function
def indices_of_window_above_threshold(index_list, values, threshold):

	windows = []
	for index in index_list:
		window = []
		index2 = index
		# Step forward while the value is greater than threshold.
		while values[index2] > threshold:
			window.append(index2)
			index2 += 1
		# Reset the the pointer to one behind the index, and step backwards while value is greater than threshold.
		index2 = index - 1
		while values[index2] > threshold:
			window.append(index2)
			index2 -= 1
		# Record the indices in the window
		windows.append(window)
	# Return a list of windows
	return windows

# Helper function called by plot_windspeed_slev()
# For each index in a window above threshold, find the max wind value in the other series
def find_max_per_window(index_window_list, values, dates):

	second_series_peaks = []
	for window in index_window_list:
		curr_values = []
		for index in window:
			curr_values.append((values[index], dates[index], index))
		second_series_peaks.append(max(curr_values, key = lambda x:x[0]))
	return second_series_peaks

def plot_windspeed_slev(df, filename, wind_threshold, tide_threshold, time_frame):

	# Allows ouy to print entire numpy array
	np.set_printoptions(threshold='nan')
	print("\nGenerating plots for %s and assembled_tides.csv..." % (filename))

	#Convert all the string objects in Date/Time index to datetime objects
	dates = [dt.datetime.strptime(string, '%Y-%m-%d %H:%M') for string in df.index]
	df.index = dates
	if(len(df) == 0):
		print("The dataframe is empty. Nothing to show here.")
		sys.exit(0)
	try:
		df.rename(columns = {'Data':'Wind Spd (km/h)'}, inplace = True)
	except KeyError as e:
		pass
		print(e)

	# Replace NaNs with zeros otherwise find-peaks function call will not work
	wind_speeds = df['Wind Spd (km/h)'].tolist()
	slevs = df['SLEV'].tolist()
	dates = df.index.tolist()
	for n, i in enumerate(wind_speeds):
		if (np.isnan(i)):
			wind_speeds[n] = 0

	# Underscore is used to ignore unwanted return values while unpacking objects
	peak_wind_indices, _  = find_peaks(wind_speeds, height = wind_threshold, distance = time_frame)
	peak_slev_indices, _  = find_peaks(slevs, height = tide_threshold, distance = time_frame)

	# Map the peak indices to the values and dates for wind speeds
	peak_wind_speeds = [wind_speeds[index] for index in peak_wind_indices]
	peak_wind_dates = [dates[index] for index in peak_wind_indices]

	# Map the peak indices to the values and dates for storm surges
	peak_slevs = [slevs[index] for index in peak_slev_indices]
	peak_slev_dates = [dates[index] for index in peak_slev_indices]

	# Wind speed peaks for surge window-----------------------------------------------------------------

	# index_windows = indices_of_window_above_threshold(peak_slev_indices.tolist(), slevs, tide_threshold)
	# peaks_in_window = find_max_per_window(index_windows, wind_speeds, dates)
	# window_max = [peaks_in_window[index][0] for index, item in enumerate(peaks_in_window)]
	# window_dates = [peaks_in_window[index][1] for index, item in enumerate(peaks_in_window)]
	#
	# # Use a masked array to suppress slev values that are below threshold, only used for plotting
	# slevs_masked = np.ma.masked_less(slevs, tide_threshold)
	# plt.scatter(window_max, peak_slevs)
	# plt.xlabel('Max Wind Speed (km/h) Per Window over Threshold')
	# plt.ylabel('Max Surge (cm) per Window over Threshold')
	# # Line of best fit
	# plt.plot(np.unique(window_max), np.poly1d(np.polyfit(window_max, peak_slevs, 1))(np.unique(window_max)),color = 'r')
	# plt.show()
	#
	# plt.scatter(window_dates, window_max, color = 'k')
	# #plt.scatter(peak_slev_dates, peak_slevs, color = 'g')
	# plt.plot(df.index, df['Wind Spd (km/h)'], label = 'Wind Speed (km/h)')
	# plt.plot(df.index, df['SLEV'], label = 'Storm Surge (Metres * 100)')
	# plt.plot(df.index, slevs_masked, 'r', linewidth = 2)
	# plt.title("Wind SPeed Peaks for %d Hour Periods Over %dcm  Storm Surge Windows\nfor %s" % (time_frame, wind_threshold, filename))
	# plt.legend(bbox_to_anchor=(0.5, -0.1), loc = 8, ncol = 2, mode = "expand", borderaxespad = 0.)
	# plt.show()

	#-----------------------------------------------------------------------------------------------------------

	# # Surge peaks for wind speed window-----------------------------------------------------------------------

	index_windows = indices_of_window_above_threshold(peak_wind_indices.tolist(), wind_speeds, wind_threshold)
	peaks_in_window = find_max_per_window(index_windows, slevs, dates)
	window_max = [peaks_in_window[index][0] for index, item in enumerate(peaks_in_window)]
	window_dates = [peaks_in_window[index][1] for index, item in enumerate(peaks_in_window)]

	# Use a masked array to suppress values that are below threshold, only used for plotting
	wind_speeds_masked = np.ma.masked_less(wind_speeds, wind_threshold)
	plt.scatter(window_max, peak_wind_speeds)
	plt.xlabel('Max Surge (cm) Per Window over Threshold')
	plt.ylabel('Max Wind Speed (km/h) per Window over Threshold')
	plt.title("Max window wind speed over max surge for window over %dkm/h\nfor %s" % (wind_threshold, filename))
	# Line of best fit
	plt.plot(np.unique(window_max), np.poly1d(np.polyfit(window_max, peak_wind_speeds, 1))(np.unique(window_max)), color = 'r')
	plt.show()

	plt.scatter(window_dates, window_max, color = 'k')
	#plt.scatter(peak_wind_dates, peak_wind_speeds, color = 'r')
	plt.plot(df.index, df['Wind Spd (km/h)'], label = 'Wind Speed (km/h)')
	plt.plot(df.index, df['SLEV'], label = 'Storm Surge (Metres * 100)')
	plt.plot(df.index, wind_speeds_masked, 'r', linewidth = 2)
	plt.title("Surge Peaks for %d Hour Periods Over %dkm/h Wind Speed Windows\nfor %s" % (time_frame, wind_threshold, filename))
	plt.legend(bbox_to_anchor=(0.5, -0.1), loc = 8, ncol = 2, mode = "expand", borderaxespad = 0.)
	plt.show()

	#-----------------------------------------------------------------------------------------------------------

	print('The number of peaks over windspeed threshold is: %s' % str(len(peak_wind_speeds)))
	print('The number of peaks over storm surge threshold is: %s' % str(len(peak_slevs)))

# The main function handles higher level program logic
def main(argv):

	if(len(argv) < 3):
		print("Include a wind .hdf data file, and a sea level .csv data file.")
		print("Filenames should be separated by spaces.\n")
		sys.exit(0)
	else:

		print('\n')
		# Load the data in to the program from the hdf files
		dataframes = load_files(argv[1:])

		#print(dataframes)
		dataframe = join_dataframes(dataframes)
		# data source, data source, (km/h), (cm), (hours)
		plot_windspeed_slev(dataframe, argv[1], 43.2, 45, 1)

		sys.exit(0)

if __name__ == "__main__":
	main(sys.argv)
