# Last edited on 2018/05/04 by Henri De Boever
# Created for exclusive use by Cascadia Coast Research

# 1 Pulls monthly meteorological data from the Environment Canada website for a specific station by station ID
# 2 Concatenates the data into a multi-year Pandas data frame.

from os import listdir
import pandas as pd, numpy as np, csv, io, requests, os, sys, urllib, shutil

# Get the associated station name for a given station ID
# I have also included approximate start and end dates for each data set
# This function returns the station name, start year, and start month for the dataset
# The start year will be used to index the loop when creating pandas dfs in get_station_data(station_id)
def get_station_data(station_id):

	if(int(station_id) == 192):
		# Start = 1954/01/01
		# End = 2013/05/16
		return ("Nanaimo A", 1954, 2013)
	elif(int(station_id) == 227):
		# Start = 1980/05/01
		# End = 2001/10/09
		return ("Amphitrite Point", 1980, 2001)
	elif(int(station_id) == 8040):
		# Start = 1994/02/01
		# End = Present
		return ("Estevan Point CS", 1994, 2018)
	elif(int(station_id) == 52):
		# Start = 1994/02/01
		# End = Present
		return ("Esquimalt Harbour", 1994, 2018)
	elif(int(station_id) == 6811):
		# Start = 1994/02/01
		# End = Present
		return ("Sheringham Point", 1994, 2018)
	elif(int(station_id) == 10943):
		# Start = 1994/02/01
		# End = Present
		return ("Race Rocks", 1994, 2018)
	elif(int(station_id) == 277):
		# Start = 1960/01/01
		# End = 2014/05/01
		return ("Tofino A", 1960, 2014)
	elif(int(station_id) == 10944):
		# Start = 1994/07/01
		# End = 2015/02/12
		return ("Victoria Harbour A", 1994, 2015)
	elif(int(station_id) == 51318):
		# Start = 2013/05/16
		# End = Present
		return ("Nanaimo A", 2013, 2018)
	elif(int(station_id) == 52941):
		# Start = 2014/10/23
		# End = Present
		return ("Nanaimo A", 2014, 2018)
	elif(int(station_id) == 138):
		# Start = on 1994/02/01
		# End = Present
		return ("Ballenas Island", 1994, 2018)
	elif(int(station_id) == 145):
		# Start = on 1979/03/01
		# End = 2013/06/13
		return ("Campbell River A", 1979, 2013)
	elif(int(station_id) == 52979):
		# Start = 2014/10/23
		# End = Present
		return ("Campbell River A", 2014, 2018)
	elif(int(station_id) == 51317):
		# Start = 2013/06/11
		# End = Present
		return("Campbell River A", 2013, 2018)
	elif(int(station_id) == 152):
		# Start = on 1994/02/01
		# End = 2001/12/13
		return ("Cape Mudge", 1994, 2001)
	elif(int(station_id) == 27289):
		# Start = on 1997/06/18
		# End = 1998/06/05
		return ("Chrome Island", 1986, 1998)
	elif(int(station_id) == 155):
		# Start = on 1953/01/01
		# End = Present
		return ("Comox A", 1953, 2018)
	elif(int(station_id) == 27226):
		# Start = on 1997/01/02
		# End = 2018/03/04
		return ("Discovery Island", 1997, 2018)
	elif(int(station_id) == 29411):
		# Start = on 1994/02/01
		# End = Present
		return ("Entrance Island", 1994, 2018)
	elif(int(station_id) == 27449):
		# Start = on 1997/11/28
		# End = Present
		return ("Grief Point", 1997, 2018)
	elif(int(station_id) == 6817):
		# Start = 1994/02/08
		# End = Present
		return ("Howe Sound Pam Rocks", 1994, 2018)
	elif(int(station_id) == 10853):
		# Start = on 1997/03/14
		# End = Present
		return ("Kelp Reefs", 1997, 2018)
	elif(int(station_id) == 65):
		# Start = 1994/02/01
		# End = Present
		return ("Malahat", 1994, 2018)
	elif(int(station_id) == 320):
		# Start = on 1954/01/01
		# End = 2001/12/13
		return ("Merry Island Lightstation", 1954, 2001)
	elif(int(station_id) == 26822):
		# Start = on 1994/05/31
		# End = 1995/08/14
		return ("Nanaimo Harbour", 1994, 1995)
	elif(int(station_id) == 844):
		# Start = on 1996/05/31
		# End = Present
		return ("Point Atkinson", 1996, 2018)
	elif(int(station_id) == 8045):
		# Start = 1994/02/01
		# End = Present
		return ("Port Alberni AUT", 1994, 2018)
	elif(int(station_id) == 327):
		# Start = on 1982/03/23
		# Ends 2013/12/31
		return ("Powell River A", 1982, 2013)
	elif(int(station_id) == 51438 or int(station_id) == 52018):
		# Start = on 2013/12/09
		# Ends 2018/05/01
		return ("Powell River A", 2013, 2018)
	elif(int(station_id) == 45807):
		# Start = 2007/07/10
		# End = Present
		return ("Powell River", 2007, 2018)
	elif(int(station_id) == 45627):
		# Start = 2006/12/11
		# End = Present
		return ("Qualicum Beach Airport", 2006, 2018)
	elif(int(station_id) == 6831):
		# Start = 1994/02/01
		# End = Present
		return ("Sandhead CS", 1994, 2018)
	elif(int(station_id) == 6810):
		# Start = 2006/06/09
		# End = Present
		return ("SATURNA CAPMON CS", 2006, 2018)
	elif(int(station_id) == 7997):
		# Start = 1980/06/10
		# End = 1992/12/31
		return ("Saturna Island Campbell Scientific", 1980, 1992)
	elif(int(station_id) == 96):
		# Start = 1994/02/28
		# End = Present
		return ("Saturna Island CS", 1994, 2018)
	elif(int(station_id) == 45788):
		# Start = 2007/07/11
		# End = Present
		return ("Sechelt AUT", 2007, 2018)
	elif(int(station_id) == 6813):
		# Start = 1995/02/16
		# End = Present
		return ("Sisters Island", 1995, 2018)
	elif(int(station_id) == 336):
		# Start = 1982/05/17
		# End = Present
		return ("Squamish Airport", 1982, 2018)
	elif(int(station_id) == 27290):
		# Start = 1997/01/01
		# End = 1998/06/05
		return ("Trial Island", 1997, 1998)
	elif(int(station_id) == 50228):
		# Start = 2012/04/30
		# End = Present
		return ("Tsawwassen Ferry AUTO", 2012, 2018)
	elif(int(station_id) == 888):
		# Start = 1976/01/20
		# End = Present
		return ("Vancouver Harbour CS", 1976, 2018)
	elif(int(station_id) == 889):
		# Start = 1953/01/01
		# End = 2013/06/13
		return ("Vancouver INTL A", 1953, 2013)
	elif(int(station_id) == 51442):
		# Start = 2013/06/11
		# End = Present
		return ("Vancouver INTL A", 2013, 2018)
	elif(int(station_id) == 51357):
		# Start = 2013/03/20
		# End = Present
		return ("Vancouver Sea Island CCG", 2013, 2018)
	elif(int(station_id) == 903):
		# Start = 1957/09/20
		# End = 1995/06/30
		return ("Vancouver UBC", 1975, 1995)
	elif(int(station_id) == 114):
		# Start = 1994/02/01
		# End = Present
		return ("Victoria Gonzales CS", 1994, 2018)
	elif(int(station_id) == 113):
		# Start = 1953/01/01
		# End = 2000/03/14
		return ("Victoria Gonzales HTS", 1953, 2000)
	elif(int(station_id) == 118):
		# Start = 1953/01/01
		# End = 2013/07/11
		return ("Victoria INTL A", 1953, 2013)
	elif(int(station_id) == 51337):
		# Start = 2013/07/09
		# End = Present
		return ("Victoria INTL A", 2013, 2018)

