"""Sample file showing how to load a geometry asset from a DSF file."""

# Import packages
import bpy
import bmesh
import mathutils
import dufman

# Import datatypes
from bpy.types import Mesh, Object
from bmesh.types import BMFace, BMLayerItem, BMesh, BMVert
from mathutils import Vector
from dufman.structs.geometry import DsonGeometry

# Replace these. FILEPATH should be a DSF (not a DUF) file. For this
#    example, we will use the Genesis8Female mesh.
DIRECTORY:str = "C:/Users/Public/Documents/Daz3D"
FILEPATH:str = "/data/DAZ 3D/Genesis 8/Female/Genesis8Female.dsf#geometry"

# Register user's content directory
dufman.file.add_content_directory(DIRECTORY)

# Create a wrapper object for DSON asset
struct:DsonGeometry = dufman.create.geometry.create_geometry_struct(FILEPATH)

# Create an empty mesh object
mesh:Mesh = bpy.data.meshes.new(struct.library_id)

# Fill the mesh object with data from DSON file
bm:BMesh = bmesh.new()
bm.from_mesh(mesh)

# Daz Studio is more lax when it comes to invalid faces than Blender,
#    which means some faces will need to be skipped. Other DSON assets (i.e.
#    morphs) may rely on the original indices, so cache them for future use 
#    during the creation process.
dson_vert:BMLayerItem = bm.verts.layers.int.new("dson_original_vertex_indices")
dson_face:BMLayerItem = bm.faces.layers.int.new("dson_original_face_indices")

# Cache the material indices from the DSF file. This is technically
#    redundant, since material indices are stored as attributes already.
#    However, this allows us to change the material slots (i.e. convert
#    to UDIM) while retaining access to the original Daz Studio surfaces.
dson_mats:BMLayerItem = bm.faces.layers.int.new("dson_material_indices")

# Add vertices
for (index, dson_vertex) in enumerate(struct.vertices):
    coordinate:Vector = Vector(dson_vertex)
    vertex:BMVert = bm.verts.new(coordinate)
    vertex[dson_vert] = index

bm.verts.ensure_lookup_table()

# Add faces
for (index, polygon) in enumerate(struct.polygons):
    
    # If a face has bad geometry, polygon's __iter__() method will
    #    return None and the face is skipped. Such a face would've
    #    been drawn as an edge anyway, so there will be no practical
    #    effect on the mesh, visually.
    vertices:list[BMVert] = [ bm.verts[index] for index in polygon ]
    
    if vertices:
        face:BMFace = bm.faces.new(vertices)
        face[dson_face] = index
        face[dson_mats] = struct.material_indices[index]

# Clean up
bm.to_mesh(mesh)
bm.free()

# Add newly-created mesh to scene.
# NOTE: This does not translate from Daz Studio's coordinate system,
#    so assets will be loaded at 100x scale and oriented Y-up.
obj:Object = bpy.data.objects.new(struct.library_id, mesh)
bpy.context.view_layer.layer_collection.collection.objects.link(obj)
