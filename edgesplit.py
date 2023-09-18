# Blender Python Script to Handle Left Mouse Click and Split Edges and Faces
# This version includes face splitting functionality

bl_info = {
    "name": "KJ Edge and Face Split",
    "blender": (2, 80, 0),
    "category": "Object",
}

import bpy, sys, bmesh, mathutils
from datetime import datetime
from mathutils import Vector

current_file_directory = bpy.path.abspath('//')
if current_file_directory not in sys.path:
    sys.path.append(current_file_directory)

# Import the HUD class from hud.py
from hud import HUD_OT_show_message
from kutilities import debug_print

class EdgeFaceSplitOperator(bpy.types.Operator):
    bl_idname = "object.edge_face_split"
    bl_label = "KJ Edge and Face Split"
    bl_options = {'REGISTER', 'UNDO'}
    
    def modal(self, context, event):
        debug_print("Modal function called")
        
        debug_print("Left mouse button pressed?")
        if not(event.type == 'LEFTMOUSE' and event.value == 'PRESS'):
            debug_print("Left mouse button not pressed.")
            return{'CANCELLED'}
        debug_print("Left mouse button pressed")

        bpy.ops.object.mode_set(mode='EDIT')  # Confirm the mode is EDIT otherwise the script below would not work.
        debug_print("MODE IS EDIT MODE?")
        if not(bpy.context.mode == 'EDIT_MESH'):
            return{'CANCELLED'}
        debug_print("MODE IS EDIT MODE")

        # Get the active mesh
        obj = bpy.context.edit_object
        mesh_data = obj.data
        bmesh_data = bmesh.from_edit_mesh(mesh_data)

        debug_print("Finding the closest edge to click on 3d view.")
        closest_edge = None
        min_distance_to_edge = float('inf')
        mouse_pos = mathutils.Vector((event.mouse_region_x, event.mouse_region_y))
        region_data = [area.spaces.active.region_3d for area in bpy.context.screen.areas if area.type == 'VIEW_3D'][0]
        perspective_matrix = region_data.perspective_matrix

        if not bmesh_data.edges:
            debug_print("No edge found.")
            return{'CANCELLED'}

        for edge in bmesh_data.edges:
            vert1_co = obj.matrix_world @ edge.verts[0].co
            vert2_co = obj.matrix_world @ edge.verts[1].co

            # After applying the perspective matrix
            screen_pos4D1 = perspective_matrix @ vert1_co.to_4d()
            screen_pos4D2 = perspective_matrix @ vert2_co.to_4d()

            # Perform perspective divide
            x1, y1, z1, w1 = screen_pos4D1
            x2, y2, z2, w2 = screen_pos4D2
            screen_pos3D1 = [x1/w1, y1/w1, z1/w1]
            screen_pos3D2 = [x2/w2, y2/w2, z2/w2]

            #converting 4d positions to vectors
            vec_screen_pos3D1 = mathutils.Vector(screen_pos3D1)
            vec_screen_pos3D2 = mathutils.Vector(screen_pos3D2)
            
            # Project down to 2D if needed
            vec_screen_pos2D1 = vec_screen_pos3D1[:2]
            vec_screen_pos2D2 = vec_screen_pos3D2[:2]
            
            vec_screen_pos2D1 = mathutils.Vector(vec_screen_pos3D1[:2])
            vec_screen_pos2D2 = mathutils.Vector(vec_screen_pos3D2[:2])

            edge_center = (vec_screen_pos2D1 + vec_screen_pos2D2) * 0.5
            distance = (mouse_pos - edge_center).length
            debug_print("if4")
            if distance < min_distance_to_edge:
                min_distance_to_edge = distance
                closest_edge = edge

        # Split the closest edge
        if not closest_edge:
            debug_print("No closest edge found.")
            return{'CANCELLED'}
        
        debug_print(f"Closest edge found: {closest_edge}")

        # Splitting at centor for now. TODO:split at click
        bmesh.utils.edge_split(closest_edge, closest_edge.verts[0], closest_edge.calc_length() / 2)
        debug_print("Edge split performed")

        # Update & Free BMesh
        bmesh.update_edit_mesh(mesh_data)
        bpy.context.view_layer.update()
        return {'FINISHED'}
            

    def execute(self, context):
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

class DebugTriggerOperator(bpy.types.Operator):
    bl_idname = "object.debug_trigger"
    bl_label = "Debug Trigger"
    
    def execute(self, context):
        bpy.ops.object.edge_face_split('INVOKE_DEFAULT')
        return {'FINISHED'}

#in order to use alt+shift+ctrl+left mouse click for this script, remove zoom possibly assigned by 3 button mode emulation
def remove_keymap():
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.user
    km = kc.keymaps['3D View']
    
    for kmi in km.keymap_items:
        if kmi.type == 'LEFTMOUSE' and kmi.ctrl and kmi.shift and kmi.alt:
            km.keymap_items.remove(kmi)
            print("Removed existing keymap for Ctrl+Shift+Alt+Left Click")
            break

#restore zoom possibly assigned by 3 button mode emulation
def restore_keymap():
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.user
    km = kc.keymaps['3D View']
#    kmi = km.keymap_items.new('view3d.zoom', 'RIGHTMOUSE', 'PRESS', ctrl=True, alt=True, shift=True)
    kmi = km.keymap_items.new('view3d.zoom', 'LEFTMOUSE', 'PRESS', ctrl=True, alt=True, shift=True)
    debug_print("Restored keymap for Ctrl+Shift+Alt+Left Click")

def register():
    debug_print(f"registering EdgeFaceSplitOperator at {datetime.now()}")
#    bpy.utils.register_class(HUD_OT_show_message)
    bpy.utils.register_class(EdgeFaceSplitOperator)
    bpy.utils.register_class(DebugTriggerOperator) #debug operator
    km, kmi = register_keymaps()
    debug_print(f"registered EdgeFaceSplitOperator at {datetime.now()}")

#    remove_keymap()

def unregister():
    bpy.utils.unregister_class(EdgeFaceSplitOperator)
    bpy.utils.unregister_class(DebugTriggerOperator)  #debug operator
    unregister_keymaps(km, kmi)
    restore_keymap()

def register_keymaps():
    wm = bpy.context.window_manager
    km = wm.keyconfigs.addon.keymaps.new(name='3D View', space_type='VIEW_3D')
    kmi = km.keymap_items.new(EdgeFaceSplitOperator.bl_idname, 'LEFTMOUSE', 'PRESS', ctrl=True, alt=True, shift=True)
    return km, kmi

def unregister_keymaps(km, kmi):
#    bpy.utils.unregister_class(HUD_OT_show_message)
    km.keymap_items.remove(kmi)

if __name__ == '__main__':
    remove_keymap()
    # Uncomment the next line to restore the keymap
    # restore_keymap()
    try:
        unregister()
    except:
        pass
    register()
