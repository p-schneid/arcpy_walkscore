"""
Script documentation

- Assign walkscore values to point feature layer

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
    from .utils import assign_walkscore_to_points
except ImportError:
    from arcpy_walkscore.utils import assign_walkscore_to_points

DEFAULT_WALKSCORE_COLUMN = 'walkscore'

arcpy.env.overwriteOutput = True

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
    
    

   
    