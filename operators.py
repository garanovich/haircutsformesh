import bpy
import bmesh
import time

class OBJECT_OT_convert_to_vertex_colors(bpy.types.Operator):
    """ Vertex paint all selected objects with viewport display colors. Useful for baking ID maps. """
    bl_idname = "object.convert_to_vertex_colors"
    bl_label = "Viewport to Vertex Colors"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        start_time = time.time()

        def delete_vertex_colors(obj):
            if obj.type == 'MESH':
                mesh = obj.data
                while mesh.color_attributes:
                    mesh.color_attributes.remove(mesh.color_attributes[0])

        def viewport_to_vertex_color(obj):
            gamma = 2.2

            delete_vertex_colors(obj)

            mesh = obj.data
            bm = bmesh.new()
            bm.from_mesh(mesh)

            color_layer = bm.loops.layers.color.new("Col")

            if not obj.material_slots:
                bm.free()
                return {'NO MATERALS'}

            color_list = [
                [pow(c, 1/gamma) for c in slot.material.diffuse_color[:3]] + [slot.material.diffuse_color[3]]
                if slot.material else [0, 0, 0, 0]
                for slot in obj.material_slots
            ]

            for face in bm.faces:
                color = color_list[face.material_index]
                for loop in face.loops:
                    loop[color_layer] = color

            bm.to_mesh(mesh)
            mesh.vertex_colors.active = mesh.vertex_colors["Col"]

            bm.free()

        wm = bpy.context.window_manager
        selected_objects = context.selected_objects
        tot = len(selected_objects)

        wm.progress_begin(0, tot)

        for i, obj in enumerate(selected_objects):
            viewport_to_vertex_color(obj)
            wm.progress_update(i + 1)

        wm.progress_end()

        elapsed_time = time.time() - start_time
        self.report({'INFO'}, f"Processing complete. Elapsed time: {elapsed_time:.2f} seconds.")
        return {'FINISHED'}

    
class TLA_OT_select_useless_loops(bpy.types.Operator):
    """ Select useless loops """
    bl_idname = "object.select_useless_loops"
    bl_label = "Select Mesh Operations"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # Retrieve the value of select_precision property
        select_precision_value = context.scene.select_precision


        # Check if we are in edit mode, switch to edit mode if not
        if bpy.context.object.mode != 'EDIT':
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='EDGE')
        bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='EDGE')
        

        # Deselect all elements first
        bpy.ops.mesh.select_all(action='DESELECT')
        # Calculate sh using select_precision_value
        sh = select_precision_value * 0.0157079633  # Gradient value adjusted by select_precision

        bpy.ops.mesh.edges_select_sharp(sharpness=sh)
        bpy.ops.mesh.loop_multi_select(ring=False)
        bpy.ops.mesh.select_non_manifold()
        bpy.ops.mesh.select_all(action='INVERT')
        bpy.ops.mesh.loop_multi_select(ring=False)
        # bpy.ops.mesh.select_random(ratio=1e-06, seed=2)
        # bpy.ops.mesh.loop_multi_select(ring=False)

        return {'FINISHED'}
    
class MoveArmatureOriginToCursorOperator(bpy.types.Operator):
    """Automaticly unparent all objects, move armature origin and parent all again"""
    bl_idname = "object.move_armature_origin_to_cursor"
    bl_label = "Move Armature Origin to 3d cursor"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        armature_obj = context.object
        
        if armature_obj is None or armature_obj.type != 'ARMATURE':
            self.report({'ERROR'}, "Выберите объект арматуры")
            return {'CANCELLED'}
        
        original_active = context.view_layer.objects.active

        children_data = []
        
        for child in armature_obj.children:
            if child.parent_type == 'BONE':
                original_matrix = child.matrix_world.copy()
                children_data.append({
                    'object': child,
                    'bone_name': child.parent_bone,
                    'original_matrix': original_matrix
                })
                child.parent = None
                child.matrix_world = original_matrix
        
        context.view_layer.objects.active = armature_obj
        
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')
        
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        
        for data in children_data:
            obj = data['object']
            obj.parent = armature_obj
            obj.parent_type = 'BONE'
            obj.parent_bone = data['bone_name']
            obj.matrix_world = data['original_matrix']
        
        context.view_layer.objects.active = original_active

        self.report({'INFO'}, "Ориджин арматуры успешно перемещен")
        return {'FINISHED'}
    
class RigToWeightPaintOperator(bpy.types.Operator):
    """Convert Rig to Weight Paint"""
    bl_idname = "object.convert_rig_to_weight_paint"
    bl_label = "Convert Rig to Weight Paint"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        try:
            self.convert_rig_to_weight_paint()
            self.report({'INFO'}, "Conversion completed successfully")
        except Exception as e:
            self.report({'ERROR'}, f"Error: {e}")
        return {'FINISHED'}

    def prepare_objects(self, all_objects):
        for obj in all_objects:
            # Проверяем, является ли объект типом 'MESH'
            if obj.type != 'MESH':
                bpy.context.view_layer.objects.active = obj
                bpy.ops.object.convert(target='MESH')
            
            # Устанавливаем уникальные данные для объекта
            if obj.data:
                obj.data = obj.data.copy()
            
            # Объединяем дочерние объекты с родительским объектом
            if obj.children:
                bpy.context.view_layer.objects.active = obj
                bpy.ops.object.select_all(action='DESELECT')
                obj.select_set(True)
                
                for child in obj.children:
                    child.select_set(True)
                
                bpy.ops.object.join()

    def convert_rig_to_weight_paint(self):
        # Определяем активную арматуру
        armature = bpy.context.active_object
        if not armature or armature.type != 'ARMATURE':
            raise ValueError("Please select an armature.")

        # Находим все объекты, привязанные к арматуре
        all_objects = [obj for obj in bpy.context.scene.objects if obj.parent == armature]

        # Подготовка объектов
        self.prepare_objects(all_objects)

        # Находим все объекты ещё раз
        all_objects = [obj for obj in bpy.context.scene.objects if obj.parent == armature]

        # Создаём пары "кость - объект"
        bone_object_pairs = [
            (obj.parent_bone, obj) for obj in all_objects if obj.parent_bone
        ]

        # Создаём модификатор Armature и отвязываем объекты
        for bone_name, obj in bone_object_pairs:
            bpy.context.view_layer.objects.active = obj
            obj.select_set(True)
            bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')

            # Создаём модификатор Armature
            mod = obj.modifiers.new(name='Armature', type='ARMATURE')
            mod.object = armature

            # Устанавливаем веса вершин
            if obj.type == 'MESH':
                vertex_group = obj.vertex_groups.new(name=bone_name)
                vertices = [v.index for v in obj.data.vertices]
                vertex_group.add(vertices, 1.0, 'REPLACE')

        # Объединяем все объекты
        for obj in all_objects:
            obj.select_set(True)
        bpy.context.view_layer.objects.active = all_objects[0]
        bpy.ops.object.join()
        joined_mesh = bpy.context.active_object

        # Устанавливаем origin итогового меша в арматуру
        cursor_location = bpy.context.scene.cursor.location.copy()
        bpy.context.scene.cursor.location = armature.location
        bpy.context.view_layer.objects.active = joined_mesh
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
        bpy.context.scene.cursor.location = cursor_location

        # Привязываем итоговый меш к арматуре
        armature.select_set(True)
        bpy.context.view_layer.objects.active = armature
        bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)

    def invoke(self, context, event):
        return self.execute(context)