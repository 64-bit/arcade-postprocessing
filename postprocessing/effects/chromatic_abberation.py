
import arcade
import imgui
from postprocessing.post_effect import PostEffect

try:
    import imgui
    import imgui.core
except:
    pass

class ChromaticAberration(PostEffect):

    def __init__(self, context, window_size):
        super().__init__(context, window_size)
        self.program = context.load_program(
            vertex_shader="postprocessing/core_shaders/fullscreen_quad.vs",
            fragment_shader="postprocessing/effects/shaders/chromatic_abberation.fs",
        )

        self.program['t_source'] = 0

        self._axial = 0.0
        self._transverse = 0.0

        self.axial = 0.3
        self.transverse = 0.3

        self.distance_scale = 0.01

        newWeights = self.compute_weights(15)

        self.program['u_channel_weights'] = newWeights[0]
        self.program['u_channel_sums'] = newWeights[1]


    def compute_weights(self, count):

        def lerp(x,y, v):
            return (x*(1.0-v)) + y*v

        def clamp(value, min_val, max_val):
            return max(min(value,max_val),min_val)

        #0 = red, 0.5 = green 1 = blue

        weight_sums = [0.0, 0.0, 0.0]
        weights = []

        for x in range(count):
            factor = float(x) / float(count)
            factor *= 2.0

            r = clamp(1.0 - factor , 0.0, 1.0)
            g = clamp(1.0 - abs(factor - 1.0) , 0.0, 1.0)
            b = clamp(factor - 1.0, 0.0, 1.0)

            weights.append(r)
            weights.append(g)
            weights.append(b)

            weight_sums[0] += r
            weight_sums[1] += g
            weight_sums[2] += b

        return (weights, weight_sums)

    def apply(self, render_target_pair):
        render_target_pair.bind(0)
        PostEffect.fullscreen_quad.render(self.program)

    def clamp(value, min_val, max_val):
        return max(min(value,max_val),min_val)

    @property
    def axial(self):
        return self._axial

    @axial.setter
    def axial(self, value):
        self._axial = ChromaticAberration.clamp(value, 0.0, 1.0)
        self.program['u_axial'] = self._axial

        #Ensure that axial + transverse do not sum to more than 1.0
        if self._axial + self.transverse > 1.0:
            self.transverse = 1.0 - self._axial
     
    @property
    def transverse(self):
        return self._transverse

    @transverse.setter
    def transverse(self, value):
        self._transverse = ChromaticAberration.clamp(value, 0.0, 1.0)
        #self.program['u_transverse'] = self._transverse

        #Ensure that axial + transverse do not sum to more than 1.0
        if self._transverse + self. axial > 1.0:
            self.axial = 1.0 - self._transverse

    @property
    def distance_scale(self):
        return self._distance_scale
    
    @distance_scale.setter
    def distance_scale(self,value):
        self._distance_scale = value
        self.program['u_distance_scale'] = value

    def show_ui(self):
        super().show_ui()

        self.axial = imgui.slider_float(f'Strength##{self.ui_index}', self.axial, 0.0, 1.0)[1]
        #self.transverse = imgui.slider_float(f'Transverse Aberration##{self.ui_index}', self.transverse, 0.0, 1.0)[1]

        self.distance_scale = imgui.slider_float(f'Distance Scale##{self.ui_index}', self.distance_scale, 0.0, 0.1)[1]