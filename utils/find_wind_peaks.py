# A python program that find the peak wind speed for a given station
# on a desired day time_frame.
# For exclusive use by Cascadia Coast Research.
# Written by Henri De Boever 2018/06/05


import matplotlib.pyplot as plt
from scipy.signal import find_peaks
import datetime as dt
import numpy as np
import pandas as pd
import sys ,os, shutil
import os.path as path

# Loads an HDF5 file into memory. Looks into the weather_station_data folder for the file
# that matches the user input. The key of the HDF5 files containing weather data is the filename
def load_hdf5(filename):
	root_dir = path.abspath(path.join(__file__ ,"../.."))
	relative_path = root_dir + "/data/processed/" + filename
	return pd.read_hdf(relative_path, filename)

# Generate a plot of windspeed over time. Threshold is the minimum windspeed that qualifies,
# and the time_frame is the time over which the peaks are calculated. This function invokes the use of find_peaks from scipy.signal
def plot_windspeed(df, filename, threshold, time_frame):

	print("\nGenerating the windspeed over time plot for %s" % (filename))
	dates = []
	#Convert all the string objects in Date/Time index to datetime objects
	for string in df.index:
		string = dt.datetime.strptime(string, '%Y-%m-%d %H:%M')
		dates.append(string)
	df.index = dates
	try:
		df = df.loc[df['Data Type'] == '070']
	except KeyError as e:
		print(e)
	if(len(df) == 0):
		print("The dataframe is empty. Nothing to show here.")
		sys.exit(0)
	try:
		df.rename(columns = {'Data':'Wind Spd (km/h)'}, inplace = True)
	except KeyError as e:
		print(e)
	#print(df)

	# Replace NaNs with zeros otherwise find-peaks will not work
	wind_speeds = df['Wind Spd (km/h)'].tolist()
	dates = df.index.tolist()
	for n, i in enumerate(wind_speeds):
		if np.isnan(i):
			wind_speeds[n] = 0

	peak_indices, _  = find_peaks(wind_speeds, height = threshold, distance = time_frame)
	peak_wind_speeds = []
	peak_wind_dates = []
	#print(peak_indices)
	#print(wind_speeds)
	for index in peak_indices:
		# print(dates[index], wind_speeds[index], index)
		peak_wind_speeds.append(wind_speeds[index])
		peak_wind_dates.append(dates[index])
	print('The number of peaks over threshold is :%s' % str(len(peak_wind_speeds)))
	plt.scatter(peak_wind_dates, peak_wind_speeds, color = 'r')
	plt.plot(df.index, df['Wind Spd (km/h)'])
	plt.title("Peak 72 Hour Wind Speed Over Threshold for " + filename)
	plt.show()

# The main function handles higher level program logic
def main(argv):

	if(len(argv) < 2):
		print("Please include the filename as a program argument.\nThe file should contain station data in hdf5 format: Station_Name_123456 where the number is the climate or station ID.")
		sys.exit(0)
	else:
		df = load_hdf5(argv[1])
		# arguments are as follows: df is the station data hdf5 dataframe, argv[1] is the filename, 3rd arg is the threshold windspeed, 4th arg is the time window in hours
		plot_windspeed(df, argv[1], 40, 72)
		sys.exit(0)

if __name__ == "__main__":
	main(sys.argv)
