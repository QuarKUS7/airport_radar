import json
import matplotlib.pyplot as plt
from matplotlib import animation
import cartopy.crs as ccrs
from cartopy.io.img_tiles import OSM, GoogleTiles
import requests
from cartopy.io import shapereader
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
import sys
from geopy import Point
from geopy.distance import vincenty

#GPS COORDINATES OF A POINT WE WANT TO OBSERVE
DEFAULT_LATITUDE = 50.10049959
DEFAULT_LONGITUDE = 14.255998976

def create_map(projection):
    # create figure and ax with gridlines and formated axes
    fig, ax = plt.subplots(figsize=(10, 10),
                           subplot_kw=dict(projection=projection))
    gl = ax.gridlines(draw_labels=True)
    gl.xlabels_top = False
    gl.ylabels_right = False
    gl.xformatter = LONGITUDE_FORMATTER
    gl.yformatter = LATITUDE_FORMATTER
    return fig, ax

def update_flights(self, long, lat, dist):
    # Request fro AdsExchange API
    url = 'http://public-api.adsbexchange.com/VirtualRadar/AircraftList.json'
    payload = {'lat': lat, 'lng': long,'fDstL': 0, 'fDstU': dist}
    #r = requests.get('http://public-api.adsbexchange.com/VirtualRadar/AircraftList.json?lat={}&lng={}&fDstL=0&fDstU={}'.format(lat, long, distKm), headers={'Connection':'close'})
    r = requests.get(url, params=payload, headers={'Connection':'close'})
    js_str=r.json()
    lat_list=[]
    long_list=[]
    #print(js_str)
    # Chekc if call was correct
    if js_str['lastDv'] == str(-1):
        return track_flights, annotation_list

    # Clean annotation list
    for anot in annotation_list:
        anot.remove()
    annotation_list[:] = []
    fig.canvas.draw()

    # Get lat, long a name of all flights
    for flight in js_str['acList']:
        latitude = flight['Lat']
        longitude = flight['Long']
        icao = flight['Icao']
        lat_list.append(latitude)
        long_list.append(longitude)
        #print((icao, longitude, latitude))
        anonnotation = ax.annotate(icao,
                    xy=(longitude,latitude), fontsize=8, fontweight='bold')
        annotation_list.append(anonnotation)
    track_flights.set_data(long_list,lat_list)
    return track_flights,

def create_extent(long, lat, dist):
    # TODO: rewrite to a loop
    # Callculate gps coordinates for square around point of interest
    extent_north =  vincenty(kilometers=dist).destination(Point(lat, long), 0).format_decimal()
    extent_east = vincenty(kilometers=dist).destination(Point(lat, long), 90).format_decimal()
    extent_south = vincenty(kilometers=dist).destination(Point(lat, long), 180).format_decimal()
    extent_west =  vincenty(kilometers=dist).destination(Point(lat, long), 270).format_decimal()
    return [float(extent_west.split(',')[1]), float(extent_east.split(',')[1]), float(extent_south.split(',')[0]), float(extent_north.split(',')[0])]

if __name__ == '__main__':

    print("loading")
    distKm = 200

    # Check if point of interest was correctly given
    # If not take default (Letiste Vaclav Havel)
    if len(sys.argv) == 3:
        latitude = float(sys.argv[1])
        longitude = float(sys.argv[2])
    else:
        latitude = DEFAULT_LATITUDE
        longitude = DEFAULT_LONGITUDE
        print("Using default values. Your arguments are wrong")

    # Create projection and tiles. See cartopy pckg for more info
    projection = ccrs.PlateCarree()
    annotation_list = []
    osm_tiles=GoogleTiles()

    extent = create_extent(longitude, latitude,  distKm)
    fig, ax = create_map(projection)

    # Put together extented projection with ax
    ax.set_extent(extent, projection)
    ax.add_image(osm_tiles,8,interpolation='spline36')
    ax.plot([longitude],[latitude], 'bs')
    track_flights, = ax.plot([],[],'ro')#, fillstyle='none')
    fig.suptitle('This is a somewhat long figure title', fontsize=16)

    # Update the plot every 2 seconds until close
    anim = animation.FuncAnimation(fig, update_flights,fargs=[longitude, latitude,  distKm], interval=2000, blit=False)
    plt.show()
