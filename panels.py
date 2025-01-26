import bpy

class VIEW3D_PT_haircuts_for_mesh(bpy.types.Panel):
    bl_label = "Haircuts for Mesh"
    bl_idname = "VIEW3D_PT_haircuts_for_mesh"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Haircuts for Mesh'

    def draw(self, context):
        layout = self.layout
        layout.operator("object.convert_to_vertex_colors")
        layout.separator(factor=1.0)
        layout.operator("object.convert_rig_to_weight_paint", text="Convert Rig to Weight Paint")
        layout.separator(factor=1.0)
        layout.label(text="Select useless loops")
        layout.prop(context.scene, "select_precision")
        layout.operator("object.select_useless_loops", text="SELECT")
        layout.separator(factor=1.0)
        layout.operator("object.move_armature_origin_to_cursor")
        
        #https://docs.blender.org/api/current/bpy.types.UILayout.html
        #https://docs.blender.org/api/current/bpy.types.Panel.html


