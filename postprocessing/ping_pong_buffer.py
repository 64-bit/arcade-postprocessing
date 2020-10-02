import arcade
from postprocessing.render_target import RenderTarget
from postprocessing.render_target_pair import RenderTargetPair

class PingPongBuffer(RenderTargetPair):

    def __init__(self, context, size, texture_format):

        self.context = context
        self._texture_format = texture_format
        self.size = size

        self._ping_buffer = None
        self._pong_buffer = None

        self._allocate_buffers(size, texture_format)

    def resize(self, size):
        self.release()
        self.size = size
        self._allocate_buffers(size, self.texture_format)

    def _allocate_buffers(self, size, texture_format):
        self._ping_buffer = RenderTarget(self.context, size, texture_format)
        self._pong_buffer = RenderTarget(self.context, size, texture_format)
        
    def release(self):
        if self._pong_buffer is not None:
            self._pong_buffer.release()

    def flip_buffers(self):
        pass

    #Implementation for RenderTargetPair
    #Bind the texture side to a given texture index, and bind the render target side as the current drawing target
    def bind(self, texture_index):
        self._ping_buffer.bind_as_texture(texture_index)
        self._pong_buffer.bind_as_framebuffer()

    #Get the (texture,framebuffer) as a tuple pair for more advanced use cases
    def get_render_target_pair(self):
         return (self._ping_buffer.texture, self._pong_buffer.framebuffer_object)