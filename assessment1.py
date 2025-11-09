"""
Understanding GIS: Assessment 1
@author [INSERT STUDENT NUMBER HERE]
"""
from time import perf_counter

# set start time
start_time = perf_counter()	

# --- NO CODE ABOVE HERE ---


''' --- ALL CODE MUST BE INSIDE HERE --- '''

# Import required libraries
import geopandas as gpd
from pyproj import Geod




# 1.Data loading and preprocessing

# Initialize Geod pbject with WGS84 ellipsoid
geod = Geod(ellps='WGS84')

# Load country boundary data
world = gpd.read_file("./data/natural-earth/ne_10m_admin_0_countries.shp")

# Print basic data information
print(f"Number of valid countries:{len(world)}")


# 2.Spatial index construction

# Extract country geometries and build STRtree spatial index
geometries = world['geometry'].tolist()


# --- NO CODE BELOW HERE ---

# report runtime
print(f"completed in: {perf_counter() - start_time} seconds")