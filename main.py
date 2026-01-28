import arcade
import base_classes as bc



class Window(arcade.Window):
    def __init__(self):
        super().__init__(800, 600, "game for game jam")
        self.bloom = arcade.experimental.BloomFilter(self.width, self.height, 20)
        # self.bloom.fbo.use()
        # self.bloom.draw(0, self.ctx)
    def on_resize(self, width: int, height: int):
        self.bloom = arcade.experimental.BloomFilter(width, height, 20)

    def on_draw(self):
        self.clear()
        self.bloom.fbo.use()
        with self.bloom.fbo: 
            arcade.draw_circle_filled(100, 100, 10, (255, 255, 255))

        self.ctx.screen.use()
        self.bloom.draw(0, self.ctx.screen)

    def on_key_press(self, key, *_):
        if key == arcade.key.Q:
            arcade.close_window()


def main():
    win = Window()
    win.run()


if __name__ == "__main__":
    main()
