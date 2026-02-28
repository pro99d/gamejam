import arcade
from dataclasses import dataclass
import base_classes as bc
from base_classes import Vec2
import time
import math
import random
import helpers
from weapons import *

enemies = []

@dataclass
class WearponData:
    reload: float
    damage: float
    spread: float
    size: Vec2
    lifetime: float


class Wall(bc.Entity):
    def __init__(self, pos: Vec2, size: Vec2 = Vec2(50, 50)):
        super().__init__(pos, size, (100, 100, 100), moment_of_inertia= bc.PymunkPhysicsEngine.MOMENT_INF, collision_type= "Wall", type_ = bc.PymunkPhysicsEngine.STATIC)
        a = size.__div__(2)
        b = size.__div__(-2)
        c = Vec2(size.x / 2, size.y / -2)
        d = Vec2(size.x / -2, size.y / 2)
        p = self.pos 


class Enemy(bc.Entity):
    def __init__(self, pos: Vec2, target: bc.Entity):
        super().__init__(
            pos, Vec2(45, 45), (255, 0, 0),
            collision_type="Enemy",
        )
        self.target = target
        self.health = 100
        self.inv = False
        self.type_ = 1 # TODO implement enemy types
        self.rect.parent = self

    def update(self, dt):
        super().update(dt)

        dp = self.target.pos - self.pos
        self.angle = math.degrees(math.atan2(dp.x, dp.y))
        speed = 600
        self.velocity = dp.normalize()*speed
        bc.phys.apply_force(self.rect, self.velocity.__list__())
        if self.health <= 0:
            self.die()
            enemies.remove(self)

class Player(bc.Entity):
    def __init__(self, pos: Vec2):
        super().__init__(pos, Vec2(45, 45), (0, 255, 0), collision_type= "Player")
        self.keys = set() 
        self.weapon_number = 0
        self.weapon_list = [Pistol(self), Riffle(self), MachinePistols(self), Shotgun(self), Crossbow(self), SniperRiffle(self)] 
        # self.weapon_list = ['Pistol','riffle','machine_pistols','shotgun','crossbow','sniper_riffle']
        self.health = 50
        self.rect.parent = self

    def set_angle(self, mouse_pos: Vec2):

        dp = self.pos -mouse_pos
        if dp.y:
            self.angle = math.degrees(math.atan2(dp.x, dp.y))
        else:
            self.angle = 90

    weapon_number = 0
    def update(self, dt: float):
        self.velocity *= 0.90
        dv = Vec2(0, 0)
        acc = 2500
        if arcade.key.W in self.keys:
            dv += Vec2(0, acc)
        if arcade.key.S in self.keys:
            dv += Vec2(0, -acc)
        if arcade.key.D in self.keys:
            dv += Vec2(acc, 0)
        if arcade.key.A in self.keys:
            dv += Vec2(-acc, 0)
        bc.phys.apply_force(self.rect, dv.__list__())

        if arcade.key.KEY_1 in self.keys:
            self.weapon_number = 0
        if arcade.key.KEY_2 in self.keys:
            self.weapon_number = 1
        if arcade.key.KEY_3 in self.keys:
            self.weapon_number = 2
        if arcade.key.KEY_4 in self.keys:
            self.weapon_number = 3
        if arcade.key.KEY_5 in self.keys:
            self.weapon_number = 4
        if arcade.key.KEY_6 in self.keys:
            self.weapon_number = 5
        # if self.velocity.magnitude() < acc * 10:
            # self.velocity += dv
        # update all childs
        for wearpon in self.weapon_list:
            wearpon.update(dt)
        if arcade.key.SPACE in self.keys:

            self.weapon_list[self.weapon_number].shoot()

        return super().update(dt)
    def on_key_press(self, key):
        self.keys.add(key)
    def on_key_release(self, key):
        self.keys.remove(key)

