# -*- coding: utf-8 -*-
"""
Created on Sat Dec 05 14:41:06 2015

@author: Vipassana + Sara
"""

#add necessary libraries
import pandas as pd
import json

"""

Broad summary of what we did here:
# Read the data
# Filter for MNH only
# Obtain pairs of stations
# Frequency count of all pairs
# Selecting the N most frequent pairs
# Create a list of locations of most frequent start and end stations

"""

citibike = pd.read_csv('data/201307_201511citibike.csv')   
citibike = citibike[citibike.usertype=='Subscriber']

unique_citibike = pd.DataFrame({'count' : citibike.groupby( [ "start station id", "end station id"] ).size()}).reset_index()
       
start_stations = citibike.drop_duplicates('start station id')
end_stations = citibike.drop_duplicates('end station id')

# Useful list of names of Stations for data visualization purposes
station_names = start_stations[['start station id','start station name']]
station_names.to_csv('data/statnames.csv')

#Removing all columns except station id, latitude and longitude
start_stations = start_stations.drop(start_stations.columns[[0,1,2,3,5,8,9,10,11,12,13,14,15]], axis = 1)
end_stations = end_stations.drop(end_stations.columns[[0,1,2,3,4,5,6,7,9,12,13,14,15]], axis = 1 )

unique_citibike = pd.merge(unique_citibike, start_stations, on = 'start station id')
unique_citibike = pd.merge(unique_citibike, end_stations, on = 'end station id')

"""

Adding zip codes to the data

"""

with open('data/stationzips.json') as f:
    zip_bikes = json.load(f)
        
ZIP_Stations = pd.DataFrame(zip_bikes.items(), columns=['start station id', 'start_zip'])
ZIP_Stations['start station id'] = ZIP_Stations['start station id'].convert_objects(convert_numeric=True)

unique_citibike = pd.merge(unique_citibike ,ZIP_Stations,how='inner',on=['start station id'])

ZIP_Stations = pd.DataFrame(zip_bikes.items(), columns=['end station id', 'end_zip'])
ZIP_Stations['end station id'] = ZIP_Stations['end station id'].convert_objects(convert_numeric=True)

unique_citibike  = pd.merge(unique_citibike ,ZIP_Stations,how='inner',on=['end station id'])

"""

Extract data for Manhattan Only
`
"""

unique_citibike = unique_citibike[(unique_citibike.start_zip>=10002) & (unique_citibike.start_zip <= 10280)
                                    & (unique_citibike.end_zip>=10002) & (unique_citibike.end_zip <= 10280)]
unique_citibike.to_csv('data/unique_citibike201307-201511.csv')