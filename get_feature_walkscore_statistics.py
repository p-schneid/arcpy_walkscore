"""
Script documentation

- Tool parameters are accessed using arcpy.GetParameter() or 
                                     arcpy.GetParameterAsText()
- Update derived parameter values using arcpy.SetParameter() or
                                        arcpy.SetParameterAsText()
"""

import arcpy

from assign_walkscore_to_points import assign_walkscore_to_points

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

    #api_key = arcpy.GetParameterAsText(0)
    input_feature = arcpy.GetParameterAsText(0)
    sample_points = arcpy.GetParameterAsText(1) 

    arcpy.AddMessage('input feature: ' + input_feature)
    arcpy.AddMessage('num points: ' + sample_points)

    point_feature = arcpy.env.workspace + '\\' + 'temp_random_points' 

    points = create_points_inside_feature(input_feature, point_feature)

    assign_walkscore_to_points(point_feature)




    


