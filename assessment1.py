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
import geopandas as g
from pyproj import Geod




# 1.Data loading and preprocessing

# Initialize Geod pbject with WGS84 ellipsoid
geod = Geod(ellps='WGS84')

# Load country boundary data
world = g.read_file("./data/natural-earth/ne_10m_admin_0_countries.shp")

# Print basic data information
print(f"Number of valid countries:{len(world)}")


# 2.Spatial index construction

# Extract country geometries and build STRtree spatial index
geometries = world['geometry'].tolist()
spatial_index = g.GeoSeries(geometries).sindex

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
        
        # Handle multi-segment cases
        border_segments = []
        if border_geom.geom_type == 'MultiLineString':
            border_segments = list(border_geom.geoms)
        else:
            border_segments = [border_geom]
        
        # Calculate ellipsoidal distance
        total_length = 0.0
        
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
            'geometry': border_geom})



# --- NO CODE BELOW HERE ---

# report runtime
print(f"completed in: {perf_counter() - start_time} seconds")