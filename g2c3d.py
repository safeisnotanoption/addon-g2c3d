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

import requests
import cv2
import os
import numpy as np
import math

try:
    import bpy
    import bmesh
    from bpy.props import StringProperty, BoolProperty, IntProperty, FloatProperty
    from bpy.types import Operator
except ImportError:
    print("You must run this script in Blender")

# eps = 2  # величина погрешности аппроксимации
# # downloading map from google maps
# latitude = 59.8702089
# longitude = 29.8649487


class ExitError(Exception):
    pass


def gmaps_landscape(latitude=59.8702089, longitude=29.8649487, zoom=16, eps=2):
    try:
        satOutput = open("output_landscape.png", 'wb')
    except ExitError:
        print("Couldn't open file for writing.")

    try:
        satOutput.write(requests.get(
            'https://maps.googleapis.com/maps/api/staticmap?center=' + str(latitude) + ',' + str(
                longitude) + '&zoom=' + str(zoom) +
            '&size=640x640&scale=2&maptype=satellite'
            '&style=feature:all|element:labels|visibility:off'
        ).content)
        satOutput.close()
    except ExitError:
        print("Something terrible happened.")

    try:
        satImage = cv2.imread('output_landscape.png')
    except ExitError:
        print("Couldn't open the map image.")

    #cv2.imshow("Map With Contours Added (" + str(latitude) + ',' + str(longitude) + ")", satImage)
    #cv2.waitKey()


def gmaps_buildings(latitude=59.8702089, longitude=29.8649487, zoom=16, eps=2):
    try:
        satOutput = open("output_buildings.png", 'wb')
    except ExitError:
        print("Couldn't open file for writing.")

    try:
        satOutput.write(requests.get(
            'https://maps.googleapis.com/maps/api/staticmap?center=' + str(latitude) + ',' + str(
                longitude) + '&zoom=' + str(zoom) +
            '&size=640x640&scale=1&maptype=roadmap'
            '&style=feature:all|element:labels|visibility:off'
            '&style=feature:all|visibility:off'
            # '&style=feature:landscape.man_made|visibility:on|element:geometry.stroke|color:0xff0000'
            '&style=feature:landscape.man_made|visibility:on|element:geometry.stroke'
            '&style=feature:road|element:geometry|color:0x00ff00'
            '&style=feature:water|element:geometry|color:0x0000ff'
        ).content)
        satOutput.close()
    except ExitError:
        print("Something terrible happened.")

    try:
        satImage = cv2.imread("output_buildings.png", cv2.IMREAD_GRAYSCALE)
    except ExitError:
        print("Couldn't open the map image.")

    img = cv2.imread("output_buildings.png", 0)
    ret, thresh = cv2.threshold(img, 127, 255, 0)
    im2, contours, hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for i in range(len(contours)):
        contours[i] = cv2.approxPolyDP(contours[i], eps, True)  # Ramer–Douglas–Peucker_algorithm
    #cv2.imshow("Map With Contours Added (" + str(latitude) + ',' + str(longitude) + ")", satImage)
    #cv2.waitKey()

    return contours

    # M = cv2.moments(contours[0])
    # cX = int(M["m10"] / M["m00"])/10
    # cY = int(M["m01"] / M["m00"])/10


def gmaps_roads(latitude=59.8702089, longitude=29.8649487, zoom=16, eps=2):
    try:
        satOutput = open('output_roads.png', 'wb')
    except ExitError:
        print("Couldn't open file for writing.")

    try:
        satOutput.write(requests.get(
            'https://maps.googleapis.com/maps/api/staticmap?center=' + str(latitude) + ',' + str(
                longitude) + '&zoom=' + str(zoom) +
            '&size=640x640&scale=1&maptype=roadmap'
            '&style=feature:all|element:labels|visibility:off'
            '&style=feature:all|visibility:off'
            # '&style=feature:landscape.man_made|visibility:on|element:geometry.stroke|color:0xff0000'
            '&style=feature:landscape.man_made|element:geometry.stroke'
            '&style=feature:road|visibility:on|element:geometry'
            '&style=feature:water|element:geometry|color:0x0000ff'
        ).content)
        satOutput.close()
    except ExitError:
        print("Something terrible happened.")

    try:
        satImage = cv2.imread("output_roads.png", cv2.IMREAD_GRAYSCALE)
    except ExitError:
        print("Couldn't open the map image.")

    img = cv2.imread("output_roads.png", 0)
    ret, thresh = cv2.threshold(img, 127, 255, 0)
    im2, contours, hierarchy = cv2.findContours(thresh, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)

    for i in range(len(contours)):
        contours[i] = cv2.approxPolyDP(contours[i], eps, True)  # Ramer–Douglas–Peucker_algorithm
    #cv2.imshow("Map With Contours Added (" + str(latitude) + ',' + str(longitude) + ")", satImage)
    #cv2.waitKey()

    return contours, hierarchy

    # M = cv2.moments(contours[0])
    # cX = int(M["m10"] / M["m00"])/10
    # cY = int(M["m01"] / M["m00"])/10


