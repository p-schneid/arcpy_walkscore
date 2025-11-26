"""
Script documentation

- Assign walkscore values to point feature layer

"""
import arcpy
from typing import Any, Literal
from walkscore_adapter import get_walkscore

arcpy.env.overwriteOutput = True

wgs_spatial_reference = arcpy.SpatialReference("WGS 1984") 

def get_feature_spatial_reference (feature_layer: str) : 
    point_layer_desc = arcpy.Describe(feature_layer)
    spatial_ref = point_layer_desc.spatialReference
    return spatial_ref


GeometryType = Literal['POINT', 'MULTIPOINT', 'POLYGON', 'POLYLINE', 'MULTIPATCH']

def create_shapefile ( target_file: str, geometry: GeometryType, spatial_reference: Any ): 

    # Create new feature class
    file_path_elements = target_file.split('\\')
    out_name = file_path_elements.pop(-1)
    out_path = '/'.join(file_path_elements)
    
    arcpy.CreateFeatureclass_management(out_path, out_name, 'POINT', spatial_reference=spatial_reference)
    
    


if __name__ == "__main__":

    point_layer = arcpy.GetParameterAsText(0)
    output_point_layer = arcpy.GetParameterAsText(1)

    projected_point_layer = "projected_points.shp"

    arcpy.AddMessage('point layer: ' + point_layer)
    arcpy.AddMessage('output point layer: ' + output_point_layer)
    arcpy.AddMessage('Workspace: ' + arcpy.env.workspace)  

    point_spatial_ref = get_feature_spatial_reference(point_layer)

    arcpy.CopyFeatures_management(point_layer, output_point_layer)

    # Add walkscore field
    arcpy.AddField_management(output_point_layer, 'walkscore', "FLOAT")

    with arcpy.da.UpdateCursor(output_point_layer, ['SHAPE@XY', 'walkscore']) as update_cursor:
        for row in update_cursor:
            x, y = row[0]

            point = arcpy.Point(x, y)
            point_geometry = arcpy.PointGeometry(point, point_spatial_ref)
            projected_point = point_geometry.projectAs(wgs_spatial_reference)
            lon = projected_point.firstPoint.X
            lat = projected_point.firstPoint.Y

            walkscore = get_walkscore(lat, lon, '40b48aa9dd8220062069e30f5233481b')
            row[1] = walkscore
            update_cursor.updateRow(row)