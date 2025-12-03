gi"""
Script documentation

- Tool parameters are accessed using arcpy.GetParameter() or 
                                     arcpy.GetParameterAsText()
- Update derived parameter values using arcpy.SetParameter() or
                                        arcpy.SetParameterAsText()
"""

import arcpy
import sys
import os

# Add parent directory to path when running as script (before imports)
_script_dir = os.path.dirname(os.path.abspath(__file__))
_parent_dir = os.path.dirname(_script_dir)
if _parent_dir not in sys.path:
    sys.path.insert(0, _parent_dir)

try:
    from .utils import create_points_inside_feature, assign_walkscore_to_points
except ImportError:
    from arcpy_walkscore.utils import create_points_inside_feature, assign_walkscore_to_points


if __name__ == "__main__":

    #api_key = arcpy.GetParameterAsText(0)
    input_feature = arcpy.GetParameterAsText(0)
    sample_points = arcpy.GetParameterAsText(1) 

    arcpy.AddMessage('input feature: ' + input_feature)
    arcpy.AddMessage('num points: ' + sample_points)

    point_feature = arcpy.env.workspace + '\\' + 'temp_random_points' 

    points = create_points_inside_feature(input_feature, point_feature)

    assign_walkscore_to_points(point_feature)

    




    


