bl_info = {
    "name": "Haircuts for Mesh",
    "description": "Streamline mesh editing with tools for converting viewport colors to vertex colors, selecting unnecessary loops, and adjusting edge sharpness.",
    "blender": (4, 2, 3),
    "category": "Object",
    "location": "View3D > UI > Haircuts for Mesh",
    "version": (1, 2),
    "author": "rentanek0"
}

import bpy

# Import operators and panels
from .operators import OBJECT_OT_convert_to_vertex_colors, TLA_OT_select_useless_loops, MoveArmatureOriginToCursorOperator, RigToWeightPaintOperator
from .panels import VIEW3D_PT_haircuts_for_mesh

classes = [
    OBJECT_OT_convert_to_vertex_colors,
    TLA_OT_select_useless_loops,
    MoveArmatureOriginToCursorOperator,
    RigToWeightPaintOperator,
    VIEW3D_PT_haircuts_for_mesh
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.select_precision = bpy.props.FloatProperty(
        name='Precision [°]',
        default=3.0,
        min=0.0,  # Minimum value constraint
        update=update_select_precision  # Assign update callback function
    )

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.select_precision

# Update callback function for select_precision property
def update_select_precision(self, context):
    # Execute the operator whenever select_precision changes
    bpy.ops.object.select_useless_loops()

if __name__ == "__main__":
    register()
