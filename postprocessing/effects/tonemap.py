
import arcade
from postprocessing.post_effect import PostEffect
import imgui

#Basic tonemap from HDR -> LDR, currently via the simple Reinhard
class Tonemap(PostEffect):

    def __init__(self, context, window_size):
        super().__init__(context, window_size)

        self.program = context.load_program(
            vertex_shader='postprocessing/core_shaders/fullscreen_quad.vs',
            fragment_shader='postprocessing/effects/shaders/tonemap.fs'
        )
        self.program['t_source'] = 0
    
        self.white_point = 2.0

    def apply(self, render_target_pair):
        render_target_pair.bind(0)
        PostEffect.fullscreen_quad.render(self.program)

    def is_tonemapping_effect(self):
        return True

    @property
    def white_point(self):
        return self._white_point

    @white_point.setter
    def white_point(self, value):
        self._white_point = value
        self.program['u_whitePoint_2'] = value * value


    def show_ui(self):
        super().show_ui()
        self.white_point = imgui.slider_float(f'Threshold##{self.ui_index}', self.white_point, 0.0, 10.0, power=2.0)[1]