import bpy


class SDFStrategy:
    def create_proxy(self, context):
        raise NotImplementedError

    def update_proxy(self, context, proxy_object_name):
        raise NotImplementedError


class SphereStrategy(SDFStrategy):
    def __init__(self, center, radius):
        self.center = center
        self.radius = radius
        self.proxy_object = None

    def create_proxy(self, context):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=self.radius, location=self.center)
        proxy_object = bpy.context.active_object
        proxy_object.display_type = "WIRE"
        proxy_object.name = "SDF_Sphere"
        return proxy_object

    def update_proxy(self, proxy_object_name):
        proxy_object = bpy.data.objects.get(proxy_object_name)
        if proxy_object:
            proxy_object.location = self.center
            proxy_object.scale = (self.radius, self.radius, self.radius)


class PG_ShapeProperties(bpy.types.PropertyGroup):
    proxy_object: bpy.props.PointerProperty(type=bpy.types.Object)
    center: bpy.props.FloatVectorProperty(name="Center", subtype="XYZ")
    radius: bpy.props.FloatProperty(name="Radius")

    def create_proxy(self, context):
        pass

    def update_proxy(self, context):
        pass


class PG_ShapePropertiesSphere(PG_ShapeProperties):
    def set_strategy(self, context) -> None:
        self.strategy = SphereStrategy(center=self.center, radius=self.radius)

    def create_proxy(self, context):
        self.proxy_object = self.strategy.create_proxy(context)

    def update_proxy(self, context):
        self.strategy.update_proxy(self.proxy_object.name)


class PG_SDFPrimitive(bpy.types.PropertyGroup):
    shape_type: bpy.props.StringProperty(name="Strategy")
    shape_properties: bpy.props.PointerProperty(type=PG_ShapeProperties)
    # Add additional strategy properties for other types like box_strategy, etc.


class PG_SDFShape(bpy.types.PropertyGroup):
    primitives: bpy.props.CollectionProperty(type=PG_SDFPrimitive)


class OP_AddSDFPrimitiveOperator(bpy.types.Operator):
    bl_idname = "sdf.add_primitive"
    bl_label = "Add SDF Primitive"
    primitive_type: bpy.props.StringProperty()

    def execute(self, context):
        sdf_shape: PG_SDFShape = context.scene.sdf_shape
        primitives: PG_SDFPrimitive = sdf_shape.primitives
        new_primitive: PG_SDFPrimitive = primitives.add()

        new_primitive.shape_type = self.primitive_type

        if self.primitive_type == "sphere":
            # Instead of instantiating SDFSphereStrategy, set its properties directly
            new_primitive.shape_properties = PG_ShapePropertiesSphere()
            new_primitive.shape_properties.center = (0, 0, 0)
            new_primitive.shape_properties.radius = 1

        new_primitive.shape_properties.set_strategy(context)
        new_primitive.shape_properties.create_proxy(context)

        # Handle other types if necessary
        return {"FINISHED"}


class PA_SDFPanel(bpy.types.Panel):
    bl_label = "SDF Primitives"
    bl_idname = "VIEW3D_PT_sdf"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "SDF"

    def draw(self, context):
        layout = self.layout
        sdf_shape: PG_SDFShape = context.scene.sdf_shape
        layout.operator(
            "sdf.add_primitive", text="Add Sphere"
        ).primitive_type = "sphere"
        # Add buttons for other primitive types

        for i, prim in enumerate(sdf_shape.primitives):
            primitive: PG_SDFPrimitive = prim
            box = layout.box()
            box.prop(primitive, "strategy_type", text="Type")
            strategy = primitive.shape_properties
            if primitive.shape_type == "sphere":
                box.prop(strategy, "center")
                box.prop(strategy, "radius")
            # UI for other types


def register():
    bpy.utils.register_class(PG_ShapeProperties)
    bpy.utils.register_class(PG_ShapePropertiesSphere)
    bpy.utils.register_class(PG_SDFPrimitive)
    bpy.utils.register_class(PG_SDFShape)
    bpy.utils.register_class(OP_AddSDFPrimitiveOperator)
    bpy.utils.register_class(PA_SDFPanel)
    bpy.types.Scene.sdf_shape = bpy.props.PointerProperty(type=PG_SDFShape)


