import arcade
from postprocessing.ping_pong_buffer import PingPongBuffer
from postprocessing.post_effect import PostEffect
from postprocessing.static_render_target_pair import StaticRenderTargetPair

class PostProcessingChain:

    def __init__(self, context: arcade.gl.context.Context, initial_size, enable_hdr):
        self.context = context
        self._current_size = initial_size

        self._effects = []

        self._ldr_ping_pong_buffer = PingPongBuffer(context, initial_size, 'f1')
        self._hdr_ping_pong_buffer = None

        self.hdr = enable_hdr

        self.blit_program = context.load_program(
            vertex_shader="postprocessing/core_shaders/fullscreen_quad.vs",
            fragment_shader="postprocessing/core_shaders/blit.fs",
        )

        self.blit_program['t_source'] = 0
        self.fullscreen_quad = arcade.gl.geometry.quad_2d_fs()
        
    def apply_effects(self, source_texture , destination_framebuffer = None):

        #TODO:Check resize

        #3 cases on how this works, the first 2 being somewhat special cases
        active_effects = self.count_active_effects()

        # #1 - 0 effects enabled, do passthrough
        if active_effects == 0:
            self._passthrough(source_texture, destination_framebuffer)
            return

        # #2 - 1 effect enabled
        if active_effects == 1:
            self._single_effect(source_texture, destination_framebuffer)
            return

        # #3 - 2 or more effects enabled
        self._multi_effect(source_texture, destination_framebuffer)

    def _passthrough(self, source_texture, destination_framebuffer):
        source_texture.texture.use(0)
        destination_framebuffer.use()
        self.fullscreen_quad.render(self.blit_program)

    def _single_effect(self, source_texture, destination_framebuffer):
        target_pair = StaticRenderTargetPair(source_texture, destination_framebuffer)

        for effect in self._effects:
            if effect.enabled:
                effect.apply(target_pair)

    def _multi_effect(self, source_texture, destination_framebuffer):
        pass

    def count_active_effects(self):
        active_effects = 0
        for effect in self._effects:
            if effect.enabled:
                active_effects += 1
        return active_effects

    def add_effect(self, effect):
       # if not isinstance(effect, PostEffect):
        #    raise TypeError("effect must be derrived from PostEffect")

        new_effect = effect(self.context, self._current_size)
        self._effects.append(new_effect)
        return new_effect

    def remove_effect(self, effect):
        self._effects.remove(effect)

    def get_effect(self, effect_type):
        for effect in self._effects:
            if isinstance(effect, effect_type):
                return effect
        return None

    def reset_effects(self):
        self._effects = []

    @property
    def hdr(self):
        return self._hdr_enabled

    @hdr.setter
    def hdr(self, value):
        self._hdr_enabled = value
        if value:
            self._enable_hdr()
        else:
            self._disable_hdr()

    def _enable_hdr(self):
        if self._hdr_ping_pong_buffer is None:
            self._hdr_ping_pong_buffer = PingPongBuffer(self.context, self._current_size, 'f2')

    def _disable_hdr(self):
        if self._hdr_ping_pong_buffer is not None:
            self._hdr_ping_pong_buffer.release()
            self._hdr_ping_pong_buffer = None