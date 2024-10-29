"""Sample script demonstrating how to apply a skin binding from a DSF file.

This script only handles the "node_weights" type used by Genesis 3 and
onward. TriAx, etc. won't work.

It also assumes a Genesis 8 Female mesh and armature have been loaded into
the scene, in the same manner as the "create_geometry_from_library.py" and
"create_armature_from_library.py" sample scripts.
"""

# Import packages
import bpy
import dufman

# Import datatypes
from bpy.types import ArmatureModifier, Object, VertexGroup
from dufman.datatypes import DsonWeightedJoint
from dufman.structs.modifier import DsonModifier
from dufman.url import AssetURL

# Replace these.
#   - DIRECTORY should match the user's Daz Studio content directory.
#   - FILEPATH should be a DSF (not DUF) file containing a SkinBinding.
#   - RIG_NAME is the name of a DSON figure node, previously imported.
#   - GEO_NAME is the name of the DSON geometry associated with the
#       RIG_NAME node.
DIRECTORY:str = "C:/Users/Public/Documents/Daz3D"
FILEPATH:str = "/data/DAZ 3D/Genesis 8/Female/Genesis8Female.dsf#SkinBinding"
RIG_NAME:str = "Genesis8Female"
GEO_NAME:str = "geometry"

# Get pointers to previously-created assets.
rig_obj:Object = bpy.data.objects[RIG_NAME]
geo_obj:Object = bpy.data.objects[GEO_NAME]

# Add user content directory.
dufman.file.add_content_directory(DIRECTORY)

# Extract modifier asset from file.
struct:DsonModifier = dufman.create.modifier.create_modifier_struct(FILEPATH)

# Ensure data is valid
if not struct.skin_binding:
    raise Exception("DSF file does not contain a skin binding modifier.")

if not struct.skin_binding.expected_vertices == len(geo_obj.data.vertices):
    raise Exception("Could not load skin binding modifier. Vertex count mismatch.")

# Dictionary holding DsonWeightedJoint objects representing bone weights.
weighted_joints:dict = struct.skin_binding.weighted_joints

# Loop through all bone weight groups and create vertex groups for them.
for joint_id in weighted_joints:
    
    joint:DsonWeightedJoint = weighted_joints[joint_id]

    # Node/bone name is stored as a URL, with a pound sign. This strips it off.
    bone_name:str = dufman.url.parse_url_string(joint.node_target).asset_id

    # Add bone weight to mesh as vertex group.
    vertex_group:VertexGroup = geo_obj.vertex_groups.new(name=bone_name)
    
    # Assign weights from DSON file.
    for vertex_index in joint.node_weights:
        value:float = joint.node_weights[vertex_index]
        vertex_group.add( [vertex_index], value, 'REPLACE')

# Parent mesh to armature.
geo_obj.parent = rig_obj

arm_mod:ArmatureModifier = geo_obj.modifiers.new(name="DsonSkinBinding", type='ARMATURE')
arm_mod.use_deform_preserve_volume = True
arm_mod.object = rig_obj
