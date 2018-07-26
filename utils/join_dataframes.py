# This script attempts to do an inner join on dataframes
# Written by Henri De Boever 2018/06/07

import pandas as pd
import sys, os, os.path as path

# A helper function to display progress bar while the frames are being read in
def progress_bar(value, endvalue, bar_length=25):
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
		frame = pd.read_hdf(temp_path, filename)
		# Get rid of the columns that we will not be using in this analysis
		try:
			del frame['Wind Spd Flag'], frame['Visibility (km)'], frame['Visibility Flag'], frame['Hmdx'], frame['Hmdx Flag']
			del frame['Dew Point Temp (°C)'], frame['Dew Point Temp Flag'], frame['Rel Hum (%)'], frame['Rel Hum Flag']
			del frame['Weather'], frame['Wind Chill'], frame['Wind Chill Flag'], frame['Year'], frame['Month'], frame['Day'], frame['Time']
			del frame['Stn Press Flag'], frame['Stn Press (kPa)'], frame['Wind Dir Flag'], frame['Temp Flag'], frame['Temp (°C)']
			#print(frame)
		except KeyError as e:
			# This is a text file DF so get it into the same format as the Env.Can. df
			print(e)
			wind_speeds = frame.loc[((frame['Data Type'] == '070') | (frame['Data Type'] == '076'))]
			wind_speeds = wind_speeds.rename(columns = {'Data' : 'Wind Spd (km/h)'})
			wind_directions = frame.loc[((frame['Data Type'] == '156') | (frame['Data Type'] == '069'))]
			wind_directions = wind_directions.rename(columns = {'Data' : 'Wind Dir (10s deg)'})
			del wind_directions['Data Type'], wind_directions['climate_id']
			del wind_speeds['Data Type'], wind_speeds['climate_id']
			text_file_df = wind_speeds.join(wind_directions, how = 'inner', lsuffix = '_l')
			frame = text_file_df
		frames.append((filename, frame))
		progress_bar(index + 1, len(filenames))
	print("\nDone\n")
	return frames

# This function takes a list of 2 dataframes as an argument and performs an inner join by matching the dataframe indices
# No longer being called or used
def inner_join_dataframes(dataframes):

	print('\nJoining dataframes...')

	df1 = dataframes[0][1]
	df2 = dataframes[1][1]

	df1.index.names = ['time']
	df2.index.names = ['time']
	print(df1.index)
	print(df2.index)

	# perfrom an inner join by default
	merged_df = pd.merge(df1, df2, left_index=True, right_index=True)
	print(merged_df)
	return merged_df

# This function takes a list of 2 dataframes as an argument and performs an inner join by matching the dataframe indices
def join_dataframes(dataframes):

	print('\nJoining dataframes...')
	df1 = dataframes[0][1]
	df2 = dataframes[1][1]
	df1.index.names = ['Date/Time']
	df2.index.names = ['Date/Time']

	# perform a join
	merged_df = df1.join(df2, how = 'outer', lsuffix = '_left', rsuffix = '_right')
	merged_df['Wind Spd (km/h)_left'] = merged_df['Wind Spd (km/h)_right'].fillna(merged_df['Wind Spd (km/h)_left'])
	merged_df['Wind Dir (10s deg)_left'] = merged_df['Wind Dir (10s deg)_right'].fillna(merged_df['Wind Dir (10s deg)_left'])
	del merged_df['Wind Dir (10s deg)_right'], merged_df['Wind Spd (km/h)_right']
	merged_df.rename(columns = {'Wind Spd (km/h)_left' : 'Wind Spd (km/h)'}, inplace = True)
	merged_df.rename(columns = {'Wind Dir (10s deg)_left' : 'Wind Dir (10s deg)'}, inplace = True)
	#with pd.option_context('display.max_rows', None, 'display.max_columns', 4):
		#print(df1)
		#print(df2)
	#	print(merged_df)
	return merged_df

def save_file(frame):

	# Convert the frame to hdf5 format
	#frame.to_hdf('Sisters_Island_All_Data', 'Sisters_Island_All_Data', append = True)

	# Convert the frame to .csv format
	frame.to_csv('Ballenas_Island_All_Data', sep = ',')

# The main function handles higher level program logic
def main(argv):

	if(len(argv) < 2):
		print("Please include the 2 files as program arguments.\nFiles should contain station data in hdf5 format: Station_Name_123456 where the number is the climate or station ID.")
		print("Filenames should be separated by spaces.\n")
		sys.exit(0)
	else:
		print('\n')
		# Load the data in to the program from the hdf files
		dataframes = load_files(argv[1:])
		#inner_join_dataframes(dataframes)
		final_frame = join_dataframes(dataframes)
		print(final_frame)
		save_file(final_frame)
		sys.exit(0)

if __name__ == "__main__":
	main(sys.argv)
