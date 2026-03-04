import arcade
import helpers

class Window(arcade.Window):
    def __init__(self):
        super().__init__()
        self.shader = helpers.Shader("shaders/test.glsl", self.ctx)

    def on_resize(self, w, h):
        self.shader["screen_size"] = (w, h)
        self.shader.resize(w, h)
    
    def on_draw(self):
        self.clear()
        self.shader.clear()
        with self.shader:
            arcade.draw_circle_filled(500, 200, 100, arcade.color.RED)
        self.shader.draw()
    def on_key_press(self, key, *_):
        if key == arcade.key.Q:
            arcade.close_window()

if __name__ == "__main__":
    window = Window()
    window.run()
