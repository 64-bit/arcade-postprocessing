import arcade

class PostEffect:

    fullscreen_quad = None

    def __init__(self,context, window_size):
        self.enabled = True
        self.context = context
        self.window_size = window_size       

        PostEffect._init_quad()

    def _init_quad():
        if PostEffect.fullscreen_quad is None:
            PostEffect.fullscreen_quad = arcade.gl.geometry.quad_2d_fs()

    def resize(self, newSize):
        self.window_size = newSize


    def apply(self, render_target_pair):
         raise NotImplementedError("This method must be implemented by a derrived class")

    #An effect that tonemaps HDR to LDR and marks the end of the HDR side of the post-processing
    #pipeline should override this and return true
    def is_tonemapping_effect(self):
        return False
       