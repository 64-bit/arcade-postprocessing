import arcade
from postprocessing.post_effect import PostEffect

try:
    import imgui
    import imgui.core
except:
    pass

class Vignette(PostEffect):

    def __init__(self, context, window_size):
        super().__init__(context, window_size)

        self.program = context.load_program(
            vertex_shader="postprocessing/core_shaders/fullscreen_quad.vs",
            fragment_shader="postprocessing/effects/shaders/vignette.fs",
        )

        self.program["t_source"] = 0

        self.inner_distance = 1.0
        self.outer_distance = 2.0
        self.color = (0.0, 0.0, 0.0, 1.0)

    def apply(self, render_target_pair):
        render_target_pair.bind(0)
        PostEffect.fullscreen_quad.render(self.program)

    @property
    def outer_distance(self):
        return self._outer_distance

    @outer_distance.setter
    def outer_distance(self, value):
        self._outer_distance = value
        self.program["u_outer_distance"] = value

    @property
    def inner_distance(self):
        return self._inner_distance

    @inner_distance.setter
    def inner_distance(self, value):
        self._inner_distance = value
        self.program["u_inner_distance"] = value

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, value):
        self._color = value
        self.program["u_color"] = value

    def show_ui(self):
        super().show_ui()

        self.inner_distance = imgui.slider_float(f'Start Distance##{self.ui_index}', self.inner_distance, -1.0, 3.0)[1]
        self.outer_distance = imgui.slider_float(f'End Distance##{self.ui_index}', self.outer_distance, -1.0, 3.0)[1]
        #self.strength = imgui.slider_float(f'Strength##{self.ui_index}', self.strength, 0.0, 2.0)[1]
        #self.scale = imgui.slider_float2(f'Scale##{self.ui_index}', self._scale[0], self._scale[1], 0.0,4.0)[1]

        self.color = imgui.color_edit4(f'Color##{self.ui_index}', *self.color)[1]