def create_plane():
    realpath = os.path.expanduser('~/PycharmProjects/diploma/output_landscape.png')
    try:
        img = bpy.data.images.load(realpath)
    except:
        raise NameError("Cannot load image output_landscape.png")
    # Create image texture from image
    cTex = bpy.data.textures.new('ColorTex', type='IMAGE')
    cTex.image = img

    # Create procedural texture
    sTex = bpy.data.textures.new('BumpTex', type='STUCCI')
    sTex.noise_basis = 'BLENDER_ORIGINAL'
    sTex.noise_scale = 0.25
    sTex.noise_type = 'SOFT_NOISE'
    sTex.saturation = 1
    sTex.stucci_type = 'PLASTIC'
    sTex.turbulence = 5

    # Create blend texture with color ramp
    # Don't know how to add elements to ramp, so only two for now
    bTex = bpy.data.textures.new('BlendTex', type='BLEND')
    bTex.progression = 'SPHERICAL'
    bTex.use_color_ramp = True
    ramp = bTex.color_ramp
    values = [(0.6, (1, 1, 1, 1)), (0.8, (0, 0, 0, 1))]
    for n, value in enumerate(values):
        elt = ramp.elements[n]
        (pos, color) = value
        elt.position = pos
        elt.color = color

    # Create material
    mat = bpy.data.materials.new('TexMat')

    # Add texture slot for color texture
    mtex = mat.texture_slots.add()
    mtex.texture = cTex
    mtex.texture_coords = 'UV'
    mtex.use_map_color_diffuse = True
    mtex.use_map_color_emission = True
    mtex.emission_color_factor = 0.5
    mtex.use_map_density = True
    mtex.mapping = 'FLAT'

    # # Add texture slot for bump texture
    # mtex = mat.texture_slots.add()
    # mtex.texture = sTex
    # mtex.texture_coords = 'ORCO'
    # mtex.use_map_color_diffuse = False
    # mtex.use_map_normal = True
    # # mtex.rgb_to_intensity = True
    #
    # # Add texture slot
    # mtex = mat.texture_slots.add()
    # mtex.texture = bTex
    # mtex.texture_coords = 'UV'
    # mtex.use_map_color_diffuse = True
    # mtex.diffuse_color_factor = 1.0
    # mtex.blend_type = 'MULTIPLY'

    # Create plane
    bpy.ops.mesh.primitive_plane_add(radius=640/10, location=(0, 0, 0))
    bpy.ops.uv.smart_project()
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.context.object.rotation_euler[2] = 1.5708

    

    # Add material to current object
    ob = bpy.context.object
    me = ob.data
    me.materials.append(mat)

    return


def create_base(context, contours, height):
    bm = bmesh.new()
    print(len(contours))
    for cnt in contours:
        print(cnt)
        bm_verts = []
        if (len(cnt) > 2):
            for point in range(len(cnt)):
                bm_verts.append(bm.verts.new(((cnt[point][0][0] - 320) / 5, (cnt[point][0][1] - 320) / 5, 0)))
            bm.faces.new(bm_verts)
    me = bpy.data.meshes.new(name='base_mesh')
    ob = bpy.data.objects.new(name='base_object', object_data=me)
    faces = bm.faces[:]
    for face in faces:
        r = bmesh.ops.extrude_discrete_faces(bm, faces=[face])
        bmesh.ops.translate(bm, vec=((0, 0, height)), verts=r['faces'][0].verts)
    bm.to_mesh(ob.data)
    context.scene.objects.link(ob)