class Window(arcade.Window):
    def __init__(self):
        super().__init__(1920, 1080, "game for game jam", fullscreen= True)
        self.bloom = arcade.experimental.BloomFilter(
            self.width, self.height, 20)
        self.mouse_pos = Vec2(1, 1)
        # self.walls = [Wall(Vec2(i.x, i.y), Vec2(50, 500)) for i in l1]


        self.vig = helpers.Shader("shaders/vignette.glsl", self.ctx, w= self.width, h= self.height)
        self.pix = helpers.Shader("shaders/pixelation.glsl", self.ctx, w= self.width, h= self.height)
        self.bg = helpers.Shader("shaders/bg.glsl", self.ctx, w= self.width, h= self.height)


        self.setup_collision_handlers()

        self.vig_alp = 1.5
        self.vig["alpha"] = self.vig_alp
        self.pix["cell_size"] = 5.0
        self.vig["inner_radius"] = 0.0
        self.vig["outer_radius"] = 1.0
        # self.bg["screen_size"] = (1920, 1080)
        
        self.screen_size = Vec2(self.width, self.height)

        aspect_ratio = self.width/self.height
        deadzone_size = 100
        self.camera_deadzone = Vec2(deadzone_size*aspect_ratio, deadzone_size/aspect_ratio)
        self.setup()

    def setup(self):
        global enemies
        enemies.clear()
        
        # Kill all existing entities (iterate over a copy to avoid modification during iteration)
        for sprite in list(bc.sprite_all_draw):
            if hasattr(sprite, "parent") and hasattr(sprite.parent, "die"):
                sprite.parent.die()
            else:
                sprite.remove_from_sprite_lists()
        
        self.level = helpers.LevelLoader.load_level("level.lvl")
        self.player = Player(self.level.spawn.pos)

        for wall in self.level.walls:
            Wall(wall.pos, wall.size)

        for enemy in self.level.enemies:
            e = Enemy(enemy.pos, self.player)
            enemies.append(e)

        self.camera = arcade.Camera2D(position= self.player.pos.__list__())
        self.camera_pos = self.player.pos

        self.health_bar = bc.Bar(
                                self.get_world_from_screen(Vec2(10, 10)),
                                Vec2(300, 20),
                                (255, 10, 10),
                                (100, 100, 100),
                                50,
                                50
                                )

    def get_world_from_screen(self, pos):
        return pos + (self.camera_pos - Vec2(self.width/2, self.height/2))

    def setup_collision_handlers(self):

        def sprite_from_arbiter(arbiter, num):
            shape = arbiter.shapes[num]
            sprite = bc.phys.get_sprite_for_shape(shape)
            return sprite

        def enemy_hit_handler(sprite_a, sprite_b, arbiter, space, data):
            """ Called for bullet/enemy collision """
            # TODO add checks for types
            bullet_sprite =sprite_from_arbiter(arbiter, 0)
            bullet_sprite.parent.die()
            enemy_sprite = sprite_from_arbiter(arbiter, 1)
            enemy_sprite.parent.health -= bullet_sprite.parent.damage
            
        def en_player_hit_handler(sprite_a, sprite_b, arbiter, space, data):
            player_sprite = sprite_from_arbiter(arbiter, 0)
            player = player_sprite.parent
            enemy = sprite_from_arbiter(arbiter, 1)
            player.health -= enemy.parent.damage
            


        def wall_hit_handler(sprite_a, sprite_b, arbiter, space, data):
            """ Called for bullet/wall collision """
            # TODO add checks for types
            bullet_sprite = sprite_from_arbiter(arbiter, 0)
            # bullet_sprite.remove_from_sprite_lists()
            # bullet_sprite.parent.die()
        
        bc.phys.add_collision_handler(
                "Bullet",
                "Enemy",
                post_handler= enemy_hit_handler
                )
        bc.phys.add_collision_handler(
                "Bullet",
                "Wall",
                post_handler= wall_hit_handler
                )



    def on_resize(self, width: int, height: int):
        self.bloom = arcade.experimental.BloomFilter(width, height, 20)
        self.pix.resize(width, height)
        self.screen_size = Vec2(width, height)

        self.vig.resize(width, height)
        # self.bg["screen_size"] = (width, height)
        self.bg.resize(width, height)

        self.camera = arcade.Camera2D()

    def all_draw(self):
        bc.sprite_all_draw.draw()

    def draw_ui(self):
        self.health_bar.update_pos(self.get_world_from_screen(Vec2(10, 10)))
        self.health_bar.draw()

        name_pos = self.get_world_from_screen(Vec2(10, self.height-15))
        weapon = self.player.weapon_list[self.player.weapon_number]
        name = weapon.__repr__()
        arcade.draw_text(f"Weapon: {name}", name_pos.x, name_pos.y)
        bullets = weapon.bul_count_now
        arcade.draw_text(f"bullets left: {bullets}", name_pos.x, name_pos.y - 15)
        if bullets == 0:
            arcade.draw_text(f"reload {weapon.prop.reload_time - (time.time() - weapon.last_shot):.2f}", name_pos.x, name_pos.y - 30)


    # def get_world_from

    def on_draw(self):
        self.camera.use()
        self.bg["pos"] = self.camera_pos.__list__()
        self.pix["screen_size"] = (self.screen_size * self.camera.zoom).__list__()
        self.vig["screen_size"] = (self.screen_size * self.camera.zoom).__list__()
        # self.fbo.clear(color = (255, 255, 255))
        self.vig.clear()
        self.pix.clear()
        self.bg.clear() 
        with self.vig:
            with self.pix:
                self.bg.draw()
                self.all_draw()
            self.pix.draw()
        self.vig.draw()
        self.draw_ui()
        # self.tex.use(0)
        # self.quad_fs.render(self.pixelation)
        # self.quad_fs.render(self.vignette)

    def on_update(self, dt: float):
        bc.phys.step(1/60)
        self.player.update(dt)
        self.player.set_angle(self.mouse_pos)
        for enemy in enemies:
            enemy.update(dt)

        dp = self.player.pos - self.camera_pos
        if abs(dp.x) > self.camera_deadzone.x:
            dp.x -= math.copysign(self.camera_deadzone.x, dp.x)
        else:
            dp.x = 0

        if abs(dp.y) > self.camera_deadzone.y:
            dp.y -= math.copysign(self.camera_deadzone.y, dp.y)
        else:
            dp.y = 0

        new_camera_pos = self.camera_pos + dp
        self.camera.position = new_camera_pos.__list__()
        self.camera_pos = new_camera_pos
        self.vig["alpha"] = self.vig_alp
        
        self.health_bar.value = self.player.health


    def on_key_press(self, key, *_):
        if key == arcade.key.Q:
            arcade.close_window()
        elif key == arcade.key.R:
            self.setup()
        self.player.on_key_press(key)

    def on_key_release(self, key, mod):
        self.player.on_key_release(key)

    def on_mouse_press(self, x, y, *_):
        pos = self.get_world_from_screen(Vec2(x, y))
        enemy = Enemy(pos, self.player)
        enemies.append(enemy)

    def on_mouse_motion(self, x, y, *_):
        pos = self.get_world_from_screen(Vec2(x, y))
        self.mouse_pos = pos


def main():
    win = Window()
    win.run()


if __name__ == "__main__":
    main()
