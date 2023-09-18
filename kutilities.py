# Utility functions
import bpy, bmesh, mathutils
from datetime import datetime

from mathutils import Vector

# Initialize a list to keep track of the text buffer
text_buffer = []
text_counter = 1

def debug_print(text_to_be_printed):
    print(text_to_be_printed)

    global text_buffer
    
    # Append new text to the buffer
    text_buffer.append(text_to_be_printed)
    
    # Remove the oldest text if buffer exceeds 20 lines
    if len(text_buffer) > 20:
        text_buffer.pop(0)
    
    # Combine text buffer into a single string
    combined_text = "\n".join(text_counter + " " + text_buffer)
    text_counter += 1

    # Find the first camera object
    camera = next((obj for obj in bpy.data.objects if obj.type == 'CAMERA'), None)
    if camera is None:
        print("No camera found.")
        return
    
    # Check if DebugText already exists
    if "DebugText" in bpy.data.objects:
        text_obj = bpy.data.objects["DebugText"]
        text_obj.data.body = combined_text
    else:
        # Create new text object
        if bpy.context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.text_add(enter_editmode=False, align='WORLD', location=(0, 0, 0))
        text_obj = bpy.context.object
        text_obj.name = "DebugText"
        
    # Set the text
    text_obj.data.body = combined_text
    
    # Position and rotate the text object to align with the camera view
    # text_obj.location = camera.location + Vector((0, 0, -1))

    # Calculate the direction the camera is facing
    camera_direction = mathutils.Vector((0, 0, -1))
    camera_direction.rotate(camera.rotation_euler)

    # Position the text object in front of the camera
    distance_in_front_of_camera = 3  # Adjust this distance as needed
    text_obj.location = camera.location + camera_direction * distance_in_front_of_camera
    text_obj.rotation_euler = camera.rotation_euler

    # Add constraints to make the text follow the camera
    if "FollowCameraLoc" not in text_obj.constraints:
        loc_constraint = text_obj.constraints.new('COPY_LOCATION')
        loc_constraint.name = "FollowCameraLoc"
        loc_constraint.target = camera

    if "FollowCameraRot" not in text_obj.constraints:
        rot_constraint = text_obj.constraints.new('COPY_ROTATION')
        rot_constraint.name = "FollowCameraRot"
        rot_constraint.target = camera

#    # Move the camera to frame the new text
#    camera.location = text_obj.location + Vector((0, 0, 1.5))
    
    # Scale the text object
    text_obj.scale = (0.05, 0.05, 0.05)
    
    # TODO: Add code to highlight the new line with a different material
