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

        #Ensure no blend mode is enabled
        self.context.enable_only()

        #TODO:Check resize
        #self._resize_if_needed(source_texture)


        #3 cases on how this works, the first 2 being somewhat special cases
        #active_effects = self.count_active_effects()
    
        if self.are_any_effects_active():
            self._apply_effect_chain(source_texture, destination_framebuffer)       
        else:
            self._passthrough(source_texture, destination_framebuffer)         



    def _apply_effect_chain(self, source_texture, destination_framebuffer):

        first_effect = self.get_first_active_effect()
        last_effect = self.get_last_active_effect()

        source_dest_pair = StaticRenderTargetPair(source_texture, destination_framebuffer)

        is_hdr = self.hdr

        for effect in self._effects:
            if not effect.enabled:
                continue

            render_target_pair = self._get_render_target_pair_for_effect(effect, first_effect, last_effect, source_texture, destination_framebuffer, is_hdr)

            effect.apply(render_target_pair)
            if effect.is_tonemapping_effect():
                is_hdr = False

    def _get_render_target_pair_for_effect(self, effect, first_effect, last_effect, source_texture, destination_framebuffer, is_hdr):
        
        target_ping_pong = self._hdr_ping_pong_buffer if self.hdr else self._ldr_ping_pong_buffer
        target_ping_pong.flip_buffers()

        target_pair = target_ping_pong

        if effect.is_tonemapping_effect():
            target_pair = StaticRenderTargetPair(target_pair.texture, self._ldr_ping_pong_buffer.framebuffer)

        if effect is first_effect:
            target_pair = StaticRenderTargetPair(source_texture, target_pair.framebuffer)

        if effect is last_effect:
            target_pair = StaticRenderTargetPair(target_pair.texture, destination_framebuffer)   

        return target_pair     

    
    def _passthrough(self, source_texture, destination_framebuffer):
        source_texture.texture.use(0)
        destination_framebuffer.use()
        self.fullscreen_quad.render(self.blit_program)

    def are_any_effects_active(self):
        for effect in self._effects:
            if effect.enabled:
                return True
        return False

    def count_active_effects(self):
        active_effects = 0
        for effect in self._effects:
            if effect.enabled:
                active_effects += 1
        return active_effects

    def get_first_active_effect(self):
        for effect in self._effects:
            if effect.enabled:
                return effect
        return None
    
    def get_last_active_effect(self):
        for effect in reversed(self._effects):
            if effect.enabled:
                return effect
        return None
        

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