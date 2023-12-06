# Import necessary libraries

import pygame as pg
from OpenGL.GL import *
import numpy as np
import pyrr as rr

from guiV1 import SimpleGUI
from objLoaderV2 import ObjLoader
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


# Setup Uniform Variables
scale_loc = glGetUniformLocation(shader, "scale")
glUniform1f(scale_loc, scale)

center_loc = glGetUniformLocation(shader, "center")
glUniform3fv(center_loc, 1, center)

aspect_loc = glGetUniformLocation(shader, "aspect")
glUniform1f(aspect_loc, aspect)

model_mat_loc = glGetUniformLocation(shader, "model_matrix")  # Get the location of the uniform variable "model_mat" in the shader

# Setup GUI
gui = SimpleGUI("Transformation")
# scale_slider = gui.add_slider("Scale", min_value=0.5*scale, max_value=2.0*scale, initial_value= scale)
# translateY_slider = gui.add_slider("TranslateY", min_value=-1.25, max_value=1.25, initial_value=0)
# translateX_slider = gui.add_slider("TranslateX", min_value=-1.25, max_value=1.25, initial_value=0)

# Rotation Sliders
minDeg = -90
maxDeg = 90
rotateZ_slider = gui.add_slider("RotateZ", min_value=minDeg, max_value=maxDeg, initial_value=0)
rotateY_slider = gui.add_slider("RotateY", min_value=(2*minDeg), max_value=(2*maxDeg), initial_value=0)
rotateX_slider = gui.add_slider("RotateX", min_value=minDeg, max_value=maxDeg, initial_value=0)

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
    rz = np.deg2rad(rotateZ_slider.get_value())
    ry = np.deg2rad(rotateY_slider.get_value())
    rx = np.deg2rad(rotateX_slider.get_value())

    # compute and set the model matrix
    scale_mat = rr.matrix44.create_from_scale([scale, scale, scale])
    # translate_mat2 = rr.matrix44.create_from_translation([tx, ty, tz])
    rotate_matZ = rr.matrix44.create_from_z_rotation(rz)
    rotate_matY = rr.matrix44.create_from_y_rotation(ry)
    rotate_matX = rr.matrix44.create_from_x_rotation(rx)

    # create one matrix for the everything
    model_mat = rr.matrix44.multiply(origin, rotate_matX)   # Bring the model to the origin and rotate by x
    model_mat = rr.matrix44.multiply(model_mat, rotate_matY)
    model_mat = rr.matrix44.multiply(model_mat, rotate_matZ)
    # model_mat = rr.matrix44.multiply(model_mat, translate_mat2)
    model_mat = rr.matrix44.multiply(model_mat, scale_mat)


    glUniformMatrix4fv(model_mat_loc, 1, GL_FALSE, model_mat)   # Set the value of the uniform variable "model_mat" in the shader

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