def create_road_t(context, contours, hierarchy):
    bm = bmesh.new()
    bmc = bmesh.new()
    #screen = bpy.context.active_object
    print(len(contours))
    for cnt in contours:
        print(cnt)
        bm_verts = []
        bm_verts_children = []
        if (len(cnt) > 2):
            for point in range(len(cnt)):
                bm_verts.append(bm.verts.new(((cnt[point][0][0] - 320) / 5, (cnt[point][0][1] - 320) / 5, 0)))
                if (hierarchy[0][point][3] != -1):
                    bm_verts_children.append(bm.verts.new(((cnt[point][0][0] - 320) / 5, (cnt[point][0][1] - 320) / 5, 0)))
            bm.faces.new(bm_verts)
            bmc.faces.new(bm_verts_children)
    me = bpy.data.meshes.new(name='road_mesh')
    mec = bpy.data.meshes.new(name='roadc_mesh')
    ob = bpy.data.objects.new(name='road_object', object_data=me)
    obc = bpy.data.objects.new(name='roadc_object', object_data=mec)
    bm.to_mesh(ob.data)
    bmc.to_mesh(obc.data)
    context.scene.objects.link(ob)
    context.scene.objects.link(obc)

    bpy.ops.object.select_all(action='DESELECT')
    ob.select = True  # this doesn't matter, the active object does
    bpy.context.scene.objects.active = ob

    # bpy.context.space_data.context = 'MODIFIER'
    bpy.ops.object.modifier_add(type='BOOLEAN')
    bpy.context.object.modifiers["Boolean"].operation = 'DIFFERENCE'
    bpy.context.object.modifiers["Boolean"].object = obc  # Hey! Use this to cut the hole please!!
    bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Boolean")
    bpy.ops.object.select_all(action='DESELECT')


def create_road(context, contours, hierarchy):
    bm = bmesh.new()
    print(len(contours))
    for cnt in contours:
        print(cnt)
        bm_verts = []
        if (len(cnt) > 2):
            for point in range(len(cnt)):
                bm_verts.append(bm.verts.new(((cnt[point][0][0] - 320) / 5, (cnt[point][0][1] - 320) / 5, 0)))
            bm.faces.new(bm_verts)
    me = bpy.data.meshes.new(name='base_mesh')
    ob = bpy.data.objects.new(name='base_object', object_data=me)
    bm.to_mesh(ob.data)
    context.scene.objects.link(ob)

    bm2 = bmesh.new()
    print(len(contours))
    i = 0
    for cnt in contours:
        print(cnt)
        bm2_verts = []
        if (len(cnt) > 2) and (hierarchy[0][i][3] != -1):
            for point in range(len(cnt)):
                bm2_verts.append(bm2.verts.new(((cnt[point][0][0] - 320) / 5, (cnt[point][0][1] - 320) / 5, 0)))
            bm2.faces.new(bm2_verts)
        i+=1
    me2 = bpy.data.meshes.new(name='base_mesh2')
    ob2 = bpy.data.objects.new(name='base_object2', object_data=me2)
    bm2.to_mesh(ob.data)
    context.scene.objects.link(ob2)

    bpy.ops.object.select_all(action='DESELECT')
    ob.select = True  # this doesn't matter, the active object does
    bpy.context.scene.objects.active = ob

    # bpy.context.space_data.context = 'MODIFIER'
    bpy.ops.object.modifier_add(type='BOOLEAN')
    bpy.context.object.modifiers["Boolean"].operation = "DIFFERENCE"
    bpy.context.object.modifiers["Boolean"].object = ob2  # Hey! Use this to cut the hole please!!
    bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Boolean")
    bpy.ops.object.select_all(action='DESELECT')


def create_city(latitude=59.8702089,
                longitude=29.8649487,
                zoom=16,
                eps=2,
                height=5,
                plane = False,
                base = False,
                road = False):
    if plane:
        create_plane()
    if base:
        contours_base = gmaps_buildings(latitude, longitude, zoom, eps)
        create_base(bpy.context, contours_base, height)
    if road:
        contours_road, hierarchy_road = gmaps_roads(latitude, longitude, zoom, eps)
        create_road(bpy.context, contours_road, hierarchy_road)


# create_city(59.8702089, 29.8649487, 16, 2, True, True, True)
