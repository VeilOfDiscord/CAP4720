# Import necessary libraries
import time

import pygame as pg
from OpenGL.GL import *
import numpy as np
import pyrr as rr

from guiV1 import SimpleGUI
from objLoaderV3 import ObjLoader
import shaderLoader

# Initialize pygame
pg.init()

# Set up OpenGL context version
pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, 3)
pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, 3)

# Create a window for graphics using OpenGL
width = 800
height = 800
pg.display.set_mode((width, height), pg.OPENGL | pg.DOUBLEBUF)


glClearColor(0.16, 0.19, 0.23, 2.0)
glEnable(GL_DEPTH_TEST)

shader = shaderLoader.compile_shader("shaders/vert.glsl", "shaders/frag.glsl")
glUseProgram(shader)

# Lets setup our scene geometry.
obj = ObjLoader("objects/raymanModel.obj")
vertices = np.array(obj.vertices, dtype="float32")
center = obj.center
dia = obj.dia

size_position = 3  # x,y,z
size_texture = 2   # u,v
size_normal = 3    # r, g, b

stride = (size_position + size_texture + size_normal) * 4
offset_position = 0
offset_texture = size_position * 4
offset_normal = (size_position + size_texture) * 4
n_vertices = len(obj.vertices) // (size_position + size_texture + size_normal)

scale = (2.0 / dia)
aspect = width / height

origin = rr.matrix44.create_from_translation(-center)

translation_mat = rr.matrix44.create_from_translation(-center)
scale_mat = rr.matrix44.create_from_scale([scale, scale, scale])
model_mat = rr.matrix44.multiply(translation_mat, scale_mat)

fov = 60           # field of view
near = 0.1          # near plane
far = 100           # far plane

camera_speed = 100

view_mat = rr.matrix44.create_look_at(eye=(0, 0, 2), target=(0,0,0), up=(0, 1, 0))
projection_mat = rr.matrix44.create_perspective_projection_matrix(fov, aspect, near, far)

vao = glGenVertexArrays(1)
glBindVertexArray(vao)

vbo = glGenBuffers(1)
glBindBuffer(GL_ARRAY_BUFFER, vbo)
glBufferData(GL_ARRAY_BUFFER,
             size=obj.vertices.nbytes,
             data=obj.vertices,
             usage=GL_STATIC_DRAW)

position_loc = glGetAttribLocation(shader, "position")
glVertexAttribPointer(index=position_loc,
                      size=size_position,
                      type=GL_FLOAT,
                      normalized=GL_FALSE,
                      stride=stride,
                      pointer=ctypes.c_void_p(offset_position))
glEnableVertexAttribArray(position_loc)

normal_loc = glGetAttribLocation(shader, "normal")
glVertexAttribPointer(index=normal_loc,
                      size=size_normal,
                      type=GL_FLOAT,
                      normalized=GL_FALSE,
                      stride=stride,
                      pointer=ctypes.c_void_p(offset_normal))
glEnableVertexAttribArray(normal_loc)

model_mat_loc = glGetUniformLocation(shader, "model_matrix")
glUniformMatrix4fv(model_mat_loc, 1, GL_FALSE, model_mat)

view_mat_loc = glGetUniformLocation(shader, "view_matrix")

projection_mat_loc = glGetUniformLocation(shader, "projection_matrix")
glUniformMatrix4fv(projection_mat_loc, 1, GL_FALSE, projection_mat)

gui = SimpleGUI("Camera Controls")
fov_slider = gui.add_slider("FOV", min_value=30, max_value=110, initial_value=90)

minDeg = -90
maxDeg = 90
rotateY_slider = gui.add_slider("Y-axis", min_value=2*minDeg, max_value=2*maxDeg, initial_value=0)
rotateX_slider = gui.add_slider("X-axis", min_value=minDeg, max_value=maxDeg, initial_value=0)

# Run a loop to keep the program running
draw = True
while draw:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            draw = False

    # Clear color buffer and depth buffer before drawing each frame
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    # scaling
    # scale = scale_slider.get_value()

    # tx = translateX_slider.get_value()
    # ty = translateY_slider.get_value()
    # tz = 0

    # rotations
    # rz = np.deg2rad(rotateZ_slider.get_value())
    # ry = np.deg2rad(rotateY_slider.get_value())
    # rx = np.deg2rad(rotateX_slider.get_value())
    #
    # # compute and set the model matrix
    # scale_mat = rr.matrix44.create_from_scale([scale, scale, scale])
    # # translate_mat2 = rr.matrix44.create_from_translation([tx, ty, tz])
    # rotate_matZ = rr.matrix44.create_from_z_rotation(rz)
    # rotate_matY = rr.matrix44.create_from_y_rotation(ry)
    # rotate_matX = rr.matrix44.create_from_x_rotation(rx)
    #
    # # create one matrix for the everything
    # model_mat = rr.matrix44.multiply(origin, rotate_matX)   # Bring the model to the origin and rotate by x
    # model_mat = rr.matrix44.multiply(model_mat, rotate_matY)
    # model_mat = rr.matrix44.multiply(model_mat, rotate_matZ)
    # # model_mat = rr.matrix44.multiply(model_mat, translate_mat2)
    # model_mat = rr.matrix44.multiply(model_mat, scale_mat)

    degY = rotateY_slider.get_value()
    rotY_mat = rr.matrix44.create_from_y_rotation(np.deg2rad(degY))
    degX = rotateX_slider.get_value()
    rotX_mat = rr.matrix44.create_from_x_rotation(np.deg2rad(degX))

    rotation_mat = rr.matrix44.multiply(rotX_mat, rotY_mat)

    transformed_eye = (0, 0, 2) - obj.center

    rotated_eye = rr.matrix44.apply_to_vector(rotation_mat, transformed_eye)
    transformed_eye = rotated_eye + obj.center

    view_mat = rr.matrix44.create_look_at(rotated_eye, (0,0,0), [0, 1, 0])
    glUniformMatrix4fv(view_mat_loc, 1, GL_FALSE, view_mat)

    # Draw
    glUseProgram(shader)
    glBindVertexArray(vao)
    glDrawArrays(GL_TRIANGLES,
                 0,
                 n_vertices)

    # Refresh the display to show what's been drawn
    pg.display.flip()

# Cleanup
glDeleteVertexArrays(1, [vao])
glDeleteBuffers(1, [vbo])
glDeleteProgram(shader)

pg.quit()  # Close the graphics window
quit()  # Exit the program