def unregister():
    del bpy.types.Scene.sdf_shape
    bpy.utils.unregister_class(PA_SDFPanel)
    bpy.utils.unregister_class(OP_AddSDFPrimitiveOperator)
    bpy.utils.unregister_class(PG_SDFShape)
    bpy.utils.unregister_class(PG_SDFPrimitive)
    bpy.utils.unregister_class(PG_ShapePropertiesSphere)
    bpy.utils.unregister_class(PG_ShapeProperties)


if __name__ == "__main__":
    register()

# import bpy

# bl_info = {
#     "name": "SDF Primitives",
#     "author": "Your Name",
#     "version": (1, 0),
#     "blender": (2, 93, 0),
#     "location": "View3D > Sidebar > SDF Tab",
#     "description": "Manage SDF Primitives in the 3D Viewport",
#     "category": "3D View",
# }


# class SDFPrimitive:
#     def create_proxy(self, context):
#         raise NotImplementedError

#     def update_proxy(self, context):
#         raise NotImplementedError

#     def generate_glsl(self):
#         raise NotImplementedError


# class SpherePrimitive(SDFPrimitive):
#     def __init__(self, center, radius):
#         self.center = center
#         self.radius = radius
#         self.proxy_object = None

#     def create_proxy(self, context):
#         bpy.ops.mesh.primitive_uv_sphere_add(radius=self.radius, location=self.center)
#         self.proxy_object = bpy.context.active_object
#         self.proxy_object.display_type = "WIRE"
#         self.proxy_object.name = "SDF_Sphere"

#     def update_proxy(self, context):
#         self.proxy_object.location = self.center
#         self.proxy_object.scale = (self.radius, self.radius, self.radius)

#     def generate_glsl(self):
#         return f"float sdSphere(vec3 p) {{ return length(p - vec3{self.center}) - {self.radius}; }}"


# class SpherePrimitiveItem(bpy.types.PropertyGroup):
#     center: bpy.props.FloatVectorProperty(name="Center", subtype="XYZ")
#     radius: bpy.props.FloatProperty(name="Radius")


# class SDFPrimitiveItem(bpy.types.PropertyGroup):
#     # Example properties for a SpherePrimitive
#     # These need to be bpy.props types
#     center: bpy.props.FloatVectorProperty(name="Center", subtype="XYZ")
#     radius: bpy.props.FloatProperty(name="Radius")
#     # You can add more properties for different types of primitives


# # Register this class


# class SDFShape(bpy.types.PropertyGroup):
#     primitives: bpy.props.CollectionProperty(type=SDFPrimitiveItem)

#     def add_primitive(self, primitive_type, center, radius):
#         item: SDFPrimitiveItem = self.primitives.add()
#         item.center = center
#         item.radius = radius
#         # other primitive properties...

#     def update_primitive(self, index, new_params):
#         if 0 <= index < len(self.primitives):
#             self.primitives[index].update_proxy(bpy.context, **new_params)

#     def generate_combined_glsl_code(self):
#         return "\n".join([primitive.generate_glsl() for primitive in self.primitives])


# class AddSDFPrimitiveOperator(bpy.types.Operator):
#     bl_idname = "sdf.add_primitive"
#     bl_label = "Add SDF Primitive"

#     primitive_type: bpy.props.StringProperty()

#     def execute(self, context):
#         sdf_shape: SDFShape = context.scene.sdf_shape
#         if self.primitive_type == "sphere":
#             sdf_shape.add_primitive("sphere", (0, 0, 0), 1)
#             # Handle the creation of the proxy object here
#         else:
#             self.report({"WARNING"}, "Unknown primitive type")
#             return {"CANCELLED"}

#         return {"FINISHED"}


# class UpdateSDFPrimitiveOperator(bpy.types.Operator):
#     bl_idname = "sdf.update_primitive"
#     bl_label = "Update SDF Primitive"

