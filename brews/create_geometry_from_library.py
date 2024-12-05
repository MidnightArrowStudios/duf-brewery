"""Sample file showing how to load a geometry asset from a DSF file.

Prerequisites:
    -None
"""

# ============================================================================ #
# IMPORT                                                                       #
# ============================================================================ #

# bpy
import bpy
from bpy.types import Context, Mesh, Object

# bmesh
import bmesh
from bmesh.types import BMesh, BMFace, BMVert

# mathutils
from mathutils import Vector

# dufman
from dufman import file
from dufman.structs import DsonGeometry


# ============================================================================ #
# FUNCTION                                                                     #
# ============================================================================ #

def create_geometry(context:Context, struct:DsonGeometry) -> Mesh:
    """Create a mesh using the data inside a DsonGeometry struct."""
    
    # Create mesh in blend file
    mesh:Mesh = context.blend_data.meshes.new(struct.library_id)
    
    # Setup BMesh
    bm:BMesh = bmesh.new()
    bm.from_mesh(mesh)
    
    # Add vertices from struct
    for (index, vertex) in enumerate(struct.vertices):
        vector:Vector = Vector(vertex)
        bm.verts.new(vector)
    
    # Ensure geometry is valid
    bm.verts.ensure_lookup_table()
    
    # Create attributes
    # "attr_original" caches the original face index, in case geometry is
    #   invalid or deleted
    # "attr_material" caches the original material index, so material slots
    #   can be reshuffled or deleted
    attr_original:BMLayerItem = bm.faces.layers.int.new("daz_original_index")
    attr_material:BMLayerItem = bm.faces.layers.int.new("daz_material_index")
    
    # Add faces from struct
    for (index, polygon) in enumerate(struct.polygons):
        
        # Invalid faces will return None, so they should be skipped
        indices:list[int] = list(polygon)
        if not indices:
            continue
        
        # Create the geometry with BMesh.
        vertices:list[BMVert] = [ bm.verts[index] for index in indices ]
        face:BMFace = bm.faces.new(vertices)
        
        # These need to be assigned inside the DsonGeometry loop, or else
        #   they will go out of alignment if invalid geometry is skipped
        face[attr_original] = index
        face[attr_material] = struct.material_indices[index]
    
    # Cleanup BMesh
    bm.to_mesh(mesh)
    bm.free()
    
    # A more robust implementation will probably want to cache the 
    #   material names inside a PropertyGroup assigned to the mesh
    
    return mesh


# ============================================================================ #
# SCRIPT                                                                       #
# ============================================================================ #

# Change this to match Daz Studio install directory
CONTENT_DIRECTORY:str = "F:/Daz3D"
GEOMETRY_URL:str = "/data/DAZ 3D/Genesis 8/Female/Genesis8Female.dsf#geometry"

# ============================================================================ #

# Setup
file.add_content_directory(CONTENT_DIRECTORY)

# Construct intermediate representation using DUFMan
struct:DsonGeometry = DsonGeometry.load(GEOMETRY_URL)

# Create mesh object
mesh:Mesh = create_geometry(bpy.context, struct)

# Add object to scene
obj:Object = bpy.data.objects.new(struct.library_id, mesh)
bpy.context.view_layer.layer_collection.collection.objects.link(obj)

# Cleanup
file.remove_content_directory(CONTENT_DIRECTORY)
