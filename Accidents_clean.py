'''
This script cleans the motor vehicle accident data set to include only accidents involving bicycles
and from the time citibike was introduced in nyc .
'''
import pandas as pd
import datetime as dt


accident_df = pd.read_csv('data/NYPD_Motor_Vehicle_Collisions.csv')
bike_accident_df = accident_df[(accident_df['VEHICLE TYPE CODE 1'] == 'BICYCLE') | (accident_df['VEHICLE TYPE CODE 2'] == 'BICYCLE') | (accident_df['VEHICLE TYPE CODE 3'] == 'BICYCLE') | (accident_df['VEHICLE TYPE CODE 4'] == 'BICYCLE') | (accident_df['VEHICLE TYPE CODE 5'] == 'BICYCLE')]
bike_accident_df['DATE'] = pd.to_datetime(bike_accident_df['DATE'])
bike_accident_df = bike_accident_df[(bike_accident_df['DATE'] > '2013-07-01') & (bike_accident_df['DATE'] < '2015-12-01')]
bike_accident_df.to_csv('citbike_accidents.csv')