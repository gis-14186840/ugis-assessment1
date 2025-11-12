"""
Understanding GIS: Assessment 1
@author [14186840]
"""
from time import perf_counter

# set start time
start_time = perf_counter()	

# --- NO CODE ABOVE HERE ---


''' --- ALL CODE MUST BE INSIDE HERE --- '''

# Import required libraries
import geopandas as g
from pyproj import Geod
from matplotlib.pyplot import subplots, title, savefig
from matplotlib_scalebar.scalebar import ScaleBar
from matplotlib.patches import Patch

# 1.Data load

# Set ellipsoid
geod = Geod(ellps='WGS84')

# Load country boundary data
world = g.read_file("./data/natural-earth/ne_10m_admin_0_countries.shp")


# 2.Spatial index construction

# Build STRtree spatial index
spatial_index = g.GeoSeries(world['geometry']).sindex

# Store border results
shortest_length = float('inf')
shortest_border = None


# 3.Border calculation and length measurement

# loop through all countries
for i in range(len(world)):
    
    # Get country information
    country_a = world.iloc[i]
    geom_a = country_a['geometry']
    
    # Check candidate countries that may intersect with current country
    candidate = list(spatial_index.query(geom_a, predicate='intersects'))
    
    # Loop all countries and calculate intersection
    for j in candidate:
        
        # Skip duplicates
        if i >= j:
            continue
        
        # Get country information
        country_b = world.iloc[j]
        geom_b = country_b['geometry']
        
        # Calculate intersection of the two countries' boundaries
        border = geom_a.intersection(geom_b)
        
        # Filter invalid borders
        if border.is_empty or border.geom_type not in ['LineString', 'MultiLineString']:
            continue
        
        # initialise a variable to hold the cumulative length
        total_length = 0
        
        # Calculate border length 
        if border.geom_type == 'MultiLineString':
            for line in border.geoms:
                coords = list(line.coords)
                for k in range(len(coords)-1):
                    _, _, dist = geod.inv(coords[k][0], coords[k][1], coords[k+1][0], coords[k+1][1])
                    total_length += dist
        else:
            coords = list(border.coords)
            for k in range(len(coords)-1):
                 _, _, dist = geod.inv(coords[k][0], coords[k][1], coords[k+1][0], coords[k+1][1])
                 total_length += dist
                          
        # Update shortest border
        if total_length > 0 and total_length < shortest_length:
            shortest_length = total_length
            shortest_border = {
              'country_pair': f"{country_a['NAME']} ({country_a['ISO_A3']}) - {country_b['NAME']} ({country_b['ISO_A3']})",
              'geometry': border,
              'country_a_x': i,
              'country_b_x': j,}

# Print results
print(f"Country Pair: {shortest_border['country_pair']}")
print(f"Length: {shortest_length:.0f} m")


# 4.Drawing the map

# create map axis object
fig, ax = subplots(1, 1, figsize=(16, 10))

# remove axes
ax.axis('off')

# set title
title(f"Shortest International Border: {shortest_border['country_pair']}\nLength: {shortest_length:.0f} m",fontsize=16, pad=20)

# Define lambert conic
lambert_conic = "+proj=lcc +lat_1=30 +lat_2=60 +lon_0=15 +datum=WGS84 +units=m +no_defs"

# Transfor shortest_border
border_series = g.GeoSeries([shortest_border['geometry']], crs=world.crs).to_crs(lambert_conic)

# Transfor countries' geometry
country_a_y = g.GeoSeries(
    [world.loc[shortest_border['country_a_x']]['geometry']], 
    crs=world.crs).to_crs(lambert_conic)
country_b_y = g.GeoSeries(
    [world.loc[shortest_border['country_b_x']]['geometry']], 
    crs=world.crs).to_crs(lambert_conic)

# extract the bounds from the GeoSeries Object
minx, miny, maxx, maxy = border_series.geometry.iloc[0].bounds

# set bounds
buffer = shortest_length / 10
ax.set_xlim([minx - buffer, maxx + buffer])
ax.set_ylim([miny - buffer, maxy + buffer])

# plot data
country_a_y.plot(ax = ax, color = '#ccebc5', edgecolor = '#4daf4a', linewidth = 0.5,)
country_b_y.plot(ax = ax, color = '#fed9a6', edgecolor = '#ff7f00', linewidth = 0.5,)
border_series.plot(ax = ax, color = '#984ea3', linewidth = 3,)

# Add scale bar
ax.add_artist(ScaleBar(dx=1, units="m", location="lower left", length_fraction=0.3))

# Add legend
legend_elements = [
    Patch(
        facecolor='#ccebc5', edgecolor='#4daf4a', 
        label=world.loc[shortest_border['country_a_x']]['NAME']),  
    Patch(
        facecolor='#fed9a6', edgecolor='#ff7f00', 
        label=world.loc[shortest_border['country_b_x']]['NAME']),  
    Patch(
        facecolor='#984ea3', 
        label=f'Shortest Border ({shortest_length:.0f} m)')]
ax.legend(handles=legend_elements, loc='lower right', fontsize=12)

# Add north arrow
x, y, arrow_length = 0.95, 0.95, 0.05
ax.annotate('N', xy=(x, y), xytext=(x, y - arrow_length),
    arrowprops=dict(facecolor='black', width=3, headwidth=10),
    ha='center', va='center', fontsize=12, xycoords=ax.transAxes)

# save the image
savefig('./out/assessment1.png')

# --- NO CODE BELOW HERE ---

# report runtime
print(f"completed in: {perf_counter() - start_time} seconds")
