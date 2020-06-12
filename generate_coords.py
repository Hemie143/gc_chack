import re
import sqlite3
from LatLon23 import string2latlon, LatLon
from gc_lib.coords import Coords_square, Coords_circle


####################### function: get latlon

def get_latlon(coords):
    # Find boundary box with max 2 miles from coords
    r = re.search('([NS][ ]*[0-9]+°?[ ]*[0-9,.]+)[ ]+([WE][ ]*[0-9]+°?[ ]*[0-9,.]+)', coords)
    gc_lat = r.group(1)
    gc_lon = r.group(2)
    # print(gc_latlon.to_string('D'))
    # print(gc_latlon)
    return string2latlon(gc_lat, gc_lon, 'H% %d%° %M')
####################### function: get_zone, params central coords and radius


def load_physicalwps():
    # wp_list = []
    gc_filename = 'geocheck.sqlite'
    conn_gc = sqlite3.connect(gc_filename)
    c = conn_gc.cursor()
    c.execute("SELECT wp_lat, wp_lon from physical_waypoints")
    wps = c.fetchall()
    conn_gc.close()
    return [string2latlon(str(w[0]), str(w[1]), 'd') for w in wps]

    '''
    # Format : N5057631E00410274
    i = 0
    for _ in range(10):
        # print(coords_zone.__next__())
        target = coords_zone.__next__()
        i += 1
    exit()
    print(i)

    # TODO: Check features of matplotlib/basemap to draw points on map and eliminate some points
    # https://basemaptutorial.readthedocs.io/en/latest/index.html
    # https://matplotlib.org/basemap/
    # https://jakevdp.github.io/PythonDataScienceHandbook/04.13-geographic-data-with-basemap.html
    # https://www.reddit.com/r/learnpython/comments/2ldevz/python_gui_with_google_maps/
    # https://wiki.openstreetmap.org/wiki/WikiProject_Corine_Land_Cover
    # https://developer.mapquest.com/documentation/open/geocoding-api/
    # https://opencagedata.com/api
    # https://wiki.openstreetmap.org/wiki/Develop
    # https://towardsdatascience.com/mapping-geograph-data-in-python-610a963d2d7f
    # https://rabernat.github.io/research_computing/intro-to-basemap.html
    # https://www.gislounge.com/tools-qgis-python-programming-cookbook/
    # https://www.gislounge.com/creating-dynamic-maps-in-qgis-using-python/
    
    
    
    

    i = 0
    for c in coords_zone:
        if c[1] < distance:
            i += 1
    print(i)

    exit()
    for c in coords_zone:
        print(c)

    # Fill in table geocheck with possible coords (if not already present) and tag to test
    # First count number of coordinates
    '''

if __name__ == '__main__':
    # gccode = 'GC85ZZ8'
    gccode = 'GC865QG'
    # gc_coords = 'N 50° 57.836 E 004° 10.188'
    gc_coords = 'N 50° 59.000 E 004° 09.000'
    # geocheck_gid = '6371353e6d45420-ab85-4673-88db-3c8e7082b65d'
    geocheck_gid = '6371614775bf720-b6fe-40c7-95bd-6af2b506d761'

    coordsll = get_latlon(gc_coords)
    # print(coordsll)
    mile = 1.609344     # in km
    distance = 2*mile   # 2 miles in km
    # borders = get_borders(coordsll, distance)
    # print(borders)

    # Generator with all coords within circle and remove points with saturation (physical_waypoints)
    # Number of points within square: 19E6
    # Number of points within circle: 15E6
    # Number of points within circle not saturated: 14.4E6
    coords_zone = Coords_circle(coordsll, distance)
    # print(coords_zone)


    table_filename = 'geocheck.sqlite'
    conn = sqlite3.connect(table_filename)
    c = conn.cursor()

    i = 0
    for target in coords_zone:
        # print(target)
        targetLL = target[0]

        c.execute("INSERT INTO geocheck VALUES (?, ?)", (gccode, target[1], 'TEST'))
        conn.commit()

    conn.close()

    i += 1
        if i % 1000 == 0:
            print(target)

    print(i)

    physical_waypoints = load_physicalwps()
    # print(physical_waypoints)
    print(f'pWP: {(physical_waypoints)}')
    # exit()

    '''
        saturated = False
           for wp in physical_waypoints:
            distance = targetLL.distance(wp)
            if distance < 0.161:
                saturated = True
                break
        if saturated:
            print('Saturation')
            continue
'''