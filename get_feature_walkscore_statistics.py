"""
Script documentation

- Tool parameters are accessed using arcpy.GetParameter() or 
                                     arcpy.GetParameterAsText()
- Update derived parameter values using arcpy.SetParameter() or
                                        arcpy.SetParameterAsText()
"""

import arcpy

from .utils import create_points_inside_feature, assign_walkscore_to_points


if __name__ == "__main__":

    #api_key = arcpy.GetParameterAsText(0)
    input_feature = arcpy.GetParameterAsText(0)
    sample_points = arcpy.GetParameterAsText(1) 

    arcpy.AddMessage('input feature: ' + input_feature)
    arcpy.AddMessage('num points: ' + sample_points)

    point_feature = arcpy.env.workspace + '\\' + 'temp_random_points' 

    points = create_points_inside_feature(input_feature, point_feature)

    assign_walkscore_to_points(point_feature)

    




    


