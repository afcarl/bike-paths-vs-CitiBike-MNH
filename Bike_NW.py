# -*- coding: utf-8 -*-
"""
Created on Sat Dec 05 14:41:06 2015

@author: Vipassana + Sara
"""

#add necessary libraries
import networkx as nx #library supporting networks
import matplotlib.pyplot as plt #plotting
import pandas as pd
import numpy as np
import scipy.stats as stat
import statsmodels.formula.api as smf

# Read the data

# Filter for MNH only

# Obtain pairs of stations

# Frequency count of all pairs

# Selecting the N most frequent pairs

# Create a list of locations of most frequent start and end stations

# Calculate the shortest paths using those locations (how would that be stored?)

# Summarize the street characteristics of the routes, maybe weighted by the frequency

citibike = pd.read_csv('201307_201511citibike.csv')   
unique_citibike = pd.DataFrame({'count' : citibike.groupby( [ "start station id", "end station id"] ).size()}).reset_index()
       
start_stations = citibike.drop_duplicates('start station id')
end_stations = citibike.drop_duplicates('end station id')
start_stations = start_stations.drop(start_stations.columns[[0,1,2,3,5,8,9,10,11,12,13,14,15]], axis = 1)
end_stations = end_stations.drop(end_stations.columns[[0,1,2,3,4,5,6,7,9,12,13,14,15]], axis = 1 )

unique_citibike = start_stations.merge(unique_citibike, on = 'start station id')
unique_citibike = end_stations.merge(unique_citibike, on = 'end station id')

##upload NYC intersections
NYCintersections = pd.read_csv( 'https://serv.cusp.nyu.edu/files/ADS-2015/NetworkAnalysis/lab2/ManhattanStreetMap_nodes.csv' , index_col=0, header=-1 )
NYCintersections.columns=['Y','X','m']

#read the network edges - street connections between adjacent nodes
NYCstreets = pd.read_csv( 'https://serv.cusp.nyu.edu/files/ADS-2015/NetworkAnalysis/lab2/StreetMap_edges.csv' , index_col=None, header=-1 )
NYCstreets.columns=['A','B']

#number of street intersections on Lower Manhattan
InManhattan={}
for c in NYCintersections.index:
    InManhattan[c]=NYCintersections.m[c]
   
#create a dictionary of intersection locations and Manhattan flags
IntPos={}
for c in NYCintersections.index:
    IntPos[c]=(NYCintersections.X[c],NYCintersections.Y[c])

#creare a directed graph representing street network
NYCStreets=nx.DiGraph()
for i in NYCstreets.index:
    #adding only streets inside Manhattan
    if InManhattan[NYCstreets.A[i]]&InManhattan[NYCstreets.B[i]]:
       NYCStreets.add_edge(NYCstreets.A[i],NYCstreets.B[i])
#
#take the largest strongly connected component for having a connected network of major streets 
#(it somehow happened during the parsing that minor roads got disconneted from the major ones 
#as being absent among the ways)
MLC=sorted(nx.strongly_connected_components(NYCStreets), key=len, reverse=True)
NYCStreetsC=NYCStreets.subgraph(MLC[0])

##visualize the street newtork
#plt.figure(figsize = (15,18))
#nx.draw(NYCStreetsC,pos=IntPos,with_labels=False,arrows=False,node_size=1,width=1,edge_color='green')
#
##auxiliary function: geodesic distance on the Earth surface between two lat-long points
from math import sin, cos, sqrt, atan2, radians
def geodist(lon1,lat1,lon2,lat2):
    lat1 = radians(lat1)
    lon1 = radians(lon1)  
    lat2 = radians(lat2)
    lon2 = radians(lon2)
    R = 6373.0
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c
#
##add length attribute to the edges
nx.set_edge_attributes(NYCStreetsC, 'dist', 0)
#
##compute and assing lengths the all the edges
for e in NYCStreetsC.edges():
   NYCStreetsC[e[0]][e[1]]['dist']=geodist(IntPos[e[0]][0],IntPos[e[0]][1],IntPos[e[1]][0],IntPos[e[1]][1])
   
##auxiliary function for locating intersections of interest: get the closest street intersection to a given point
def closest(lon,lat):
    c=0
    d=1000000000000000000000000000000000000000000000#Inf
    for n in NYCStreetsC.nodes():
        d1=geodist(IntPos[n][0],IntPos[n][1],lon,lat)
        if d1<d:
            c=n
            d=d1
    return c 
    
#find node closest to world trade center, Empire State Building and Metropolitan Museum of Art
node_wtc=closest(-74.0125,40.7117)
node_emp=closest(-73.9857,40.7484)
node_mma=closest(-73.9637,40.7789)
print('WTC:{0}'.format(node_wtc))
print('Empire St. Bld.:{0}'.format(node_emp))
print('Metropolitan Museum:{0}'.format(node_mma))

#compute shortest paths, first without distances, just number of edges
path_wtc_emp=nx.shortest_path(NYCStreetsC,node_wtc,node_emp)


path_StartEnd = [[],[],[]]
for i in unique_citibike.index:
    path_StartEnd[i,0] = nx.shortest_path(NYCStreetsC,
                        closest(unique_citibike[i][['start station longitude','start station latitude']]),
                        closest(unique_citibike[i][['end station longitude','end station latitude']]))
    path_StartEnd[i,1] = closest(unique_citibike[i][['start station longitude','start station latitude']])
    path_StartEnd[i,2] = closest(unique_citibike[i][['start station longitude','start station latitude']])
    
paths         = pd.DataFrame(path_StartEnd)
paths.columns = ['Route','Start coords', 'End coords']




#


#auxiliary function - visualize path on the map
def visualize_path(path):
    plt.figure(figsize = (15,18))
    nx.draw(NYCStreetsC,pos=IntPos,with_labels=False,arrows=False,node_size=1,width=1,edge_color='green')
    x=[IntPos[v][0] for v in path]
    y=[IntPos[v][1] for v in path]
    plt.plot(x,y,'ro-')
    plt.plot([x[0],x[-1]],[y[0],y[-1]],'bs',markersize=10)
    
visualize_path(path_wtc_emp)
