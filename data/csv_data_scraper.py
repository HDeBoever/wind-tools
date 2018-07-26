# A script to scrape wind readings from the csv file for the Halibut Bank Buoy by Henri De Boever
# Read the file in, insert the data pertaining to each climateID into an OrderedDict
# Reformat it based on new parameters, then insert into a pandas dataframe

# Specifically programmed to read the marine data for the Halibut Bank Buoy, Station_ID = C46146
# and the Sentry Shoal Buoy, Station ID = C46131

from datetime import datetime, date
import pandas as pd
import sys, os, shutil

# Read the csv file and make the necessary formatting modification to it
def read_file(filename):

	# Set this option to see more columns when printing pandas df for debugging purposes
	pd.set_option('display.expand_frame_repr', False)
	df = pd.read_csv(filename)
	# Convert the format of the date to match the date format of all the other files
	df['Date/Time'] = pd.to_datetime(df['DATE'], errors = 'coerce').dt.strftime('%Y-%m-%d %H:00')
	df['Date/Time'] = pd.to_datetime(df['Date/Time']).dt.strftime('%Y-%m-%d %H:%M')
	df = df.set_index('Date/Time')
	del df['DATE'], df['VCAR'], df['VTPK'], df['VWH$'], df['VCMX'], df['GSPD'], df['WSPD'], df['DEPTH'], df['WDIR'], df['WSS$.1']
	del df['GSPD.1'], df['DRYT'], df['ATMS'], df['ATMS.1'], df['SSTP'], df['Q_FLAG'], df['STN_ID'], df['LATITUDE'], df['LONGITUDE']
	del df['VTP$'], df['WSS$'], df['Unnamed: 23']
	df.rename(columns={'WSPD.1': 'Wind Spd (km/h)', 'WDIR.1': 'Wind Dir (10s deg)'}, inplace=True)
	#df['Wind Dir (10s deg)'] = df['Wind Dir (10s deg)'] - 180
	df['Wind Dir (10s deg)'] = df['Wind Dir (10s deg)']/10
	df['Wind Spd (km/h)'] = (df['Wind Spd (km/h)'] * (3.6)).round()
	print(df)
	return df

# Store the .csv data in hdf5 format
def store_data(dataframe, filename):

	path = os.getcwd()
	if('Halibut' in filename):
		filename = filename[:-4] + '_46146'
	elif('Sentry' in filename):
		filename = filename[:-4] + '_46131'
	# Establish the path of the location where you want to store the files
	relative_path = path + "/processed/" + filename
	# Convert the frame to hdf5 format
	dataframe.to_hdf(filename, filename, append = True)
	# Move the file to its destination
	shutil.move(path + "/" + filename, relative_path)

# The main function takes care of the overall program logic
def main(argv):

	if(len(argv) < 2):
		print("Please include the name of the .csv as the second argument.")
		sys.exit(0)
	else:
		relative_path = os.getcwd()
		# Getting Hourly Data from a text file
		file_contents = read_file(relative_path + "/raw/" + argv[1])
		# Storing the data in /weather_station_data
		store_data(file_contents, argv[1])
		# Quit the program once storage is complete
		sys.exit(0)

if __name__ == "__main__":
	   main(sys.argv)
