"""

This is a aracde demo adapted to work with this post-procesisng library
You can find the original demo code here https://arcade.academy/examples/sprite_bouncing_coins.html#sprite-bouncing-coins 

Sprite Simple Bouncing

Simple program to show how to bounce items.
This only works for straight vertical and horizontal angles.

Artwork from http://kenney.nl

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.sprite_bouncing_coins
"""

import arcade
import os
import random

from postprocessing.post_processing_chain import PostProcessingChain
from postprocessing.render_target import RenderTarget

from postprocessing.effects.vignette import Vignette
from postprocessing.effects.greyscale import GreyScale
from postprocessing.effects.bloom import Bloom
from postprocessing.effects.tonemap import Tonemap
from postprocessing.effects.split_tone import SplitTone
from postprocessing.effects.good_chromatic_abberation import GoodChromaticAberration


from typing import Iterable, Iterator
from typing import Any
from typing import TypeVar
from typing import List
from typing import Tuple
from typing import Optional
from typing import Union

import logging
import math
import array
import time

from PIL import Image

from arcade import Color
from arcade import Matrix3x3
from arcade import Sprite
from arcade import get_distance_between_sprites
from arcade import are_polygons_intersecting
from arcade import is_point_in_polygon

from arcade import rotate_point
from arcade import get_window
from arcade import Point
from arcade import gl

import imgui
import imgui.core

from arcade_imgui import ArcadeRenderer
from arcade_imgui import ArcadeGLRenderer

SPRITE_SCALING = 0.5

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 632
SCREEN_TITLE = "Sprite Bouncing Coins"

MOVEMENT_SPEED = 5

#patch class to allow for additive blending in spritelist.draw
def draw_additive(self, **kwargs):
    """
    Draw this list of sprites.

    :param filter: Optional parameter to set OpenGL filter, such as
                    `gl.GL_NEAREST` to avoid smoothing.
    """
    if len(self.sprite_list) == 0:
        return

    # What percent of this sprite list moved? Used in guessing spatial hashing
    self._percent_sprites_moved = self._sprites_moved / len(self.sprite_list) * 100
    self._sprites_moved = 0

    # Make sure window context exists
    if self.ctx is None:
        self.ctx = get_window().ctx
        # Used in drawing optimization via OpenGL
        self.program = self.ctx.sprite_list_program_cull

    if self._vao1 is None:
        self._calculate_sprite_buffer()

    self.ctx.enable(self.ctx.BLEND)
    self.ctx.blend_func = self.ctx.BLEND_ADDITIVE

    self._texture.use(0)

    if "filter" in kwargs:
        self._texture.filter = self.ctx.NEAREST, self.ctx.NEAREST

    self.program['Texture'] = self.texture_id

    texture_transform = None
    if len(self.sprite_list) > 0:
        # always wrap texture transformations with translations
        # so that rotate and resize operations act on the texture
        # center by default
        texture_transform = Matrix3x3().translate(-0.5, -0.5).multiply(self.sprite_list[0].texture_transform.v).multiply(Matrix3x3().translate(0.5, 0.5).v)
    else:
        texture_transform = Matrix3x3()
    self.program['TextureTransform'] = texture_transform.v

    if not self.is_static:
        if self._sprite_pos_changed:
            self._sprite_pos_buf.orphan()
            self._sprite_pos_buf.write(self._sprite_pos_data)
            self._sprite_pos_changed = False

        if self._sprite_size_changed:
            self._sprite_size_buf.orphan()
            self._sprite_size_buf.write(self._sprite_size_data)
            self._sprite_size_changed = False

        if self._sprite_angle_changed:
            self._sprite_angle_buf.orphan()
            self._sprite_angle_buf.write(self._sprite_angle_data)
            self._sprite_angle_changed = False

        if self._sprite_color_changed:
            self._sprite_color_buf.orphan()
            self._sprite_color_buf.write(self._sprite_color_data)
            self._sprite_color_changed = False

        if self._sprite_sub_tex_changed:
            self._sprite_sub_tex_buf.orphan()
            self._sprite_sub_tex_buf.write(self._sprite_sub_tex_data)
            self._sprite_sub_tex_changed = False

    self._vao1.render(self.program, mode=self.ctx.POINTS, vertices=len(self.sprite_list))

arcade.SpriteList.draw_additive = draw_additive

