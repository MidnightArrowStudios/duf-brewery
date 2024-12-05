"""Sample file showing how to load an armature asset from a DSF file.

Prerequisites:
    -None
"""

# ============================================================================ #
# IMPORT                                                                       #
# ============================================================================ #

# python stdlib
from math import isclose, radians
from pathlib import Path

# bpy
import bpy
from bpy.types import Armature, Context, EditBone, Object, ViewLayer

# mathutils
from mathutils import Euler, Matrix, Quaternion, Vector

# dufman
from dufman.enums import NodeType, RotationOrder
from dufman.file import add_content_directory, remove_content_directory
from dufman.library import get_node_hierarchy_urls_from_library
from dufman.structs import DsonNode
from dufman.url import AssetURL, create_url_string, parse_url_string


# ============================================================================ #
# FUNCTION                                                                     #
# ============================================================================ #

def create_armature(context:Context, figure_struct:DsonNode) -> Object:
    """Create an armature using the data inside a DsonNode struct."""

    # Ensure root node is the correct type.
    if not figure_struct.node_type == NodeType.FIGURE:
        raise Exception("NodeType must be \"figure\"")

    # Array of child nodes.
    bone_structs:list[DsonNode] = []

    # Return URLs of all child nodes, ensure they have the correct type,
    #   and add them to the list.
    for child_url in get_node_hierarchy_urls_from_library(figure_struct.dsf_file):
        struct:DsonNode = DsonNode.load(child_url)
        if not struct.node_type == NodeType.BONE:
            raise Exception("Non-bone node was returned from \"get_node_hierarchy_urls_from_library()\"")
        bone_structs.append(struct)
    
    # Create blend file objects
    rig_name:str = figure_struct.library_id
    armature:Armature = context.blend_data.armatures.new(rig_name)
    arm_object:Object = context.blend_data.objects.new(rig_name, armature)
    
    # Setup armature editing
    # Normally, we would use a context override. But Blender does not have a
    #   bmesh-equivalent for armatures, so we must add the armature into the 
    #   current scene to edit it.
    view_layer:ViewLayer = context.view_layer
    view_layer.layer_collection.collection.objects.link(arm_object)
    view_layer.objects.active = arm_object
    bpy.ops.object.mode_set(mode='EDIT')
    
    # World position of armature. Subtracted from each bone to offset its
    #   position.
    origin:Vector = Vector(figure_struct.center_point)
    
    # Create individual bones.
    for bone_struct in bone_structs:
        
        # The newly-created bone object.
        edit_bone:EditBone = armature.edit_bones.new(bone_struct.library_id)

        # Convert orientation from degrees to radians
        or_x:float = radians(bone_struct.orientation.x)
        or_y:float = radians(bone_struct.orientation.y)
        or_z:float = radians(bone_struct.orientation.z)
        
        # Declare important variables
        center_point    : Vector            = Vector(bone_struct.center_point)
        end_point       : Vector            = Vector(bone_struct.end_point)
        orientation     : Vector            = Vector((or_x, or_y, or_z))
        rotation_order  : RotationOrder     = bone_struct.rotation_order
        
        # NOTE: Not sure about these enums.
        edit_bone.inherit_scale = 'FULL' if bone_struct.inherits_scale else 'NONE'

        # Since we are not setting the tail position directly, we
        #   need to pre-set the length. Length is applied on the
        #   Y-axis (not the Z-axis, as when creating a new
        #   armature), so our bone will point in the positive Y.
        bone_length:float = (end_point - center_point).length
        
        # If bone length is zero, it won't be created. Daz assets
        #   sometimes use zero-length bones for environment nodes.
        if isclose(bone_length, 0.0):
            bone_length = 0.01
        
        edit_bone.length = bone_length
        
        # Orientation, in Daz Studio's Joint Editor, is a rotational
        #   offset from the X axis. Despite how it may seem, the
        #   rotation order has no effect at this stage. It only
        #   changes how the bone is drawn visually, not its actual
        #   orientation. Orientation is ALWAYS calculated in XYZ
        #   order.
        daz_orientation:Matrix = Euler(orientation, 'XYZ').to_matrix().to_4x4()

        # Blender bones are always oriented along the Y axis. To
        #   match their (visual) representation in Daz Studio, we
        #   must rotate them in 90-degree increments according to
        #   their rotation order.
        daz_direction:Matrix = None
        match(rotation_order.value[0].upper()):
            case 'X':
                daz_direction = Matrix.Rotation(radians(-90), 4, 'Z')
            case 'Y':
                daz_direction = Matrix.Identity(4)
            case 'Z':
                daz_direction = Matrix.Rotation(radians( 90), 4, 'X')

        # Bones are flipped according to whether the end point
        #   is less than the center point on the primary rotation
        #   order axis.
        daz_flip:Matrix = Matrix.Identity(4)
        match(rotation_order.value[0].upper()):
            case 'X':
                if end_point.x < center_point.x:
                    daz_flip = Matrix.Rotation(radians(180), 4, 'X')
            case 'Y':
                if end_point.y < center_point.y:
                    daz_flip = Matrix.Rotation(radians(180), 4, 'X')
            case 'Z':
                if end_point.z < center_point.z:
                    daz_flip = Matrix.Rotation(radians(180), 4, 'Z')

        # In Daz Studio, the Joint Editor defines a bone's
        #   position in world space. To compensate, we must
        #   subtract the origin point of the armature.
        translation:Matrix = Matrix.Translation(center_point - origin).to_4x4()

        # Set bone's position.
        edit_bone.matrix = translation @ daz_orientation @ daz_direction @ daz_flip
        
        # Assign parenting
        # TODO: Can a bone have a parent in another file?
        #   Probably not, but might be an edge case?
        parent_id:AssetURL = parse_url_string(bone_struct.parent).asset_id
        if parent_id and parent_id in armature.edit_bones:
            edit_bone.parent = armature.edit_bones[parent_id]

    # Clean up after armature editing.
    bpy.ops.object.mode_set(mode='OBJECT')

    # Needed to ensure pose bones are available for editing.
    view_layer.update()

    # Some properties can only be set on PoseBone objects.
    for bone_struct in bone_structs:
        
        pose_bone:PoseBone = arm_object.pose.bones[bone_struct.library_id]
        pose_bone.rotation_mode = RotationOrder(bone_struct.rotation_order).value
        
        # NOTE: Bones can have their properties driven by formulas, but these
        #   have been omitted for the sake of simplicity.
        
        # A more robust implementation will probably want to cache data from
        #   the struct as custom properties on the bone itself.

    return arm_object


# ============================================================================ #
# SCRIPT                                                                       #
# ============================================================================ #

# Change this to match Daz Studio install directory
CONTENT_DIRECTORY:str = "C:/Users/Public/Documents/Daz3D"
ARMATURE_URL:str = "/data/DAZ 3D/Genesis 8/Female/Genesis8Female.dsf#Genesis8Female"

# ============================================================================ #

# Setup
add_content_directory(CONTENT_DIRECTORY)

# Construct intermediate representation using DUFMan
struct:DsonNode = DsonNode.load(ARMATURE_URL)

# Create object data and add it to scene
obj:Object = create_armature(bpy.context, struct)
obj.show_in_front = True
obj.data.display_type = 'STICK'

# Cleanup
remove_content_directory(CONTENT_DIRECTORY)
