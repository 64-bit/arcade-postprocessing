
import math
import arcade
from postprocessing.post_effect import PostEffect

try:
    import imgui
    import imgui.core
except:
    pass
class GreyScale(PostEffect):

    def __init__(self, context, window_size):
        super().__init__(context, window_size)

        self.program = context.load_program(
            vertex_shader="postprocessing/core_shaders/fullscreen_quad.vs",
            fragment_shader="postprocessing/effects/shaders/greyscale.fs",
        )
        self.program['t_source'] = 0

        self.strength = 1.0
        self.shadow_color = (0.0,0.0,0.0)
        self.highlight_color = (1.0,1.0,1.0)

    @property
    def strength(self):
        return self._strength

    @strength.setter
    def strength(self,value):
        self._strength = value
        self.program['u_strength'] = value

    @property
    def shadow_color(self):
        return self._shadow_color

    @shadow_color.setter
    def shadow_color(self,value):
        self._shadow_color = value
        self.program['u_shadow_color'] = value

    @property
    def highlight_color(self):
        return self._highlight_color

    @highlight_color.setter
    def highlight_color(self, value):
        self._highlight_color = value
        self.program['u_highlight_color'] = value

    def apply(self, render_target_pair):
        render_target_pair.bind(0)
        PostEffect.fullscreen_quad.render(self.program)

    def show_ui(self):
        super().show_ui()
        self.strength = imgui.slider_float(f'Strength##{self.ui_index}', self.strength, 0.0, 1.0)[1]
        self.shadow_color = imgui.color_edit3(f'Shadow Color##{self.ui_index}', *self.shadow_color)[1]
        self.highlight_color = imgui.color_edit3(f'Highlight Color##{self.ui_index}', *self.highlight_color)[1]
       