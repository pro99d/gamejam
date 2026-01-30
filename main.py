import arcade
import base_classes as bc
from base_classes import Vec2

class Player(bc.Entity):
    def __init__(self, pos: Vec2):
        super().__init__(pos, Vec2(50, 50), (0, 255, 0))
        self.keys = set() 

    def update(self, dt: float):
        self.velocity *= 0.90
        dv = Vec2(0, 0)
        acc = 100
        if arcade.key.W in self.keys:
            dv += Vec2(0, acc)
        if arcade.key.S in self.keys:
            dv += Vec2(0, -acc)
        if arcade.key.D in self.keys:
            dv += Vec2(acc, 0)
        if arcade.key.A in self.keys:
            dv += Vec2(-acc, 0)
        self.update_vel(dv, 600)
        return super().update(dt)
    def on_key_press(self, key):
        self.keys.add(key)
    def on_key_release(self, key):
        self.keys.remove(key)

class Window(arcade.Window):
    def __init__(self):
        super().__init__(800, 600, "game for game jam")
        self.bloom = arcade.experimental.BloomFilter(self.width, self.height, 20)
        self.player = Player(Vec2(200, 200)) 

    def on_resize(self, width: int, height: int):
        self.bloom = arcade.experimental.BloomFilter(width, height, 20)

    def on_draw(self):
        self.clear()
        self.bloom.fbo.use()
        self.bloom.fbo.clear()
        with self.bloom.fbo: 
            bc.sprite_all_draw.draw()

        self.ctx.screen.use()
        self.bloom.draw(0, self.ctx.screen)

    def on_update(self, dt: float):
        self.player.update(dt)

    def on_key_press(self, key, *_):
        if key == arcade.key.Q:
            arcade.close_window()
        self.player.on_key_press(key)
    def on_key_release(self, key, mod):
        self.player.on_key_release(key)


def main():
    win = Window()
    win.run()


if __name__ == "__main__":
    main()
