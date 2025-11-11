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

# 1.Data loading and preprocessing

# Set ellipsoid
geod = Geod(ellps='WGS84')

# Load country boundary data
world = g.read_file("./data/natural-earth/ne_10m_admin_0_countries.shp")


# 2.Spatial index construction

# Build STRtree spatial index
spatial_index = g.GeoSeries(world['geometry']).sindex

# Store border results
border_results = []


# 3.Border calculation and length measurement

# loop through a list (i < j)
for i in range(len(world)):
    
    # Get current country information
    country_a = world.loc[i]
    geom_a = world.geometry.loc[i]
    iso_a = world.ISO_A3.loc[i]
    name_a = world.NAME.loc[i]
    
    # Check candidate countries that may intersect with current country
    candidate_indices = list(spatial_index.query(geom_a, predicate='intersects'))
    
    # Filter candidate countries with index bigger than i
    candidate_indices = [j for j in candidate_indices if j > i]
    
    # Loop all candidate countries and calculate intersection
    for j in candidate_indices:
        
        # Get current country information
        country_b = world.loc[j]
        geom_b = world.geometry.loc[j]
        iso_b = world.ISO_A3.loc[j]
        name_b = world.NAME.loc[j]
        
        # Calculate intersection of the two countries' boundaries
        border_geom = geom_a.intersection(geom_b)
        
        # Filter invalid borders
        if border_geom.geom_type not in ['LineString', 'MultiLineString']:
            continue
        
        # Store multi-segment results
        border_segments = []
        
        # Handle multi-segment cases
        if border_geom.geom_type == 'MultiLineString':
            border_segments = list(border_geom.geoms)
        else:
            border_segments = [border_geom]
        
        # Calculate ellipsoidal distance
        total_length = 0
        
        # Calculate total length by iterating over all segments
        for segment in border_segments:
            
            # Ensure coordinates of a single LineString
            coords = list(segment.coords)  
            
            # Accumulate length of each sub-segment
            for k in range(len(coords) - 1):
                lon1, lat1 = coords[k]
                lon2, lat2 = coords[k + 1]
                
                # Calculate ellipsoidal distance between two points
                _, _, dist = geod.inv(lon1, lat1, lon2, lat2)
                total_length += dist
                
        # Store results
        border_results.append({
            'country_pair': f"{name_a} ({iso_a}) - {name_b} ({iso_b})",
            'length_m': total_length,
            'geometry': border_geom,
            'country_a_x': i,
            'country_b_x': j,})
        
        
# 4. Filter the shortest border

# Sort and take the shortest one
shortest_border = sorted(border_results, key=lambda x: x['length_m'])[0]

# From shortest_border get key points for drawing map
length_m = shortest_border['length_m'] 

# Print results
print(f"Country Pair: {shortest_border['country_pair']}")
print(f"Length: {shortest_border['length_m']:.0f} m")


# 5.Drawing the map

# create map axis object
my_fig, my_ax = subplots(1, 1, figsize=(16, 10))

# remove axes
my_ax.axis('off')

# set title
title(f"Shortest International Border: {shortest_border['country_pair']}\nLength: {shortest_border['length_m']:.0f} m",fontsize=16, pad=20)

# Define lambert conic
lambert_conic = "+proj=lcc +lat_1=30 +lat_2=60 +lon_0=15 +datum=WGS84 +units=m +no_defs"

# Transfor shortest_border
border_series = g.GeoSeries(
    [shortest_border['geometry']], 
    crs=world.crs).to_crs(lambert_conic)

# Transfor countries' geometry
country_a_y = g.GeoSeries(
    [world.loc[shortest_border['country_a_x']]['geometry']], 
    crs=world.crs).to_crs(lambert_conic)
country_b_y = g.GeoSeries(
    [world.loc[shortest_border['country_b_x']]['geometry']], 
    crs=world.crs).to_crs(lambert_conic)

# extract the bounds from the (projected) GeoSeries Object
minx, miny, maxx, maxy = border_series.geometry.iloc[0].bounds

# set bounds 
buffer = length_m / 10
my_ax.set_xlim([minx - buffer, maxx + buffer])
my_ax.set_ylim([miny - buffer, maxy + buffer])

# plot data
country_a_y.plot(
    ax = my_ax,
    color = '#ccebc5',
    edgecolor = '#4daf4a',
    linewidth = 0.5,)

country_b_y.plot(
    ax = my_ax,
    color = '#fed9a6',
    edgecolor = '#ff7f00',
    linewidth = 0.5,)

border_series.plot(     
    ax = my_ax,
    color = '#984ea3',
    linewidth = 3,)

# Add scale bar
my_ax.add_artist(
    ScaleBar(
        dx=1, 
        units="m", 
        location="lower left", 
        length_fraction=0.3))

# Add legend
legend_elements = [
    Patch(
        facecolor='#ccebc5', 
        edgecolor='#4daf4a', 
        label=world.loc[shortest_border['country_a_x']]['NAME']),  
    Patch(
        facecolor='#fed9a6', 
        edgecolor='#ff7f00', 
        label=world.loc[shortest_border['country_b_x']]['NAME']),  
    Patch(
        facecolor='#984ea3', 
        label=f'Shortest Border ({length_m:.0f} m)')]
my_ax.legend(handles=legend_elements, loc='lower right', fontsize=12)

# Add north arrow
x, y, arrow_length = 0.95, 0.95, 0.05
my_ax.annotate(
    'N',
    xy=(x, y),
    xytext=(x, y - arrow_length),
    arrowprops=dict(facecolor='black', width=3, headwidth=10),
    ha='center', va='center', fontsize=12, xycoords=my_ax.transAxes)

# save the image
savefig('./out/assessment1.png')

# --- NO CODE BELOW HERE ---

# report runtime
print(f"completed in: {perf_counter() - start_time} seconds")
