"""Sample script demonstrating how to create an armature using a DSF file."""

# Import packages
import bpy
import mathutils
import dufman

# Import datatypes
from bpy.types import Armature, EditBone, Object, PoseBone, ViewLayer
from dufman.enums import RotationOrder
from dufman.structs.node import DsonNode
from dufman.url import AssetURL, create_url_string, parse_url_string
from math import isclose, radians
from pathlib import Path
from mathutils import Euler, Matrix, Quaternion, Vector

# Replace these.
# - DIRECTORY should match the user's Daz Studio setup.
# - FILEPATH is the URL to a figure, with bone children. 
#     For this sample, we will use the Genesis 8 Female
#     armature.
DIRECTORY:str = "C:/Users/Public/Documents/Daz3D"
FILEPATH:str = "/data/DAZ 3D/Genesis 8/Female/Genesis8Female.dsf#Genesis8Female"

# Add user content directory.
dufman.file.add_content_directory(DIRECTORY)

# Extract DsonNode structs from DSF file.
root_struct:DsonNode = dufman.create.node.create_node_struct(FILEPATH)
hierarchy_urls:list[str] = dufman.library.get_node_hierarchy_urls_from_library(FILEPATH)
hierarchy_structs:list[DsonNode] = []

for url in hierarchy_urls:
    bone_struct:DsonNode = dufman.create.node.create_node_struct(url)
    hierarchy_structs.append(bone_struct)

# Add objects to BlendData
armature:Armature = bpy.data.armatures.new(root_struct.library_id)
obj:Object = bpy.data.objects.new(root_struct.library_id, armature)

# Set view layer for armature editing. Normally, we would use
#   a context override here. However, changing modes does not
#   use the context, so we're forced to do it for real.
view_layer:ViewLayer = bpy.context.view_layer
view_layer.layer_collection.collection.objects.link(obj)
view_layer.objects.active = obj
bpy.ops.object.mode_set(mode='EDIT')

# World position of armature.
origin:Vector = Vector(root_struct.center_point)

# Loop through bones and construct armature.
for bone_struct in hierarchy_structs:
    
    # Newly-created bone.
    edit_bone:EditBone = armature.edit_bones.new(bone_struct.library_id)
    
    # Convert orientation from degrees to radians
    or_x:float = radians(bone_struct.orientation.x.current)
    or_y:float = radians(bone_struct.orientation.y.current)
    or_z:float = radians(bone_struct.orientation.z.current)
    
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

# Clean up after armature editing
bpy.ops.object.mode_set(mode='OBJECT')

# Needed to ensure pose bones are created.
view_layer.update()

# Set properties on pose bones.
for bone_struct in hierarchy_structs:
    
    pose_bone:PoseBone = obj.pose.bones[bone_struct.library_id]
    pose_bone.rotation_mode = RotationOrder(bone_struct.rotation_order).value
    
    # NOTE: Bones can have their properties driven by
    #   formulas, but these have been omitted for the
    #   sake of simplicity.
