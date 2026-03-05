import arcade
import helpers

class Window(arcade.Window):
    def __init__(self):
        super().__init__()
        self.shader = helpers.Shader("shaders/ammo_left.glsl", self.ctx)
        self.total_time = 0
        self.shader["start_pos"] = (0, self.height-25)

    def on_update(self, dt):
        self.total_time += dt

    def on_resize(self, w, h):
        self.shader["screen_size"] = (w, h)
        self.shader.resize(w, h)
    
    def on_draw(self):
        self.clear()
        self.shader["reload"] = self.total_time%1
        # self.shader["repeat_count"] = round(self.total_time * 10)
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
