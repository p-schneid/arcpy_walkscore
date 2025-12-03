
import arcpy

from typing import Any, Literal
from walkscore_adapter import get_walkscore

wgs_spatial_reference = arcpy.SpatialReference("WGS 1984") 

GeometryType = Literal['POINT', 'MULTIPOINT', 'POLYGON', 'POLYLINE', 'MULTIPATCH']
DEFAULT_WALKSCORE_COLUMN = 'walkscore'


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


def create_points_inside_feature(input_feature: str, point_feature: str) :

    grid_feature, sample_point_feature = create_sample_grid(input_feature, 6, 6)

    arcpy.analysis.Clip(sample_point_feature, input_feature, point_feature)

    return point_feature


def create_sample_grid (feature_extent: str, rows: int, cols: int, grid_feature: str = "temp_grid" ) :
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

    # Create a point label feature class 
    labels = 'LABELS'

    # Each output cell will be a polygon
    geometry_type = 'POLYGON'


    arcpy.management.CreateFishnet(
        output_feature, 
        origin, 
        y_axis_reference_coordinate,
        cell_width, 
        cell_height, 
        rows, 
        cols, 
        opposite_corner, 
        labels, 
        '#', 
        geometry_type
    )

    point_feature = grid_feature + '_label'
    
    return [grid_feature, point_feature]



def get_file_name_and_path (target_file: str) -> list[str]:
    file_path_elements = target_file.split('//')
    out_name = file_path_elements.pop(-1)
    out_path = '/'.join(file_path_elements) 

    return [out_name, out_path]

def get_feature_spatial_reference (feature_layer: str) : 
    point_layer_desc = arcpy.Describe(feature_layer)
    spatial_ref = point_layer_desc.spatialReference
    return spatial_ref

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


if __name__ == "__main__":

    get_file_name_and_path('testing')