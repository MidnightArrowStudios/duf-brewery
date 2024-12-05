"""Sample file showing how to apply a UVSet asset from a DSF file.

Prerequisites:
    -run "create_geometry_from_library.py"
"""

# ============================================================================ #
# IMPORT                                                                       #
# ============================================================================ #

# bpy
import bpy
from bpy.types import Float2Attribute, IntAttribute, Mesh

# mathutils
from mathutils import Vector

# dufman
from dufman import file
from dufman.structs import DsonUVSet

# ============================================================================ #
# FUNCTION                                                                     #
# ============================================================================ #

def apply_uv_map(mesh:Mesh, struct:DsonUVSet) -> Float2Attribute:
    """Apply a UV map using the data inside a UVSet struct."""
    
    # Ensure number of vertices match.
    if len(mesh.vertices) != struct.expected_vertices:
        raise Exception("Could not apply UV Map. Vertex count mismatch.")
    
    # The UV map we will insert data into.
    uv_map:Float2Attribute = mesh.attributes.new(struct.library_id, 'FLOAT2', 'CORNER')
    
    # These are the cached indices from the DSF file, which we use in case we
    #   had to skip invalid geometry.
    face_indices:IntAttribute = mesh.attributes["daz_original_index"]
    
    # Add UV coordinates from struct.
    for (index, polygon) in enumerate(mesh.polygons):
    
        # Get the original index, cached from the DSF file.
        original_index:int = face_indices.data[index].value
        
        # DSON has a bizarre way of storing vertex indices. This helper method
        #   handles the confusing part for us.
        vertex_indices:list[int] = struct.hotswap(original_index, polygon.vertices)
    
        for (iteration, uv_index) in enumerate(vertex_indices):
            loop_index:int = polygon.loop_start + iteration
            uv_map.data[loop_index].vector = Vector(struct.uv_coordinates[uv_index])
    
    return uv_map


# ============================================================================ #
# SCRIPT                                                                       #
# ============================================================================ #

# Change this to match Daz Studio install directory
CONTENT_DIRECTORY:str = "C:/Users/Public/Documents/Daz3D"
UV_SET_URL:str = "/data/DAZ 3D/Genesis 8/Female/UV Sets/DAZ 3D/Base/Base Female.dsf#Base Female"

# ============================================================================ #

# Setup
file.add_content_directory(CONTENT_DIRECTORY)

# The mesh we want to assign the UV map to. Should have been created by
#   running "create_geometry_from_library.py".
mesh:Mesh = bpy.data.meshes["geometry"]

# Construct intermediate representation using DUFMan.
struct:DsonUVSet = DsonUVSet.load(UV_SET_URL)

# Assign UV map to mesh.
apply_uv_map(mesh, struct)

# Cleanup
file.remove_content_directory(CONTENT_DIRECTORY)
