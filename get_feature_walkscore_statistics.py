"""
Script documentation

"""

from typing import Any
import arcpy

from assign_walkscore_to_points import assign_walkscore_to_points, DEFAULT_WALKSCORE_COLUMN, get_file_name_and_path

def create_sample_points_inside_feature(input_feature: str, point_feature: str) :

    grid_feature, sample_point_feature = create_sample_grid(input_feature, 6, 6)

    # Only clip to the first feature in data set
    first_feature = get_first_feature(input_feature)

    arcpy.AddMessage('sample_point_feature: ' + sample_point_feature)
    arcpy.AddMessage('point_feature: ' + point_feature)
    arcpy.analysis.Clip(sample_point_feature, first_feature, point_feature)

    return point_feature
    


def create_sample_grid (feature_extent: str, rows: int, cols: int, grid_feature: str = "sample" ) :
    output_feature = arcpy.env.workspace + "\\" + grid_feature

    arcpy.env.outputCoordinateSystem = arcpy.SpatialReference("WGS 1984") 

    # Set the origin of the fishnet,
    origin_lon, origin_lat = get_feature_origin(feature_extent)
    origin = f"{origin_lon} {origin_lat}"

    arcpy.AddMessage('origin: ' + origin)

    # Set the orientation
    y_axis_reference_coordinate = f"{origin_lon} {origin_lat + 0.0001}" # May not work for UTM projection
    # y_axis_reference_coordinate = '1037.26 4155.81'

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

    point_feature = grid_feature + '_label' # Dont' alter!
    
    return [grid_feature, point_feature]


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
#################################################################


if __name__ == "__main__":

    #api_key = arcpy.GetParameterAsText(0)
    input_geometry = arcpy.GetParameterAsText(0)

    arcpy.AddMessage('input geometry: ' + input_geometry)

    input_feature = input_geometry

    if ' ' in input_feature:
       # this is the layer name. Lookup the feature name
       input_feature = get_layer_feature_name(input_geometry)

    point_feature = arcpy.env.workspace + '\\' + input_feature + '_samples' 
    stats_table = arcpy.env.workspace + '\\' + input_feature + '_stats' 

    create_sample_points_inside_feature(input_feature, point_feature)

    assign_walkscore_to_points(point_feature)

    arcpy.analysis.Statistics(point_feature, stats_table, [
        [DEFAULT_WALKSCORE_COLUMN, "MIN"],
        [DEFAULT_WALKSCORE_COLUMN, "MAX"],
        [DEFAULT_WALKSCORE_COLUMN, "MEAN"],
        [DEFAULT_WALKSCORE_COLUMN, "MEDIAN"],
        [DEFAULT_WALKSCORE_COLUMN, "STD"],
        [DEFAULT_WALKSCORE_COLUMN, "VARIANCE"]
    ])

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




    


