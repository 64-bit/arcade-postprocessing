
#This needs to be re-named
#Represents a pair of render targets used in a blit, a source as a texture and a desteniation as a framebuffer object
class RenderTargetPair:

    #Bind the texture side to a given texture index, and bind the render target side as the current drawing target
    def bind(self, texture_index):
        raise NotImplementedError("This needs to be implemented in a derrived class")

    #Get the (texture,framebuffer) as a tuple pair for more advanced use cases
    def get_render_target_pair(self):
         raise NotImplementedError("This needs to be implemented in a derrived class")
       