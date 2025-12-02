import arcpy

def get_file_name_and_path (target_file: str) -> list[str]:
    file_path_elements = target_file.split('//')
    out_name = file_path_elements.pop(-1)
    out_path = '/'.join(file_path_elements) 

    return [out_name, out_path]

def get_feature_spatial_reference (feature_layer: str) : 
    point_layer_desc = arcpy.Describe(feature_layer)
    spatial_ref = point_layer_desc.spatialReference
    return spatial_ref

if __name__ == "__main__":

    get_file_name_and_path('testing')