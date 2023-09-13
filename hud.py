import bpy
import bgl
import blf
from bpy.types import Operator

class HUD_OT_show_message(Operator):
    bl_idname = "hud.show_message"
    bl_label = "Show HUD Message"
    message: bpy.props.StringProperty()

    def modal(self, context, event):
        context.area.tag_redraw()

        if event.type == 'TIMER':
            self.counter += 1
            if self.counter > 100:
                bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
                return {'FINISHED'}

        return {'PASS_THROUGH'}

    def execute(self, context):
        self.counter = 0

        def draw_callback_px(self, context):
            font_id = 0
            blf.position(font_id, 50 + self.counter, 50, 0)
            blf.size(font_id, 20, 72)
            blf.draw(font_id, self.message)

        self._handle = bpy.types.SpaceView3D.draw_handler_add(draw_callback_px, (self, context), 'WINDOW', 'POST_PIXEL')

        context.window_manager.modal_handler_add(self)
        self._timer = context.window_manager.event_timer_add(0.1, window=context.window)
        return {'RUNNING_MODAL'}

def register():
    bpy.utils.register_class(HUD_OT_show_message)

def unregister():
    bpy.utils.unregister_class(HUD_OT_show_message)
