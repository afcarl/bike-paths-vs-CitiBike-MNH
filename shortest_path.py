import geopandas as gpd

import googlemaps

import simplekml

import matplotlib.pyplot as plt

import mplleaflet

from fiona.crs import from_epsg

from shapely import geometry as geometry

from polyline.codec import PolylineCodec

import pandas as pd

# KML TO GEOJSON


cbike = pd.read_csv('top50.csv')

gmaps = googlemaps.Client(key='')

dirs = []


for i in cbike.index[:5]:

    xa = cbike['start station longitude'][i]
    ya = cbike['start station latitude'][i]
    xb = cbike['end station longitude'][i]
    yb = cbike['end station latitude'][i]
    directions = gmaps.directions((ya,xa), (yb,xb), mode='bicycling')

    #print directions
    codec = PolylineCodec()

    path = []

    for s in directions[0]['legs'][0]['steps']:

        path += codec.decode(s['polyline']['points'])
    # swap lat and lon
    pp = zip(*path)
    path = zip(pp[1], pp[0])
    lines = geometry.LineString(path)
    kml = simplekml.Kml()
    ls = kml.newlinestring(name='sample')
    ls.coords = lines.coords
    kml.save("/data/path" + str(i) + ".kml")




