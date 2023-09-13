# Utility functions
import bpy, bmesh, mathutils
from datetime import datetime

from mathutils import Vector

def debug_print(text_to_be_printed):
    print("Debug:" + text_to_be_printed)

    # Find the first camera object
    camera = next((obj for obj in bpy.data.objects if obj.type == 'CAMERA'), None)
    if camera is None:
        print("No camera found.")
        return
    
    # Check if DebugText already exists
    if "DebugText" in bpy.data.objects:
        text_obj = bpy.data.objects["DebugText"]
        text_obj.data.body = text_to_be_printed
    else:
        # Create new text object
        # Make sure you're in Object Mode before adding text
        if bpy.context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')

        # Create new text object
        bpy.ops.object.text_add(enter_editmode=False, align='WORLD', location=(0, 0, 0))
        text_obj = bpy.context.object
        text_obj.name = "DebugText"
        
    # Set the text
    text_obj.data.body = text_to_be_printed
    
    # Position and rotate the text object to align with the camera view
    text_obj.location = camera.location + Vector((0, 0, -1))
    text_obj.rotation_euler = camera.rotation_euler
    
    # Scale the text object
    text_obj.scale = (0.1, 0.1, 0.1)
