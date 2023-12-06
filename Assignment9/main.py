# Import necessary libraries
import pygame as pg
from OpenGL.GL import *
import numpy as np
from utils import load_image
from utils import load_cubemap_texture

from guiV3 import SimpleGUI
from objLoaderV4 import ObjLoader
import shaderLoaderV3
import pyrr

# Initialize pygame
pg.init()

# Set up OpenGL context version
pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, 3)
pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, 3)

# Create a window for graphics using OpenGL
width = 800
height = 800
pg.display.set_mode((width, height), pg.OPENGL | pg.DOUBLEBUF)


glClearColor(0.3, 0.4, 0.5, 1.0)
glEnable(GL_DEPTH_TEST)


# Write our shaders. We will write our vertex shader and fragment shader in a different file
shaderProgram = shaderLoaderV3.ShaderProgram("shaders/vert.glsl", "shaders/frag.glsl")
shaderProgram_skybox = shaderLoaderV3.ShaderProgram("shaders/skybox/vert_skybox.glsl", "shaders/skybox/frag_skybox.glsl")

# Camera parameters
eye = (0,0,4)
target = (0,0,0)
up = (0,1,0)

fov = 45
aspect = width/height
near = 0.1
far = 10

view_mat = pyrr.matrix44.create_look_at(eye, target, up)
projection_mat = pyrr.matrix44.create_perspective_projection_matrix(fov, aspect, near, far)


# Lets load our objects
obj = ObjLoader("objects/stormtrooper/stormtrooper.obj")


# *********** Lets define the model matrix ***********
translation_mat = pyrr.matrix44.create_from_translation(-obj.center)

scaling_mat = pyrr.matrix44.create_from_scale([2 / obj.dia, 2 / obj.dia, 2 / obj.dia])

model_mat = pyrr.matrix44.multiply(translation_mat, scaling_mat)

# ***** Create VAO, VBO, and configure vertex attributes for object 1 *****
# VAO
vao = glGenVertexArrays(1)
glBindVertexArray(vao)

# VBO
vbo = glGenBuffers(1)
glBindBuffer(GL_ARRAY_BUFFER, vbo)
glBufferData(GL_ARRAY_BUFFER, obj.vertices.nbytes, obj.vertices, GL_STATIC_DRAW)

# Configure vertex attributes for object
position_loc = glGetAttribLocation(shaderProgram.shader, "position")
glVertexAttribPointer(position_loc, obj.size_position, GL_FLOAT, GL_FALSE, obj.stride, ctypes.c_void_p(obj.offset_position))
glEnableVertexAttribArray(position_loc)

# texture attribute
texture_loc = 1
glBindAttribLocation(shaderProgram.shader, texture_loc, "uv")
glVertexAttribPointer(texture_loc, obj.size_texture, GL_FLOAT, GL_FALSE, obj.stride, ctypes.c_void_p(obj.offset_texture))
glEnableVertexAttribArray(texture_loc)

normal_loc = glGetAttribLocation(shaderProgram.shader, "normal")
glVertexAttribPointer(normal_loc, obj.size_normal, GL_FLOAT, GL_FALSE, obj.stride, ctypes.c_void_p(obj.offset_normal))
glEnableVertexAttribArray(normal_loc)

# # Set up for skybox
quad_vertices = (
            # Position
            -1, -1,
             1, -1,
             1,  1,
             1,  1,
            -1,  1,
            -1, -1
)
vertices = np.array(quad_vertices, dtype=np.float32)

size_position = 2       # x, y, z
stride = size_position * 4
offset_position = 0
quad_n_vertices = len(vertices) // size_position  # number of vertices

# Create VA0 and VBO
vao_quad = glGenVertexArrays(1)
glBindVertexArray(vao_quad)            # Bind the VAO. That is, make it the active one.
vbo_quad = glGenBuffers(1)                  # Generate one buffer and store its ID.
glBindBuffer(GL_ARRAY_BUFFER, vbo_quad)     # Bind the buffer. That is, make it the active one.
glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)   # Upload the data to the GPU.

position_loc = 0
glBindAttribLocation(shaderProgram_skybox.shader, position_loc, "position")
glVertexAttribPointer(position_loc, size_position, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(offset_position))
glEnableVertexAttribArray(position_loc)

