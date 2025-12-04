"""
Script documentation

"""

from typing import Any
import arcpy
import numpy as np 

from assign_walkscore_to_points import assign_walkscore_to_points, get_file_name_and_path

WALKSCORE_COLUMN = 'WALK'
SAMPLE_POSTFIX = '_samples'


def create_sample_points_inside_feature(constraining_feature: str, sample_point_feature: str) :

    grid_feature, grid_point_feature = create_sample_grid(constraining_feature, 6, 6)

    # Only clip to the first feature in data set
    first_feature = get_first_feature(constraining_feature)

    arcpy.AddMessage('grid_point_feature: ' + grid_point_feature)
    arcpy.AddMessage('point_feature: ' + sample_point_feature)
    arcpy.analysis.Clip(grid_point_feature, first_feature, sample_point_feature)

    return sample_point_feature
    


def create_sample_grid (feature_extent: str, rows: int, cols: int, grid_feature: str = "sample" ) :
    output_feature = arcpy.env.workspace + "\\" + grid_feature

    arcpy.env.outputCoordinateSystem = arcpy.SpatialReference("WGS 1984") 

    # Set the origin of the fishnet,
    origin_lon, origin_lat = get_feature_origin(feature_extent)
    origin = f"{origin_lon} {origin_lat}"

    arcpy.AddMessage('origin: ' + origin)

    # Set a y axis reference point to set the grid's orientation
    y_axis_reference_coordinate = f"{origin_lon} {origin_lat + 0.1}" # May not work for UTM projection?

    cell_width = ''    
    cell_height = ''

    opposite_lon, opposite_lat = get_feature_opposite(feature_extent)
    opposite_corner = f"{opposite_lon} {opposite_lat}"

    arcpy.management.CreateFishnet(
        output_feature, 
        origin, 
        y_axis_reference_coordinate,
        cell_width, 
        cell_height, 
        rows, 
        cols, 
        opposite_corner, 
        labels='LABELS', 
        geometry_type='POLYGON'
    )

    # Dont' alter! The create fishnet tool writes the intersection points to this file name. 
    point_feature = grid_feature + '_label' 
    
    return [grid_feature, point_feature]


def assign_walkscore_stats_to_polygon (sample_point_feature: str, output_polygon_feature: str): 

    stats = ["MIN", "MAX", "MEAN", "MED", "STD"]
    stat_columns = list(map( lambda stat: stat + "_" + WALKSCORE_COLUMN, stats ))

    sample_data = arcpy.da.FeatureClassToNumPyArray(sample_point_feature, (WALKSCORE_COLUMN))
    walkscores = sample_data[WALKSCORE_COLUMN]

    # create columns in target feature

    for column in stat_columns:
        arcpy.AddMessage('column: ' + column)
        arcpy.AddField_management(output_polygon_feature, column, "FLOAT")

    with arcpy.da.UpdateCursor(output_polygon_feature, stat_columns) as update_cursor:
        for row in update_cursor:
            # Use numpy to calculate statistics from point collection
            row[0] = np.min(walkscores)
            row[1] = np.max(walkscores)
            row[2] = np.mean(walkscores)
            row[3] = np.median(walkscores)
            row[4] = np.std(walkscores)

            update_cursor.updateRow(row)

def get_feature_extent(feature):  
    desc = arcpy.Describe(feature)

    xmin = str(desc.extent.XMin)
    xmax = str(desc.extent.XMax)
    ymin = str(desc.extent.YMin)
    ymax = str(desc.extent.YMax)

    extent = xmin + " " + ymin + " " + xmax + " " + ymax
    return extent

def get_feature_origin(feature):  
    desc = arcpy.Describe(feature)

    xmin = desc.extent.XMin
    ymin = desc.extent.YMin
    
    return [xmin, ymin]

def get_feature_opposite(feature):  
    desc = arcpy.Describe(feature)

    xmax = desc.extent.XMax
    ymax = desc.extent.YMax
    
    return [xmax, ymax]
    

def get_first_feature(input_feature: str) : 
    
    first_feature_geometry = None

    with arcpy.da.SearchCursor(input_feature, ["SHAPE@"], None, None) as cursor:
        first_row = next(cursor)
        first_feature_geometry = first_row[0]

    return first_feature_geometry
    

