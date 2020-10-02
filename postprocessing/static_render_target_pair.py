import arcade
from postprocessing.render_target_pair import RenderTargetPair

class StaticRenderTargetPair(RenderTargetPair):

    def __init__(self, texture: arcade.gl.texture.Texture, framebuffer: arcade.gl.framebuffer.Framebuffer):
        self.texture = texture
        self.framebuffer = framebuffer

    #Bind the texture side to a given texture index, and bind the render target side as the current drawing target
    def bind(self, texture_index):
        self.texture.use(texture_index)
        self.framebuffer.use()

    #Get the (texture,framebuffer) as a tuple pair for more advanced use cases
    def get_render_target_pair(self):
         return (self.texture, self.framebuffer)
    