# Load cubemap
cubemap_images = ["objects/skybox/right.png", "objects/skybox/left.png",
                  "objects/skybox/top.png", "objects/skybox/bottom.png",
                  "objects/skybox/front.png", "objects/skybox/back.png"]
cubemap_id = load_cubemap_texture(cubemap_images)



# Load our texture image
img_data, img_width, img_height = load_image("objects/stormtrooper/stormtrooper.jpg")


# Create a texture object
texture_id = glGenTextures(1)
glBindTexture(GL_TEXTURE_2D, texture_id)        # Bind the texture object. That is, make it the active one.
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)    # Set the texture wrapping parameters
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)    # Set texture filtering parameters
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, img_width, img_height, 0, GL_RGB, GL_UNSIGNED_BYTE, img_data)

shaderProgram["tex2D"] = 0
shaderProgram["cubeMapTex"] = 1

# *************************************************************************

gui = SimpleGUI("Assignment 9 - Textures")

# Create a slider for the rotation angle around the Z axis
camera_rotY_slider = gui.add_slider("camera Y angle", -180, 180, 0, resolution=1)
camera_rotX_slider = gui.add_slider("camera X angle", -90, 90, 0, resolution=1)
fov_slider = gui.add_slider("fov", 5, 90, 25, resolution=1)

text_type_radio_buttons = gui.add_radio_buttons("Texture Type:", options_dict={"Environment Mapping": 1,
                                                                               "Texture Mapping": 2, "Mix": 3},
                                                initial_option="Texture Mapping")



# Run a loop to keep the program running
draw = True
while draw:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            draw = False

    # Clear color buffer and depth buffer before drawing each frame
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    rotateY_mat = pyrr.matrix44.create_from_y_rotation(np.deg2rad(camera_rotY_slider.get_value()))
    rotateX_mat = pyrr.matrix44.create_from_x_rotation(np.deg2rad(camera_rotX_slider.get_value()))
    rotation_mat = pyrr.matrix44.multiply(rotateX_mat, rotateY_mat)
    rotated_eye = pyrr.matrix44.apply_to_vector(rotation_mat, eye)

    view_mat = pyrr.matrix44.create_look_at(rotated_eye, target, up)
    projection_mat = pyrr.matrix44.create_perspective_projection_matrix(fov_slider.get_value(),
                                                                        aspect, near,  far)
    text_val = int(text_type_radio_buttons.get_value())

    view_mat_without_translation = view_mat.copy()
    view_mat_without_translation[3][:3] = [0,0,0]
    inverseViewProjection_mat = pyrr.matrix44.inverse(pyrr.matrix44.multiply(view_mat_without_translation,projection_mat))


    # Set uniforms for diffuse material
    shaderProgram["model_matrix"] = model_mat
    shaderProgram["view_matrix"] = view_mat
    shaderProgram["projection_matrix"] = projection_mat
    shaderProgram["eye_pos"] = rotated_eye
    shaderProgram["text_type"] = text_val

    glUseProgram(shaderProgram.shader)

    glActiveTexture(GL_TEXTURE0)
    glBindTexture(GL_TEXTURE_2D, texture_id)

    glActiveTexture(GL_TEXTURE1)
    glBindTexture(GL_TEXTURE_CUBE_MAP, cubemap_id)

    glBindVertexArray(vao)
    glDrawArrays(GL_TRIANGLES,0, obj.n_vertices)      # draw the object

    # ******************* Draw the skybox ************************
    glDepthFunc(GL_LEQUAL)  # Change depth function so depth test passes when values are equal to depth buffer's content
    glUseProgram(shaderProgram_skybox.shader)  # being explicit even though the line below will call this function
    shaderProgram_skybox["invViewProjectionMatrix"] = inverseViewProjection_mat
    glBindVertexArray(vao_quad)
    glDrawArrays(GL_TRIANGLES,
                 0,
                 quad_n_vertices)  # Draw the triangle
    glDepthFunc(GL_LESS)  # Set depth function back to default
    # *************************************************************

    # Refresh the display to show what's been drawn
    pg.display.flip()


# Cleanup
glDeleteVertexArrays(1, [vao, vao_quad])
glDeleteBuffers(1, [vbo, vbo_quad])

glDeleteProgram(shaderProgram.shader)
glDeleteProgram(shaderProgram_skybox.shader)

pg.quit()   # Close the graphics window
quit()      # Exit the program