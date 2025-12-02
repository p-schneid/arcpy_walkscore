"""
Script documentation

- Assign walkscore values to point feature layer

"""
import arcpy
from typing import Any, Literal
from utils import get_feature_spatial_reference, get_file_name_and_path
from walkscore_adapter import get_walkscore

arcpy.env.overwriteOutput = True

wgs_spatial_reference = arcpy.SpatialReference("WGS 1984") 

GeometryType = Literal['POINT', 'MULTIPOINT', 'POLYGON', 'POLYLINE', 'MULTIPATCH']
DEFAULT_WALKSCORE_COLUMN = 'walkscore'

def create_shapefile ( target_file: str, geometry: GeometryType, spatial_reference: Any ): 

    # Create new feature class
    out_name, out_path = get_file_name_and_path(target_file)
    
    arcpy.CreateFeatureclass_management(out_path, out_name, 'POINT', spatial_reference=spatial_reference)
    
    

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


if __name__ == "__main__":

    #api_key = arcpy.GetParameterAsText(0)
    point_feature = arcpy.GetParameterAsText(0)
    output_point_feature = arcpy.GetParameterAsText(1)
    walkscore_column = arcpy.GetParameterAsText(2)

    arcpy.AddMessage('point feature: ' + point_feature)
    arcpy.AddMessage('output point feature: ' + output_point_feature)
    arcpy.AddMessage('walkscore column: ' + walkscore_column)
    arcpy.AddMessage('Workspace: ' + arcpy.env.workspace)  

    target_point_feature = point_feature
    target_column = walkscore_column or DEFAULT_WALKSCORE_COLUMN

    if output_point_feature:
        arcpy.CopyFeatures_management(point_feature, output_point_feature)
        target_point_feature = output_point_feature

    assign_walkscore_to_points(target_point_feature, target_column)
    
    

   
    