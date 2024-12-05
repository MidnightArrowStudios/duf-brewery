"""Sample file showing how to apply a SkinBinding asset from a DSF file.

This only handles "node_weights" skin binding used by Genesis 3 and above.

Prerequisites:
    -run "create_geometry_from_library.py"
    -run "create_armature_from_library.py"
"""


# ============================================================================ #
# IMPORT                                                                       #
# ============================================================================ #

# bpy
import bpy
from bpy.types import ArmatureModifier, Object, VertexGroup

# dufman
from dufman.file import add_content_directory, remove_content_directory
from dufman.structs import DsonModifier, DsonSkinBinding, DsonWeightedJoint
from dufman.url import parse_url_string


# ============================================================================ #
# FUNCTION                                                                     #
# ============================================================================ #

def apply_skin_binding(geometry:Object, armature:Object, struct:DsonModifier) -> ArmatureModifier:
    """Rig a mesh to an armature using the data inside a DsonModifier struct."""

    # Modifiers is either a control property or a morph, not a skin binding.
    if not struct.skin_binding:
        raise Exception("Modifier does not contain skin binding.")
    
    # Get sub-object
    binding:DsonSkinBinding = struct.skin_binding
    
    # Mesh does not have the right number of vertices.
    if binding.expected_vertices != len(geometry.data.vertices):
        raise Exception("Could not apply skin binding. Vertex count mismatch.")
    
    # Create a vertex group for each bone weight.
    for weighted_joint in binding.weighted_joints:

        # Names are stored as URLs, with pound signs. This strips them off.
        bone_name:str = parse_url_string(weighted_joint.node).asset_id
        
        # Add vertex group to object.
        vertex_group:VertexGroup = geometry.vertex_groups.new(name=bone_name)
    
        # Assign the weights based on their index.
        for vertex_index in weighted_joint.node_weights:
            
            # Weights are stored in a dictionary, with the vertex index as
            #   the key.
            value:float = weighted_joint.node_weights[vertex_index]
            vertex_group.add([vertex_index], value, 'REPLACE')
    
    # Parent objects
    geometry.parent = armature
    
    # Create modifier
    arm_mod:ArmatureModifier = geometry.modifiers.new(name=struct.library_id, type='ARMATURE')
    arm_mod.use_deform_preserve_volume = True
    arm_mod.object = armature
    
    return arm_mod


# ============================================================================ #
# FUNCTION                                                                     #
# ============================================================================ #

# Change this to match Daz Studio install directory
CONTENT_DIRECTORY:str = "C:/Users/Public/Documents/Daz3D"
SKIN_BINDING_URL:str = "/data/DAZ 3D/Genesis 8/Female/Genesis8Female.dsf#SkinBinding"

# ============================================================================ #

# Setup
add_content_directory(CONTENT_DIRECTORY)

# Retrieve objects to apply skin binding to. These should have been already
#   created by running "create_armature_from_library.py" and 
#   "create_geometry_from_library.py".
armature_object:Object = bpy.data.objects["Genesis8Female"]
geometry_object:Object = bpy.data.objects["geometry"]

# Construct intermediate representation using DUFMan.
struct:DsonModifier = DsonModifier.load(SKIN_BINDING_URL)

# Apply skin binding to mesh and armature.
apply_skin_binding(geometry_object, armature_object, struct)

# Cleanup
remove_content_directory(CONTENT_DIRECTORY)
