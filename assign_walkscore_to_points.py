"""
Script documentation

- Assign walkscore values to point feature layer

"""
import re
import arcpy
from typing import Any, Literal
from walkscore_adapter import get_walkscore

arcpy.env.overwriteOutput = True

wgs_spatial_reference = arcpy.SpatialReference("WGS 1984") 
GeometryType = Literal['POINT', 'MULTIPOINT', 'POLYGON', 'POLYLINE', 'MULTIPATCH']
DEFAULT_WALKSCORE_COLUMN = 'WALK'

# Given a full file path, split into path and file name
# Many arcpy functions use both params, rather than a singular file path

def get_file_name_and_path (target_file: str, no_extension = False):
    file_path_elements = re.split(r'[//\\]', target_file)
    out_name = file_path_elements.pop(-1)
    out_path = '/'.join(file_path_elements) 

    if no_extension: 
        out_name = out_name.split('.')[0]

    return [out_name, out_path]

def get_feature_spatial_reference (feature_layer: str) : 
    point_layer_desc = arcpy.Describe(feature_layer)
    spatial_ref = point_layer_desc.spatialReference
    return spatial_ref


def assign_walkscore_to_points (point_feature: str, walkscore_column: str = DEFAULT_WALKSCORE_COLUMN) : 

    # Add walkscore field
    arcpy.AddField_management(point_feature, walkscore_column, "FLOAT")

    spatial_ref = get_feature_spatial_reference(point_feature)

    with arcpy.da.UpdateCursor(point_feature, ['SHAPE@XY', walkscore_column]) as update_cursor:
        for row in update_cursor:
            x, y = row[0]

            point = arcpy.Point(x, y)
            point_geometry = arcpy.PointGeometry(point, spatial_ref)

            # walkscore api requires coordinates in lat, lon
            projected_point = point_geometry.projectAs(wgs_spatial_reference)
            lon = projected_point.firstPoint.X
            lat = projected_point.firstPoint.Y

            walkscore = get_walkscore(lat, lon, '40b48aa9dd8220062069e30f5233481b')
            row[1] = walkscore
            update_cursor.updateRow(row)


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
        file_name, path = get_file_name_and_path(output_feature)
        return file_name
    else:
        return input_feature
        
    
#################################################################

if __name__ == "__main__":

    #api_key = arcpy.GetParameterAsText(0)
    input_point_geometry = arcpy.GetParameterAsText(0)
    output_point_feature = arcpy.GetParameterAsText(1)
    walkscore_column = arcpy.GetParameterAsText(2)

    arcpy.AddMessage('input point geometry: ' + input_point_geometry)
    arcpy.AddMessage('output point feature: ' + output_point_feature)
    arcpy.AddMessage('walkscore column: ' + walkscore_column)
    arcpy.AddMessage('Workspace: ' + arcpy.env.workspace)  

    input_point_feature = get_input_geometry_feature(input_point_geometry)

    target_point_feature = get_target_feature(input_point_feature, output_point_feature)

    target_column = walkscore_column or DEFAULT_WALKSCORE_COLUMN

    assign_walkscore_to_points(target_point_feature, target_column)
    
    

   
    