#     index: bpy.props.IntProperty()  # Index of the primitive to update

#     # Assuming we're updating a sphere primitive
#     new_center: bpy.props.FloatVectorProperty(name="New Center", subtype="XYZ", size=3)
#     new_radius: bpy.props.FloatProperty(name="New Radius")

#     def execute(self, context):
#         sdf_shape: SDFShape = context.scene.sdf_shape

#         # Ensure the index is valid
#         if 0 <= self.index < len(sdf_shape.primitives):
#             primitive = sdf_shape.primitives[self.index]
#             if isinstance(primitive, SpherePrimitive):
#                 # Assuming SpherePrimitive has methods to update center and radius
#                 primitive.update_center(self.new_center)
#                 primitive.update_radius(self.new_radius)
#                 # Handle proxy update and GLSL update
#             else:
#                 self.report({"WARNING"}, "Primitive type does not match")
#                 return {"CANCELLED"}
#         else:
#             self.report({"WARNING"}, "Invalid primitive index")
#             return {"CANCELLED"}

#         return {"FINISHED"}


# class RemoveSDFPrimitiveOperator(bpy.types.Operator):
#     bl_idname = "sdf.remove_primitive"
#     bl_label = "Remove SDF Primitive"

#     index: bpy.props.IntProperty()

#     def execute(self, context):
#         sdf_shape: SDFShape = context.scene.sdf_shape
#         sdf_shape.remove_primitive(self.index)
#         return {"FINISHED"}


# class SDFPanel(bpy.types.Panel):
#     bl_label = "SDF Primitives"
#     bl_idname = "VIEW3D_PT_sdf"
#     bl_space_type = "VIEW_3D"
#     bl_region_type = "UI"
#     bl_category = "SDF"

#     def draw(self, context):
#         layout = self.layout

#         # Other UI components...
#         sdf_shape: SDFShape = context.scene.sdf_shape

#         for i, primitive in enumerate(sdf_shape.primitives):
#             box = layout.box()
#             box.label(text=f"Primitive {i}: Sphere")  # Simplified for example
#             # Add UI elements for properties of the primitive
#             box.prop(primitive, "center")
#             box.prop(primitive, "radius")

#             # Conditional UI based on the type of primitive
#             if isinstance(primitive, SpherePrimitive):
#                 box.prop(context.scene, "new_center")
#                 box.prop(context.scene, "new_radius")
#                 update_op = box.operator("sdf.update_primitive", text="Update")
#                 update_op.index = i
#                 update_op.new_center = context.scene.new_center
#                 update_op.new_radius = context.scene.new_radius

#             box.operator("sdf.remove_primitive", text="Remove").index = i


# def register():
#     bpy.utils.register_class(SDFPrimitiveItem)
#     bpy.utils.register_class(SDFShape)
#     bpy.utils.register_class(AddSDFPrimitiveOperator)
#     bpy.utils.register_class(UpdateSDFPrimitiveOperator)
#     bpy.utils.register_class(RemoveSDFPrimitiveOperator)
#     bpy.utils.register_class(SDFPanel)
#     bpy.types.Scene.sdf_shape = bpy.props.PointerProperty(type=SDFShape)
#     bpy.types.Scene.new_center = bpy.props.FloatVectorProperty(
#         name="New Center", subtype="XYZ", size=3
#     )
#     bpy.types.Scene.new_radius = bpy.props.FloatProperty(name="New Radius")


# def unregister():
#     bpy.utils.unregister_class(AddSDFPrimitiveOperator)
#     bpy.utils.unregister_class(UpdateSDFPrimitiveOperator)
#     bpy.utils.unregister_class(RemoveSDFPrimitiveOperator)
#     bpy.utils.unregister_class(SDFPanel)
#     del bpy.types.Scene.sdf_shape
#     del bpy.types.Scene.new_center
#     del bpy.types.Scene.new_radius
#     bpy.utils.unregister_class(SDFShape)
#     bpy.utils.unregister_class(SDFPrimitiveItem)  #


# if __name__ == "__main__":
#     register()