## I had to duplicate this logic because of a quixiotic import error 
## I believe the interpreter thinks there is a circular dependency, even when there isn't
#########################################################################
def get_active_map () :
    project = arcpy.mp.ArcGISProject("CURRENT")
    project.listMaps()  
    map = project.activeMap
    return map

def get_layer_from_active_map(layer_name: str):
    map = get_active_map()
    layer = map.listLayers(layer_name)[0]
    return layer

def get_layer_source(layer: Any ):
    if layer.supports("DATASOURCE"):
        source = layer.dataSource
        arcpy.AddMessage(f"New feature data source: {source}")
        return source
    else:
        raise Exception('Could not identify input layer source')
    
def get_layer_feature_name (layer_name: str) :
    layer = get_layer_from_active_map(layer_name)
    layer_file = get_layer_source(layer)
    name, path = get_file_name_and_path(layer_file)
    return name

def get_input_geometry_feature ( input_geometry ) :

    if ' ' in input_geometry:
       # this is the layer name. Lookup the feature name
       return get_layer_feature_name(input_geometry)
    else:
        return input_geometry
    
def get_target_feature (input_feature, output_feature) : 
    if output_feature:
        arcpy.CopyFeatures_management(input_feature, output_feature)
        file_name, path = get_file_name_and_path(output_feature, no_extension=True)
        return file_name
    else:
        return input_feature

#################################################################


if __name__ == "__main__":

    #api_key = arcpy.GetParameterAsText(0)
    input_polygon_geometry = arcpy.GetParameterAsText(0)
    output_polygon_feature = arcpy.GetParameterAsText(1)
    random_samples = arcpy.GetParameterAsText(2)

    arcpy.AddMessage('input_polygon_geometry: ' + input_polygon_geometry)
    arcpy.AddMessage('output_polygon_feature: ' + output_polygon_feature)
    arcpy.AddMessage('random_samples: ' + random_samples)

    create_random_samples = random_samples == 'true'

    input_polygon_feature = input_polygon_geometry

    input_polygon_feature = get_input_geometry_feature(input_polygon_geometry)

    sample_point_feature = arcpy.env.workspace + '\\' + input_polygon_feature + SAMPLE_POSTFIX 
    
    target_polygon_feature = input_polygon_feature

    #sample_point_feature = arcpy.env.workspace + '\\'  + 'midtown_samples' 

    if output_polygon_feature:
        arcpy.CopyFeatures_management(input_polygon_feature, output_polygon_feature)
        target_polygon_feature = output_polygon_feature
        base_name, path = get_file_name_and_path(output_polygon_feature, no_extension=True)
        sample_point_feature = path + '\\' + base_name + SAMPLE_POSTFIX


    arcpy.AddMessage('target_polygon_feature: ' + target_polygon_feature)
    arcpy.AddMessage('sample_point_feature: ' + sample_point_feature)



    if create_random_samples: 
        name, path = get_file_name_and_path(sample_point_feature)
        arcpy.management.CreateRandomPoints(path, name, target_polygon_feature, number_of_points_or_field=30)
    
    else:
        create_sample_points_inside_feature(target_polygon_feature, sample_point_feature)

    assign_walkscore_to_points(sample_point_feature, WALKSCORE_COLUMN)

    assign_walkscore_stats_to_polygon(sample_point_feature, target_polygon_feature)

    # arcpy.analysis.Statistics(sample_point_feature, stats_table, [
    #     [WALKSCORE_COLUMN, "MIN"],
    #     [WALKSCORE_COLUMN, "MAX"],
    #     [WALKSCORE_COLUMN, "MEAN"],
    #     [WALKSCORE_COLUMN, "MEDIAN"],
    #     [WALKSCORE_COLUMN, "STD"],
    #     [WALKSCORE_COLUMN, "VARIANCE"]
    # ])

    # Not idempotent. Would need to check and remove join if exists
    # arcpy.management.AddJoin(
    #     in_layer_or_view=input_feature,
    #     in_field="OBJECTID",
    #     join_table=stats_table,
    #     join_field="OBJECTID",
    #     join_type="KEEP_ALL",
    #     index_join_fields="NO_INDEX_JOIN_FIELDS",
    #     rebuild_index="NO_REBUILD_INDEX"
    # )




    


