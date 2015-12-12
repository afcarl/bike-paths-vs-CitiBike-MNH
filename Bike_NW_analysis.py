# -*- coding: utf-8 -*-
"""
Created on Thu Dec 10 15:07:35 2015

@author: saf537
"""

"""

Create network of Streets in NYC

"""

import numpy as np
import scipy.stats as stat
import statsmodels.formula.api as smf
import networkx as nx #library supporting networks
import matplotlib.pyplot as plt #plotting
import pandas as pd

# Read data
cbike = pd.read_csv( 'data/unique_citibike201307-201511.csv' , index_col=0)
station_names = pd.read_csv('data/statnames.csv')

##upload NYC intersections
NYCintersections = pd.read_csv( 'data/ManhattanStreetMap_nodes.csv' , index_col=0, header=-1 )
NYCintersections.columns=['Y','X','m']

#read the network edges - street connections between adjacent nodes
NYCstreets = pd.read_csv( 'data/StreetMap_edges.csv' , index_col=None, header=-1 )
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
#node_wtc=closest(-74.0125,40.7117)

#print('WTC:{0}'.format(node_wtc))

#compute shortest paths, first without distances, just number of edges
#path_wtc_emp=nx.shortest_path(NYCStreetsC,node_wtc,node_emp)

"""

Create shortest route matrix and network

"""

path_StartEnd = []
citinetwork = cbike
cbike = cbike.sort('count', ascending=False)[:10]
cbike = cbike.reset_index()
for i in cbike.index.get_values():
    path_StartEnd.append(nx.shortest_path(NYCStreetsC,
                        closest(cbike.iloc[i][['start station longitude']], cbike.iloc[i][['start station latitude']]),
                        closest(cbike.iloc[i][['end station longitude']], cbike.iloc[i][['end station latitude']]),'dist'))
    #path_StartEnd[i,1] = closest(unique_citibike.iloc[i][['start station longitude','start station latitude']])
    #path_StartEnd[i,2] = closest(unique_citibike.iloc[i][['start station longitude','start station latitude']])
    
#paths         = pd.DataFrame(path_StartEnd)
#paths.columns = ['Route','Start coords', 'End coords']


#


#auxiliary function - visualize path on the map
def visualize_path(path):
    plt.figure(figsize = (8,10))
    nx.draw(NYCStreetsC,pos=IntPos,with_labels=False,arrows=False,node_size=0.5,width=1,edge_color='gray')
    x=[IntPos[v][0] for v in path]
    y=[IntPos[v][1] for v in path]
    plt.plot(x,y,'ro-')
    plt.plot([x[0],x[-1]],[y[0],y[-1]],'bs',markersize=10)    
    
visualize_path(path_StartEnd[0])  
        
"""

Visualize the N shortest paths inside the Manhattan network

Important: automatize plots.

def save_path_plots(path_list):
    it = 1
    for path in path_list:
        fig = plt.figure(figsize = (8,10))
        fig.add_subplot(nx.draw(NYCStreetsC,pos=IntPos,with_labels=False,arrows=False,node_size=0.5,width=1,edge_color='gray'))
        x=[IntPos[v][0] for v in path]
        y=[IntPos[v][1] for v in path]
        plt.plot(x,y,'ro-')
        plt.plot([x[0],x[-1]],[y[0],y[-1]],'bs',markersize=10) 
        plt_nm = 'Route' + it + '.png'
        #plt.savefig(plt_nm)
        it +=1

"""


"""
SARA STARTS HERE.
Interesting plots:
- Proportion of trips per origin-destination pair
- Number of intersections per distance, per origin-destination pair
- (Visualization above)
- 

"""
citinetwork['prop_trips'] = 100*citinetwork['count'] / citinetwork['count'].sum()
plt.plot( (citinetwork.sort('prop_trips', ascending=False))['prop_trips'])

"""

Interesting analysis:
- Representing CB as a network and finding the most important stations in terms of conectivity.
- Could we cluster, or find groups of stations? What would be the relevance of this?

"""



CB_nw = nx.DiGraph()
nx.set_edge_attributes(CB_nw,'weight',0)
for k in citinetwork.index:
    CB_nw.add_edge(citinetwork['start station id'][k],citinetwork['end station id'][k],weight=citinetwork['prop_trips'][k])



w_CB = [d['weight'] for (u,v,d) in CB_nw.edges(data=True)]

# closest(cbike.iloc[i][['end station longitude']], cbike.iloc[i][['end station latitude']])
pos_CB = {citinetwork['start station id'][i]: (citinetwork['start station latitude'][i],citinetwork['start station longitude'][i]) for i in citinetwork.index}
#nx.draw(CB_nw,width=w_CB,pos=pos_CB,node_size=30)
#nx.draw(NYCStreetsC,pos=IntPos,with_labels=False,arrows=False,node_size=0.5,width=1,edge_color='gray')


# Betweenness, pagerank, eigenvectot

# Finding the most important Citibike Stations from the Networks perspective and visually check if they are surrounded by bike lanes.

#output top tn centrality scores, given the dictionary d
def topdict(d,tn):
    ind=sorted(d, key=d.get, reverse=True)
    for i in range(0,tn):
       print('{0}|{1}:{2}'.format(i+1,station_names[station_names['start station id']==ind[i]]['start station name'],d[ind[i]]))

c2= nx.eigenvector_centrality(CB_nw)
topdict(c2,10)

c5 = nx.pagerank(CB_nw,0.85)
topdict(c5,10)

path_topo = []
for i in cbike.index.get_values():
    path_topo.iloc[i] = [cbike.iloc[i][['start station id']],cbike.iloc[i][['end station id']],nx.shortest_path(NYCStreetsC,
                        closest(cbike.iloc[i][['start station longitude']], cbike.iloc[i][['start station latitude']]),
                        closest(cbike.iloc[i][['end station longitude']], cbike.iloc[i][['end station latitude']]))]


data=pd.DataFrame({'start':[],'end':[],'path':[]})
for e in cbike.index.get_values():
    i=data.index.max()
    if np.isnan(i):
        i=-1
    data.loc[i + 1] = [cbike.iloc[i][['start station id']],cbike.iloc[i][['end station id']],nx.shortest_path(NYCStreetsC,
                        closest(cbike.iloc[i][['start station longitude']], cbike.iloc[i][['start station latitude']]),
                        closest(cbike.iloc[i][['end station longitude']], cbike.iloc[i][['end station latitude']]))]

# Number of intersections for the most common trips (or number of intersections per number of trips per edge) - maybe map that out.


# Calculate the degree of the stations

