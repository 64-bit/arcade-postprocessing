import arcade

class RenderTarget:

    def __init__(self, context, size, texture_format='f1'):
        self.context = context
        self.texture = None
        self.framebuffer_object = None
        self.size = size
        self.texture_format = texture_format

        self.resize(size)

    def resize(self, newSize):
        self.release()
        self.size = newSize
        self._allocate_target(newSize)

    def _allocate_target(self, size):
        self.texture = arcade.gl.Texture(
            self.context,
            size,
            components=4,
            dtype=self.texture_format,
            wrap_x=arcade.gl.CLAMP_TO_EDGE,
            wrap_y=arcade.gl.CLAMP_TO_EDGE,
        )

        self.framebuffer_object = arcade.gl.Framebuffer(
            self.context, color_attachments=[self.texture]
        )

    def bind_as_texture(self, texture_slot):
        self.texture.use(texture_slot)

    def bind_as_framebuffer(self):
        self.framebuffer_object.use()        

    def release(self):
        if self.texture is not None:
            self.texture.release()

        if self.framebuffer_object is not None:
            self.framebuffer_object.release()

        self.texture = None
        self.framebuffer_object = None
