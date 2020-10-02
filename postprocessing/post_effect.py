import arcade

class PostEffect:

    fullscreen_quad = None

    def __init__(self):
        self.enabled = True
        PostEffect._init_quad()

    def on_add(self, context, window_size):
        self.context = context
        self.window_size = window_size       

    def _init_quad():
        if PostEffect.fullscreen_quad is None:
            PostEffect.fullscreen_quad = arcade.gl.geometry.quad_2d_fs()

    def resize(self, newSize):
        self.window_size = newSize


    def apply(self, render_target_pair):
         raise NotImplementedError("This method must be implemented by a derrived class")
       