class MyGame(arcade.Window):
    """ Main application class. """

    def __init__(self, width, height, title):
        """
        Initializer
        """
        super().__init__(width, height, title)

        # Set the working directory (where we expect to find files) to the same
        # directory this .py file is in. You can leave this out of your own
        # code, but it is needed to easily run the examples using "python -m"
        # as mentioned at the top of this program.
        file_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(file_path)

        # Sprite lists
        self.coin_list = None
        self.wall_list = None

        # Must create or set the context before instantiating the renderer
        imgui.create_context()
        self.renderer = ArcadeRenderer(self)

    def setup(self):
        """ Set up the game and initialize the variables. """

        # Sprite lists
        self.wall_list = arcade.SpriteList()
        self.coin_list = arcade.SpriteList()

        # -- Set up the walls

        # Create horizontal rows of boxes
        for x in range(32, SCREEN_WIDTH, 64):
            # Bottom edge
            wall = arcade.Sprite(":resources:images/tiles/boxCrate_double.png", SPRITE_SCALING)
            wall.center_x = x
            wall.center_y = 32
            self.wall_list.append(wall)

            # Top edge
            wall = arcade.Sprite(":resources:images/tiles/boxCrate_double.png", SPRITE_SCALING)
            wall.center_x = x
            wall.center_y = SCREEN_HEIGHT - 32
            self.wall_list.append(wall)

        # Create vertical columns of boxes
        for y in range(96, SCREEN_HEIGHT, 64):
            # Left
            wall = arcade.Sprite(":resources:images/tiles/boxCrate_double.png", SPRITE_SCALING)
            wall.center_x = 32
            wall.center_y = y
            self.wall_list.append(wall)

            # Right
            wall = arcade.Sprite(":resources:images/tiles/boxCrate_double.png", SPRITE_SCALING)
            wall.center_x = SCREEN_WIDTH - 32
            wall.center_y = y
            self.wall_list.append(wall)

        # Create boxes in the middle
        for x in range(128, SCREEN_WIDTH, 196):
            for y in range(128, SCREEN_HEIGHT, 196):
                wall = arcade.Sprite(":resources:images/tiles/boxCrate_double.png", SPRITE_SCALING)
                wall.center_x = x
                wall.center_y = y
                # wall.angle = 45
                self.wall_list.append(wall)

        # Create coins
        for i in range(10):
            coin = arcade.Sprite(":resources:images/items/coinGold.png", 0.25)
            coin.center_x = random.randrange(100, 700)
            coin.center_y = random.randrange(100, 500)
            while coin.change_x == 0 and coin.change_y == 0:
                coin.change_x = random.randrange(-4, 5)
                coin.change_y = random.randrange(-4, 5)

            self.coin_list.append(coin)

        # Set the background color
        arcade.set_background_color(arcade.color.AMAZON)

        #setup post processing
        self.setup_post_processing()

    def setup_post_processing(self):
        #Create a new post-processing chain, this will automatically resize with anything you render through it
        self.post_processing = PostProcessingChain(self.ctx, self.get_size(), True)

        #Allocate and add effects

        #Not sure about this method of allocating a object / weird implicit factory thing

        self.bloom = self.post_processing.add_effect(Bloom)
        self.bloom.threshold = 0.9
        self.bloom.power = 1.0

        self.tonemap = self.post_processing.add_effect(Tonemap)
        self.tonemap.threshold = 2.0

        self.chromatic = self.post_processing.add_effect(GoodChromaticAberration)
        self.chromatic.axial = 1.0
        self.chromatic.distance_scale = 0.003

        self.greyscale = self.post_processing.add_effect(GreyScale)
        self.greyscale.strength = 0.5

        self.split_tone = self.post_processing.add_effect(SplitTone)

        self.vignette = self.post_processing.add_effect(Vignette)
        self.vignette.inner_distance = 0.1

        size = self.get_size()
        self.render_target = RenderTarget(self.ctx, size, 'f2')

    def on_draw(self):
        """
        Render the screen.
        """

        # This command has to happen before we start drawing
        arcade.start_render()

        #Draw to a render target instead of the screen
        self.render_target.bind_as_framebuffer()
        self.render_target.framebuffer_object.clear(arcade.color.AMAZON)

        # Draw all the sprites.
        self.wall_list.draw()
        self.coin_list.draw()

        #Draw coin list again additivly for HDR related reasons
        self.ctx.enable_only(self.ctx.BLEND)
        self.ctx.blend_func = self.ctx.BLEND_ADDITIVE

        self.coin_list.draw_additive()



        #Apply the post processing effect chain to the render target, and apply it to the screen
        self.post_processing.apply_effects(self.render_target.texture, self.ctx.screen)

        self.draw_gui()

    def draw_gui(self):
        imgui.new_frame()

        self.post_processing.show_postprocess_ui()
     
        imgui.render()
        self.renderer.render(imgui.get_draw_data())

    def on_update(self, delta_time):
        """ Movement and game logic """

        for coin in self.coin_list:

            coin.center_x += coin.change_x
            walls_hit = arcade.check_for_collision_with_list(coin, self.wall_list)
            for wall in walls_hit:
                if coin.change_x > 0:
                    coin.right = wall.left
                elif coin.change_x < 0:
                    coin.left = wall.right
            if len(walls_hit) > 0:
                coin.change_x *= -1

            coin.center_y += coin.change_y
            walls_hit = arcade.check_for_collision_with_list(coin, self.wall_list)
            for wall in walls_hit:
                if coin.change_y > 0:
                    coin.top = wall.bottom
                elif coin.change_y < 0:
                    coin.bottom = wall.top
            if len(walls_hit) > 0:
                coin.change_y *= -1


def main():
    """ Main method """
    window = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()