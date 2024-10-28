"""Sample file showing how to load a geometry asset from a DSON file."""

# Import packages
import bpy
import bmesh
import mathutils
import dufman

# Import datatypes
from bpy.types import Mesh, Object
from bmesh.types import BMesh, BMVert
from mathutils import Vector
from dufman.structs.geometry import DsonGeometry

# Replace these 
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

# Add vertices
for vertex in struct.vertices:
    coordinate:Vector = Vector(vertex)
    bm.verts.new(coordinate)

bm.verts.ensure_lookup_table()

# Add faces
for polygon in struct.polygons:
    vertices:list[BMVert] = [ bm.verts[index] for index in polygon ]
    bm.faces.new(vertices)

# Clean up
bm.to_mesh(mesh)
bm.free()

# Add newly-created mesh to scene
obj:Object = bpy.data.objects.new(struct.library_id, mesh)
bpy.context.view_layer.layer_collection.collection.objects.link(obj)