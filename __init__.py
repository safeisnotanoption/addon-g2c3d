bl_info = {
    "name": "Gmaps2City3D",
    "author": "Imran Dzhumabaev",
    "version": (1, 0, 0),
    "blender": (2, 78, 0),
    "location": "View3D > Add > Mesh",
    "description": "Generate 3D cities from google maps.",
    "wiki_url": " ",
    "tracker_url": " ",
    "category": "Add Mesh"
}

if "bpy" in locals():
    # reload logic (magic)
    import importlib
    importlib.reload(g2c3d)
else:
    from . import g2c3d

import bpy
from bpy.props import StringProperty, BoolProperty, FloatProperty
from bpy.types import Operator

class G2C3D(Operator):
    """City generator"""
    bl_idname = "mesh.generate_city"
    bl_label = "City"
    bl_options = {'REGISTER', 'UNDO'}

    latitude = FloatProperty(
        name	= 'latitude',
        default		= 59.8702089,
        description	= "geographic coordinate that specifies "
                         "the north–south position of a point")
    longitude = FloatProperty(
        name='longitude',
        default	= 29.8649487,
        description	= "geographic coordinate that specifies "
                         "the east-west position of a point")
    zoom = FloatProperty(
        name='zoom',
        default=16,
        description	= "zoom level")
    eps = FloatProperty(
        name='eps',
        default=2,
        description="error")
    height = FloatProperty(
        name='height',
        default=5,
        description="height of buildings")
    landscape  = BoolProperty(default=False, name='Create landscape')
    buildings = BoolProperty(default=False, name='Create buildings')
    roads = BoolProperty(default=False, name='Create roads')
    #inverted_roads = BoolProperty(default=True, name='Is roadcontour inverted')


    def execute(self, context):
        g2c3d.create_city(
            self.latitude,
            self.longitude,
            self.zoom,
            self.eps,
            self.height,
            self.landscape,
            self.buildings,
            self.roads)
        return {'FINISHED'}

def menu_func(self, context):
    self.layout.operator(G2C3D.bl_idname, text="City")

def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_mesh_add.append(menu_func)

def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_mesh_add.remove(menu_func)

if __name__ == "__main__":
    register()
