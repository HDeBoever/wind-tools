README for the wind tools tool suite
@author: Henri De Boever
2018/07/26

  This "Read Me" file serves as general purpose overview of the tools developed for wind data collection, interpolation, mapping, and exporting.
  The tool suite includes the data scrapers, as well as the tools used to interact with the raw data files. The data was taken from its various sources,
  converted to pandas dataframes, and then stored into HDF compressed file formats for later visualization and interaction.

  Data Scrapers:
      csv_data_scraper.py
      environment_canada_data_scraper.py
      text_file_data_scraper.py

    Visualization tools:
        wind_analysis.py
        find_wind_peaks.py
        wind_surge_analysis.py
        join_dataframes.py

  1. - csv_data_scraper.py

    Core Dependencies:

    from datetime import datetime, date
    import pandas as pd
    import sys, os, shutil

    This tool was written to specifically scrape wind readings from the csv files for the Halibut Bank Buoy and the Sentry Shoal Buoy.
    Read the file in, insert the data pertaining to each climateID into an Ordered Dict
    Reformat it based on new parameters, then insert into a pandas dataframe

    Specifically programmed to read the data for the Halibut Bank Buoy, Station_ID = C46146
    and the Sentry Shoal Buoy, Station ID = C46131

    The overall functioning of this program is ressentially converting the .csv file to a pandas dataframe and storing it to HDF format.

  2. - environment_canada_data_scraper.py

      Core Dependencies:

      Anaconda for Python 3.6.5 (conda 4.5.2)
      from os import listdir
      from os.path import isfile, join
      import pandas as pd, numpy as np, csv, io, requests, os, sys, urllib, shutil

    The primary objective of this script is to poll the Environment Canada website for hourly csv data. The script converts the .csv files to equivalent pandas
    dataframes, concatenates them, then stores the final frame in HDF5 format in a folder called weather_station_data.

    The program will create a folder called weather_station_data to store the HDF5 files if one does not currently exist.

    Current Functionality:

    Since there is no way that the user could know of at the moment to get the station ID from the station name, we are currently finding the station ID from the URL.
    The program then uses the station ID alongside the time a measurement was taken to create a unique key for all the data points in the dataframes. This method
    is convenient since each station ID maps to a unique station, whereas the name may map to several different station IDs.

    The program polls the Environment Canada website by creating a new URL each time the user inputs a different station ID when the program is executed.

    Usage example e.g.

      The execution call:

      python3.6 environment_canada_data_scraper.py 118

      tells the program to search the Environment Canada website for the hourly weather data from station number '118', which in this case corresponds with
      'Victoria INTL A'.

    Since the Environment Canada data set contains information that was gathered from stations that either no longer exist, or has station data that
    starts at different times, the program also handles the time intervals for each station once the user has specified the date ranges for the station
    of interest in the get_station_data(station_id) function.

    Upon successful exit of the program, the user will find an HDF5 format file in a folder called weather_station_data.

    It is possible for the program to hang during execution possibly due to a large amount of server traffic on the Environment Canada servers.
    In that case, it may be advisable to exit the program with CTRL-C and attempt to re-execute the program, or to wait until the peak times for server
    usage on the east coast to subside.

    The program also includes a simple progress bar to track the number of frames that have been read from the website.

    Possible Future Improvements:

    I. Make it so that the entry of end dates for each station is dynamically polled from the Environment Canada Website
    II. Trying to sync local computer time with the remote server time
    III. Attempt to gracefully handle slow responses from the Environment Canada website by checking the status of the url requests.

  3. - text_file_data_scraper.py

    Core Dependencies:

    import pandas as pd
    import numpy as np
    import sys, os, re, shutil
    from collections import OrderedDict

    As in the environment_canada_data_scraper.py script, a correspondence had to be made between the climateIDs in the data, and the corresponding station names.
    Each text file is formatted in a deterministic way with different data types embedded in it. This python scripts goes thorugh the input text files
    and obtains the relevant data from each for each station. Once that has been completed,the files are converted to HDF format.
