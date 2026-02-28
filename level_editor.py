import arcade
import os
from base_classes import Vec2
import helpers
from main import Wall, Enemy
from base_classes import sprite_all_draw

SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
SCREEN_TITLE = "Level Editor"


class Window(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, fullscreen= True)
        arcade.set_background_color(arcade.color.DARK_GREEN)
        self.camera = arcade.Camera2D()
        self.grid_shader = helpers.Shader("shaders/grid.glsl", self.ctx)
        self.camera_pos = Vec2(0, 0)
        self.grid_shader["grid_color"] = [0.5450, 0, 0]
        self.grid_shader["bg_color"] = [0, 0.5450, 0]
        self.gr_size = 50
        self.grid_shader["size"] = self.gr_size
        self.grid_shader["u_resolution"] = (self.width, self.height)
        self.keys = set()
        self.mode = 1
        if "level.lvl" in os.listdir('.'):
            self.level = helpers.LevelLoader.load_level("level.lvl")
            walls = []
            enemies = []
            for enemy in self.level.enemies:
                enemies.append(Enemy(enemy.pos, 1))
            self.level.enemies = enemies 
            for wall in self.level.walls:
                walls.append(Wall(wall.pos, wall.size))
            self.level.walls = walls
        else:
            self.level = helpers.Level()

    def on_resize(self, w, h):
        self.grid_shader.resize(w, h)
        self.grid_shader["u_resolution"] = (w, h)

    def get_world_from_screen(self, pos):
        return pos + (Vec2(*self.camera.position) - Vec2(self.width/2, self.height/2))

    def on_draw(self):
        self.camera.use()
        self.clear()
        self.grid_shader.clear()
        self.grid_shader.draw()
        sprite_all_draw.draw()
        pos = self.get_world_from_screen(Vec2(10, 15))
        arcade.draw_text("SPACE to save to «level.lvl»", pos.x, pos.y + 75)
        arcade.draw_text(f"mode: {self.mode}", pos.x, pos.y+60)
        arcade.draw_text("Q to exit", pos.x, pos.y+45)
        arcade.draw_text("1 for enter wall mode.", pos.x, pos.y + 30)
        arcade.draw_text("2 for enter enemy mode.", pos.x, pos.y + 15)
        arcade.draw_text("3 for enter spawn point mode.", pos.x, pos.y)
        arcade.draw_text("LMB for place, RMB for delete", pos.x, pos.y + self.height - 30)
        arcade.draw_text("spawn", *self.level.spawn.pos.__list__())
        
    def on_update(self, dt):
        self.camera_pos = Vec2(*self.camera.position)
        self.grid_shader["pos"] = self.camera_pos.__list__()
        dp = Vec2(0, 0)
        acc = 10
        if arcade.key.W in self.keys:
            dp += Vec2(0, acc)
        if arcade.key.S in self.keys:
            dp += Vec2(0, -acc)
        if arcade.key.D in self.keys:
            dp += Vec2(acc, 0)
        if arcade.key.A in self.keys:
            dp += Vec2(-acc, 0)
        self.camera.position = (self.camera_pos + dp).__list__()

    def on_key_press(self, symbol, modifiers):
        if symbol == arcade.key.Q:
            self.close()
        elif symbol == arcade.key.KEY_1:
            self.mode = 1
        elif symbol == arcade.key.KEY_2:
            self.mode = 2
        elif symbol == arcade.key.KEY_3:
            self.mode = 3
        elif symbol == arcade.key.SPACE:
            helpers.LevelLoader.save_level("level.lvl", self.level)

        self.keys.add(symbol)
    
    def on_key_release(self, symbol, modifiers):
        self.keys.remove(symbol)
    def on_mouse_press(self, x, y, button, *_):
        pos = self.get_world_from_screen(Vec2(x, y))
        pos.x //= self.gr_size
        pos.y //= self.gr_size
        pos *= self.gr_size
        pos += .5 * self.gr_size
        if button == arcade.MOUSE_BUTTON_LEFT:
            if self.mode == 1:
                wall = Wall(pos, Vec2(self.gr_size, self.gr_size))
                self.level.walls.append(wall)
            elif self.mode == 2:
                enemy = Enemy(pos, None)
                self.level.enemies.append(enemy)
            elif self.mode == 3:
                self.level.spawn.pos = pos
        elif button == arcade.MOUSE_BUTTON_RIGHT:
            for enemy in self.level.enemies:
                if enemy.rect.collides_with_point(pos.__list__()):
                    enemy.die()
                    enemy.rect.kill()
                    self.level.enemies.remove(enemy)
            for wall in self.level.walls:
                if wall.rect.collides_with_point(pos.__list__()):
                    wall.die()
                    wall.rect.kill()
                    self.level.walls.remove(wall)
        else:
            print(button)
        # print(walls)

if __name__ == "__main__":
    window = Window()
    window.run()

