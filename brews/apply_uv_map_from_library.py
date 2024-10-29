"""Sample file showing how to apply a UV map from a DSF file to a geometry asset.

This code assumes we have already loaded a mesh from a DSF file using the
"create_geometry_from_library.py" sample file.
"""

# Import packages
import bpy
import dufman

# Import datatypes
from bpy.types import Float2Attribute, IntAttribute, Mesh
from dufman.structs.uv_set import DsonUVSet
from mathutils import Vector

# Replace these.
# - content_directory should match the user's Daz Studio set-up.
# - uv_set_url should point to a DSF (not DUF) file containing 
#     a UV set.
# - daz_geometry should be the name of an already-imported
#     Daz Studio asset. This example assumes we are reusing the
#     Genesis 8 Female mesh from "create_geometry_from_library.py".
DIRECTORY:str = "C:/Users/Public/Documents/Daz3D"
FILEPATH:str = "/data/DAZ 3D/Genesis 8/Female/UV Sets/DAZ 3D/Base/Base Female.dsf#Base Female"
MESH_NAME:str = "geometry"

# Add user's content directory.
dufman.file.add_content_directory(DIRECTORY)

# This should be a previously-loaded Daz Studio geometry asset.
# For this example, we will use the Genesis 8 Female mesh.
mesh:Mesh = bpy.data.meshes[MESH_NAME]

# Extract UV map data from DSF file.
struct:DsonUVSet = dufman.create.uv_set.create_uv_set_struct(FILEPATH)

if not struct.expected_vertices == len(mesh.vertices):
    raise Exception("Could not apply UV map. Mismatched vertex count.")

# Create mesh attribute to store UV map data.
uv_map:Float2Attribute = mesh.attributes.new(struct.library_id, 'FLOAT2', 'CORNER')

# In "create_geometry_from_library.py", we cached the original
#   face indices. Now we extract them, in case the geometry is bad.
face_indices:IntAttribute = mesh.attributes["dson_face_indices"]

# Loop through all faces and add UV coordinates to face corners.
for (index, polygon) in enumerate(mesh.polygons):
    
    # Use original DSON index, in case geometry is bad.
    original_index:int = face_indices.data[index].value
    
    # DSON has a bizarre method of handling UVs, which involves
    #   swapping vertex indices so they can be used to index into 
    #   the UV coordinates array. This helper function handles
    #   all of that for us.
    vertex_indices:list[int] = struct.hotswap_polygon(original_index, polygon.vertices)
    
    # Loop through the face's corners and apply the UV 
    #   coordinates from from the UV set struct.
    for (iteration, uv_index) in enumerate(vertex_indices):
        loop_index:int = polygon.loop_start + iteration
        uv_map.data[loop_index].vector = Vector(struct.uv_coordinates[uv_index])
