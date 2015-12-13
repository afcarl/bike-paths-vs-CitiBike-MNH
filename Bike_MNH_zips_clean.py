# -*- coding: utf-8 -*-
"""
Created on Sat Dec 12 18:07:29 2015

@author: vv744

This script cleaned and formatted all the filtered citibike code for manhattan from arcgis
"""


import pandas as pd 
import re

unique_citibike_spatial = pd.read_csv('data/data_export_forVipa_GOOD.txt', sep=';')
unique_citibike_spatial = unique_citibike_spatial.drop(['FID', 'FID_','Field1'], axis = 1)
uc = pd.read_csv('data/unique_citibike201307-201511.csv', index_col = 0)
unique_citibike_spatial.columns = uc.columns
unique_citibike_spatial.to_csv('unique_citibike_spatial.csv')