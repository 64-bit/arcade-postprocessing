import arcade
import math

from postprocessing.post_effect import PostEffect
from postprocessing.render_target import RenderTarget
from postprocessing.ping_pong_buffer import PingPongBuffer
from pyglet import gl

try:
    import imgui
    import imgui.core
except:
    pass

class Bloom(PostEffect):
    def __init__(self, context, window_size):
        super().__init__(context, window_size)
        
        self.extract_blur_x = context.load_program(
            vertex_shader="postprocessing/core_shaders/fullscreen_quad.vs",
            fragment_shader="postprocessing/effects/shaders/extract_blur_x.fs"
        )

        self.blur_y_power = context.load_program(
            vertex_shader="postprocessing/core_shaders/fullscreen_quad.vs",
            fragment_shader="postprocessing/effects/shaders/blur_y_power.fs"
        )

        self.set_universal_shader_args(self.extract_blur_x)
        self.set_universal_shader_args(self.blur_y_power)

        self.blur_y_power['t_last'] = 1

        self.load_apply_bloom(context)

        self.chain = []
        self._desired_chain = 5

        self.threshold = 1.0
        self.power = 1.0

        # Allocate the downscaled render targets and blur buffers
        self.allocate_whole_chain()

    def set_universal_shader_args(self, program):
        program["t_source"] = 0

        weights = self.get_blur_coefficents(11)  # must match shader
        weights_sum = 0
        for x in weights:
            weights_sum += x

        program["u_weights"] = weights
        program["u_weight_sum"] = weights_sum


    def adjust_chain_size(self, size):
        if len(self.chain) == size:
            return
        if size < len(self.chain):
            self.chain = self.chain[0:size]
        else:
            current_min_size = self.chain[-1].size
            self.allocate_chain(size-len(self.chain), current_min_size)

    def allocate_whole_chain(self):
        self.chain = []
        self.allocate_chain(self._desired_chain, self.window_size)

    def allocate_chain(self, remaining, size):
        if remaining == 0:
            return
        
        if size[0] == 0 or size[1] == 0:
            return

        size = (size[0] // 2 , size[1] // 2)
        ping_pong = PingPongBuffer(self.context, size, texture_format='f2')#TODO: Is HDR
        self.chain.append(ping_pong)
        self.allocate_chain(remaining-1, size)

    def load_apply_bloom(self, context):

        self.apply_bloom = context.load_program(
            vertex_shader="postprocessing/core_shaders/fullscreen_quad.vs",
            fragment_shader="postprocessing/effects/shaders/apply_bloom.fs",
        )

        self.apply_bloom["t_source"] = 0
        self.apply_bloom["t_half"] = 1
        #self.apply_bloom["t_quater"] = 2

    def resize(self, window_size):
        super(Bloom, self).resize(window_size)
        self.allocate_whole_chain()

    def get_blur_coefficents(self, count):
        midpoint = math.floor(count / 2)
        stdev = midpoint / 3.0  # I think this is right but #GameJam

        coefficents = [0.0] * count

        for x in range(0, midpoint + 1):
            distance = midpoint - x
            factor = self.gaussian(distance, stdev)

            coefficents[x] = factor
            coefficents[count - (1 + x)] = factor

        return coefficents

    def gaussian(self, distance, stdev):
        # See this for the math: https://en.wikipedia.org/wiki/Gaussian_blur
        preamble = 1.0 / math.sqrt(2.0 * math.pi * stdev * stdev)
        exponent = -((distance * distance) / (2.0 * stdev * stdev))

        return preamble * math.exp(exponent)

    def apply(self, render_target_pair):

        # Downsample main RT to half and quater size
        self.downsample_to_ping(render_target_pair.texture)

        # run ping pong back and forth to blur the light buffer
        for ping_pong in self.chain:
            self.apply_blur_down(ping_pong)

        #clear texture 1 so that the bottom of the chain reads from a unbound black texture
        gl.glActiveTexture(gl.GL_TEXTURE0 + 1)
        gl.glBindTexture(gl.GL_TEXTURE_2D, 0)
       
        #run up and down the chain
        last = None
        for ping_pong in reversed(self.chain):
            self.apply_blur_up(ping_pong, last)
            last = ping_pong

        # Apply top of chain to main image, as it has all the lower levels added already
        render_target_pair.bind(0)
        self.chain[0].texture.use(1)

        PostEffect.fullscreen_quad.render(self.apply_bloom)

    def apply_blur(self, ping_pong):

        # Set arugments for pass size
        texel_uv_size = (1.0 / ping_pong.size[0], 1.0 / ping_pong.size[1])

        self.extract_blur_x["u_texel_size"] = texel_uv_size
        self.blur_y_power["u_texel_size"] = texel_uv_size

        # blur ping onto pong
        ping_pong.bind(0)
        PostEffect.fullscreen_quad.render(self.extract_blur_x)
        ping_pong.flip_buffers()

        # blur pong back to ping
        ping_pong.bind(0)
        PostEffect.fullscreen_quad.render(self.blur_y_power)
        ping_pong.flip_buffers()

        pass

    def apply_blur_down(self, ping_pong):

        # Set arugments for pass size
        texel_uv_size = (1.0 / ping_pong.size[0], 1.0 / ping_pong.size[1])

        self.extract_blur_x["u_texel_size"] = texel_uv_size
        self.blur_y_power["u_texel_size"] = texel_uv_size

        # blur ping onto pong
        ping_pong.bind(0)
        PostEffect.fullscreen_quad.render(self.extract_blur_x)
        ping_pong.flip_buffers()

        pass

    def apply_blur_up(self, ping_pong, last):

        # Set arugments for pass size
        texel_uv_size = (1.0 / ping_pong.size[0], 1.0 / ping_pong.size[1])

        self.extract_blur_x["u_texel_size"] = texel_uv_size
        self.blur_y_power["u_texel_size"] = texel_uv_size

        #bind last
        if last is not None:
            last.texture.use(1)

        # blur pong back to ping
        ping_pong.bind(0)
        PostEffect.fullscreen_quad.render(self.blur_y_power)
        ping_pong.flip_buffers()

        pass

    def downsample_to_ping(self, source_texture):

        program = RenderTarget.blit_program #TODO:Set to extract

        for ping_pong in self.chain:

            ping_pong.framebuffer.use()
            source_texture.use(0)

            RenderTarget.fullscreen_quad.render(program)
            ping_pong.flip_buffers()
            source_texture = ping_pong.texture

            program = RenderTarget.blit_program

    @property
    def threshold(self):
        return self._threshold

    @threshold.setter
    def threshold(self, value):
        self._threshold = value
        self.extract_blur_x["u_threshold"] = value

    @property
    def power(self):
        return self._power * 2.0

    @power.setter
    def power(self, value):
        self._power = value * 0.5
        self.blur_y_power["u_power"] = value * 0.5

    def show_ui(self):
        super().show_ui()

        self.power = imgui.slider_float(f'Strength##{self.ui_index}', self.power, 0.0, 5.0)[1]
        self.threshold = imgui.slider_float(f'Threshold##{self.ui_index}', self.threshold, 0.0, 16.0, power=2.0)[1]