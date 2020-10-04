
import math
import arcade
from postprocessing.post_effect import PostEffect

try:
    import imgui
    import imgui.core
except:
    pass

class Tempalte(PostEffect):

    def __init__(self, context, window_size):
        super().__init__(context, window_size)

        self.program = context.load_program(
            vertex_shader="postprocessing/core_shaders/fullscreen_quad.vs",
            fragment_shader="postprocessing/effects/shaders/template.fs",
        )
        self.program['t_source'] = 0

    def apply(self, render_target_pair):
        render_target_pair.bind(0)
        PostEffect.fullscreen_quad.render(self.program)

    def show_ui(self):
        super().show_ui()
        pass
       