# Check if the directory weather_station_data exists;
# If it does not, then create it
def check_directory(dir_name):
	print("Checking if the directory %s exists." % (dir_name))
	path = os.getcwd() +'/' + dir_name
	if(os.path.exists(path)):
		print("%s exists." % (dir_name))
	else:
		print("Creating directory %s to store HDF5 files.")
		os.makedirs(path)

# A helper function to display progress bar while the frames are being read in
def progress_bar(value, endvalue, bar_length=25):
	percent = float(value) / endvalue
	arrow = '-' * int(round(percent * bar_length)-1) + '>'
	spaces = ' ' * (bar_length - len(arrow))
	sys.stdout.write("\rPercent: [{0}] {1}%".format(arrow + spaces, int(round(percent * 100))))
	sys.stdout.flush()

# Returns the status of a given url request to check the connection
def get_request_status(url):
	try:
		r = requests.get(url)
	except request.exceptions.Timeout as e:
		return e
	return r.status_code

# Get data by station ID and start date
# Function takes a string for the station_id, and a string for the start year
# This function is designed to specificcally work with the csv files found on the
# Governement of Canada website hourly climate data.
# Returns a list of dfs called frames
def get_weather_data(station_id):

	# Set this option to see more columns when printing pandas dfs
	pd.set_option('display.expand_frame_repr', False)

	# Obtain station name and the start year for that particuar station id using the get_station_data helper function
	station_name  = get_station_data(station_id)[0]
	start_year = get_station_data(station_id)[1]
	end_year = get_station_data(station_id)[2]
	year_gap = end_year - start_year
	# create a filename based on the station name
	filename = (str(station_name) + " " + str(station_id)).replace(" ", "_")

	#Check if an HDF5 format file containing the data already exists
	path = os.getcwd()
	relative_path = path + "/processed/" + filename
	if(os.path.isfile(relative_path)):
		print("\n%s exists in HDF5 format in /weather_station_data and can be read." % (filename))
		df = pd.read_hdf(relative_path, key = filename, mode = 'r')
		return df
	else:
		# If no HDF5 file is found in the current directory, make one
		print("\nFile was not found in %s.\nProceeding to create it using data on the Governement of Canada website datasheets." % (relative_path))
		print("\nPopulating meteorological data pandas frames for station %s.\n\nStation ID: %s\nStart Year: %s\nEnd Year: %s\n" % (station_name, station_id, start_year, end_year))
		print("The total number of frames that will have to be created and concatenated is: %d\n" % (year_gap*12))

		frames = []
		# Generate the URLs for a given date range and station ID, and create dfs from the csvs found in them
		for year in range(int(start_year), int(end_year) + 1):
			for month in range (1, 13):
				url = "http://climate.weather.gc.ca/climate_data/bulk_data_e.html?format=csv&stationID=%s&Year=%s&Month=%s&Day=1&timeframe=1&submit=Download+Data" \
				 % (str(station_id), str(year), str(month))

				# Check the requests status of the url, if it is 200, then create a df
				if(get_request_status(url) != 200):
					print("Invalid request: %s\n%s" % (url, get_request_status(url)))
					continue
				else:
					# Load it into a pandas frame, skip the first 15 rows of the input to avoid repetition of the column headers
					df = pd.read_csv(url, error_bad_lines = False, skiprows = 15)
					# Set the key of the df to be the Date/Time column
					df = df.set_index("Date/Time")
					frames.append(df)
					#print("Sucessfully appended frame #%d to the list" % (frame_number))
				if(year < end_year):
					progress_bar(len(frames), (year_gap*12))

		# Iterating through the list of dfs and concatenating them together
		print("\n\nNow concatenating monthly frames into a single multi-year frame...\n")
		df = frames.pop(0)
		for frame in frames:
			df = df.append(frame)

		# Store the df to HDF5 format to the current directory
		df.to_hdf(filename, filename, append = True)
		# Move the file to the appropriate folder
		shutil.move(path + "/" + filename, relative_path)
		print("Successfully downloaded the data for %s in single dataframe." % station_name)

# The main function takes care of the overall program logic
def main(argv):

	if(len(argv) < 2):
		print("Not enough arguments. Please include the station ID as the second argument.")
		exit(0)
	else:
		# Getting Hourly Data by Station #ID
		check_directory("processed")
		get_weather_data(argv[1])
		sys.exit(0)

if __name__ == "__main__":
	   main(sys.argv)
