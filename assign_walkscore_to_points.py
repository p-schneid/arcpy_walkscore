"""
Script documentation

- Assign walkscore values to point feature

"""
import re
import arcpy
from typing import Any, Literal
from utils import get_feature_spatial_reference, get_input_geometry_feature, get_target_feature
from walkscore_adapter import get_walkscore

arcpy.env.overwriteOutput = True

wgs_spatial_reference = arcpy.SpatialReference("WGS 1984") 
GeometryType = Literal['POINT', 'MULTIPOINT', 'POLYGON', 'POLYLINE', 'MULTIPATCH']
DEFAULT_WALKSCORE_COLUMN = 'WALK'


def assign_walkscore_to_points (api_key: str, point_feature: str, walkscore_column: str = DEFAULT_WALKSCORE_COLUMN) : 

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

            walkscore = get_walkscore(lat, lon, api_key)
            row[1] = walkscore
            update_cursor.updateRow(row)
            

if __name__ == "__main__":

    #api_key = arcpy.GetParameterAsText(0)
    api_key = arcpy.GetParameterAsText(0)
    input_point_geometry = arcpy.GetParameterAsText(1)
    output_point_feature = arcpy.GetParameterAsText(2)
    walkscore_column = arcpy.GetParameterAsText(3)

    arcpy.AddMessage('api key: ' + api_key)
    arcpy.AddMessage('input point geometry: ' + input_point_geometry)
    arcpy.AddMessage('output point feature: ' + output_point_feature)
    arcpy.AddMessage('walkscore column: ' + walkscore_column)
    arcpy.AddMessage('Workspace: ' + arcpy.env.workspace)  

    input_point_feature = get_input_geometry_feature(input_point_geometry)

    target_point_feature = get_target_feature(input_point_feature, output_point_feature)

    target_column = walkscore_column or DEFAULT_WALKSCORE_COLUMN

    assign_walkscore_to_points(api_key, target_point_feature,  target_column)
    
    

   
    