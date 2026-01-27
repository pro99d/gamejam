import arcade
import base_classes as bc


class Window(arcade.Window):
    def __init__(self):
        super().__init__(800, 600, "game for game jam")

    def on_draw(self):
        self.clear()

    def on_key_press(self, key, *_):
        if key == arcade.key.Q:
            arcade.close_window()


def main():
    win = Window()
    win.run()


if __name__ == "__main__":
    main()
