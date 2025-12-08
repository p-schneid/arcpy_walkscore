
import re
from typing import Any
import arcpy

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


def get_active_map () :
    project = arcpy.mp.ArcGISProject("CURRENT")
    project.listMaps()  
    map = project.activeMap
    return map

def get_layer_from_active_map(layer_name: str):
    map = get_active_map()
    layer = map.listLayers(layer_name)[0]
    return layer

def get_layer_source(layer: Any):
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

# Resolve the input feature. If input contains a space, it is a feature layer
def get_input_geometry_feature ( input_geometry ) :

    if ' ' in input_geometry:
       # this is the layer name. Lookup the feature name
       return get_layer_feature_name(input_geometry)
    else:
        return input_geometry

# Resolve the target. If no output, use the input feature.
def get_target_feature (input_feature, output_feature) : 
    if output_feature:
        arcpy.CopyFeatures_management(input_feature, output_feature)
        file_name, path = get_file_name_and_path(output_feature, no_extension=True)
        return file_name
    else:
        return input_feature
    

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
    
