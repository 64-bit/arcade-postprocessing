import arcade
from postprocessing.render_target import RenderTarget
from postprocessing.ping_pong_buffer import PingPongBuffer
from postprocessing.post_effect import PostEffect
from postprocessing.static_render_target_pair import StaticRenderTargetPair

class PostProcessingChain:

    has_imgui = True

    def __init__(self, context: arcade.gl.context.Context, initial_size, enable_hdr):
        self.context = context
        self._current_size = initial_size

        self._effects = []

        self._ldr_ping_pong_buffer = PingPongBuffer(context, initial_size, 'f1')
        self._hdr_ping_pong_buffer = None

        self.hdr = enable_hdr
        
    def apply_effects(self, source_texture , destination_framebuffer = None):

        #Ensure no blend mode is enabled
        self.context.enable_only()

        self._resize_if_needed(source_texture)

        if self.are_any_effects_active():
            self._apply_effect_chain(source_texture, destination_framebuffer)       
        else:
            self._passthrough(source_texture, destination_framebuffer)         

    def _apply_effect_chain(self, source_texture, destination_framebuffer):

        first_effect = self.get_first_active_effect()
        last_effect = self.get_last_active_effect()

        is_hdr = self.hdr

        for effect in self._effects:
            if not effect.enabled:
                continue

            render_target_pair = self._get_render_target_pair_for_effect(effect, first_effect, last_effect, source_texture, destination_framebuffer, is_hdr)

            effect.apply(render_target_pair)

            #TODO: how to re-factor this into or out of the method above ?
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

    def _resize_if_needed(self, source_texture):
        pass

    def _passthrough(self, source_texture, destination_framebuffer):
        source_texture.texture.use(0)
        destination_framebuffer.use()
        RenderTarget.fullscreen_quad.render(RenderTarget.blit_program)

    def are_any_effects_active(self):
        for effect in self._effects:
            if effect.enabled:
                return True
        return False

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

    def show_postprocess_ui(self):
        if PostProcessingChain.has_imgui == False:
            raise TypeError("IMGUI cannot be found")

        imgui.begin("Post-Processing window", False)
        imgui.text("Post-Processing Stages:")
        imgui.separator()

        for stage in self._effects:
            if imgui.collapsing_header(type(stage).__name__, flags=imgui.TREE_NODE_DEFAULT_OPEN)[0]:
                stage.show_ui()

        imgui.end()

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


try:
    import imgui
except ImportError:
    PostProcessingChain.has_imgui = False