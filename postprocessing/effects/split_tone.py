
import math
import arcade
from postprocessing.post_effect import PostEffect

try:
    import imgui
    import imgui.core
except:
    pass


#Basic Split tone shader with the following arguments:

#threshold-> (Default 0.5) The middle point between shadows and highlights 0.0->1.0 for LDR, 0.0->A LOT(brightest light in scene) for HDR
#Crossover-> (Defualt 0.05) The sizeof the band where the 2 colors are blended between, this value indicates the total length in brightness for this band. 
#shadow_color-> (Default (0.0,0.0,0.0)) The color to add to shadows (or subtract if this is negative)
#highlight_color-> (Default (0.0,0.0,0.0)) The color to add to highlights (or subtract if this is negative)
#NOTE: Values can be HDR if this stage runs before tonemapping
class SplitTone(PostEffect):

    def __init__(self, context, window_size):
        super().__init__(context, window_size)

        self.program = context.load_program(
            vertex_shader="postprocessing/core_shaders/fullscreen_quad.vs",
            fragment_shader="postprocessing/effects/shaders/split_tone.fs",
        )
        self.program['t_source'] = 0

        self.threshold = 0.5
        self.crossover = 0.05
        self.shadow_color = (0.0,0.0,0.0)
        self.highlight_color = (0.0,0.0,0.0)

    @property
    def threshold(self):
        return self._threshold

    @threshold.setter
    def threshold(self,value):
        self._threshold = value
        self.program['u_threshold'] = value

    @property
    def crossover(self):
        return self._crossover

    @crossover.setter
    def crossover(self,value):
        value = max(0.0, value)
        self._crossover = value
        self.program['u_crossover_half'] = value * 0.5

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
        self.threshold = imgui.slider_float(f'Threshold##{self.ui_index}', self.threshold, 0.0, 10.0)[1]
        self.crossover = imgui.slider_float(f'Crossover##{self.ui_index}', self.crossover, 0.0, 2.0)[1]
        self.shadow_color = imgui.color_edit3(f'Shadow Color##{self.ui_index}', *self.shadow_color)[1]
        self.highlight_color = imgui.color_edit3(f'Highlight Color##{self.ui_index}', *self.highlight_color)[1]
       