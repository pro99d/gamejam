import arcade
from dataclasses import dataclass
import base_classes as bc
from base_classes import Vec2
import time
import math
import random
import helpers
from weapons import *
import particles


enemies = []
walls = arcade.SpriteList()


@dataclass
class WearponData:
    reload: float
    damage: float
    spread: float
    size: Vec2
    lifetime: float


class Wall(bc.Entity):
    def __init__(self, pos: Vec2, size: Vec2 = Vec2(50, 50)):
        super().__init__(pos, size, (100, 100, 100), moment_of_inertia=bc.PymunkPhysicsEngine.MOMENT_INF,
                         collision_type="Wall", type_=bc.PymunkPhysicsEngine.STATIC)
        a = size.__div__(2)
        b = size.__div__(-2)
        c = Vec2(size.x / 2, size.y / -2)
        d = Vec2(size.x / -2, size.y / 2)
        p = self.pos


class Trigger:
    def __init__(self, on_enter, on_exit, pos: Vec2, radius=50, sprite=None):
        if sprite == None:
            self.shape = arcade.SpriteCircle(50, (0, 0, 0), False, *pos.list)
        else:
            self.shape = sprite
        self.pos = pos
        bc.phys.add_sprite(self.shape, collision_type="Trigger")
        physics_object = bc.phys.get_physics_object(self.shape)
        physics_object.shape.sensor = True
        first_time = False

        def exit_handler(*_):
            on_exit(*_)

        def enter_handler(*_):
            nonlocal first_time
            if first_time:
                on_enter(*_)
                return True
            else:
                first_time = True
                return False

        bc.phys.add_collision_handler(
            "Trigger",
            "Player",
            begin_handler=enter_handler,
            separate_handler=exit_handler
        )

    @property
    def pos(self):
        return self._pos

    @pos.setter
    def pos(self, value: Vec2):
        self._pos = value
        self.shape.center_x, self.shape.center_y = value.list

    def die(self):
        self.shape.remove_from_sprite_lists()


class InteractiveEntity(bc.Entity):
    def __init__(self, pos: Vec2):
        super().__init__(
            pos,
            Vec2(50, 50),
            (203, 138, 39),
            type_=bc.PymunkPhysicsEngine.STATIC
        )
        self.player_inside = False

        def on_player_exit(*_):
            self.player_inside = False

        def on_player_enter(*_):
            self.player_inside = True

        self.trigger = Trigger(on_player_enter, on_player_exit, pos)

    def on_draw(self):
        if self.player_inside:
            arcade.draw_text(f"PRESS E TO USE, (WIP)", *self.pos.list)


class Item:
    def __init__(self, pos: Vec2, item: int):
        self.pos = pos
        self.player_entered = False
        self.item = item

        def on_player_exit(*_):
            pass
            # self.player_entered = False

        def on_player_enter(trig, player, *_):
            self.player_entered = True
            player = player.parent
            player.items.append(self.item)
            player.update_items()

            self.trigger.die()

        self.trigger = Trigger(on_player_enter, on_player_exit, pos, 10)
    def draw(self):
        arcade.draw_text(f"item {self.item}", *self.pos.list)


@dataclass
class WeapDrawItem:
    name: str
    def draw(self, x, y):
        arcade.draw_text(self.name, x, y)

class Enemy(bc.Entity):
    def __init__(self, pos: Vec2, target: bc.Entity):
        super().__init__(
            pos, Vec2(45, 45), (155, 0, 0),
            collision_type="Enemy",
            friction=0.3
        )
        self.target = target
        self.health = 100
        self.inv = False
        self.damage = 25
        self.type_ = 1
        self.rect.parent = self

    def update(self, dt):
        super().update(dt)

        if self.health <= 0:
            self.die()
            enemies.remove(self)
            return

        # Direct chase toward player
        dp = self.target.pos - self.pos
        if dp.magnitude > 0.01:
            at = math.atan2(dp.x, dp.y)
            self.angle = math.degrees(at)

            speed = 1300

            self.velocity = 1*Vec2(math.sin(at), math.cos(at)) * speed
            bc.phys.apply_force(self.rect, self.velocity.list)

    def draw(self):
        pass


class Player(bc.Entity):
    def __init__(self, pos: Vec2):
        super().__init__(pos, Vec2(45, 45), (0, 255, 0),
                         collision_type="Player", friction=0.0)
        self.keys = set()
        self.weapon_number = 0
        self.weapon_list = [Pistol(self), Riffle(self), MachinePistols(
            self), Shotgun(self), Crossbow(self), SniperRiffle(self)]
        self.active_weapon_sprite = arcade.SpriteList()
        # self.available_weapons = self.weapon_list
        self.available_weapons = [self.weapon_list[0]]
        self.health = 50
        self.rect.parent = self
        self.last_damage = 0
        self.shoot = False
        self.sources_damage = {}
        self.items = []

    def update_items(self):
        for item in self.items:
            if item < 5:
                self.available_weapons.append(self.weapon_list[item])
                self.items.remove(item)

    def set_angle(self, mouse_pos: Vec2):
        dp = self.pos - mouse_pos
        if dp.y:
            self.angle = math.degrees(math.atan2(dp.x, dp.y))
        else:
            self.angle = 90

    def update(self, dt: float):
        self.velocity *= 0.90
        dv = Vec2(0, 0)
        acc = 1000
        if arcade.key.W in self.keys:
            dv += Vec2(0, acc)
        if arcade.key.S in self.keys:
            dv += Vec2(0, -acc)
        if arcade.key.D in self.keys:
            dv += Vec2(acc, 0)
        if arcade.key.A in self.keys:
            dv += Vec2(-acc, 0)
        bc.phys.apply_force(self.rect, dv.list)

        weapon_number = self.weapon_number
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

        if self.weapon_number >= len(self.available_weapons):
            self.weapon_number = weapon_number
        for i in self.active_weapon_sprite:
            i.remove_from_sprite_lists()
        sprite = self.weapon_list[self.weapon_number].sprite
        self.active_weapon_sprite.append(sprite)
        bc.sprite_all_draw.append(sprite)
        # if self.velocity.magnitude() < acc * 10:
            # self.velocity += dv
        # update all childs
        if arcade.key.SPACE in self.keys or self.shoot:
            self.available_weapons[self.weapon_number].shoot()
        for wearpon in self.weapon_list:
            wearpon.update(dt)
        return super().update(dt)

    def take_damage(self, damage: int | float, source):
        if source in self.sources_damage.keys():
            if time.time() - self.sources_damage[source] > 1:
                self.health -= damage
                self.sources_damage[source] = time.time()
        else:
            self.health -= damage
            self.sources_damage[source] = time.time()

    def on_key_press(self, key):
        self.keys.add(key)

    def on_key_release(self, key):
        if key in self.keys:
            self.keys.remove(key)


class Window(arcade.Window):
    def __init__(self):
        super().__init__(1920, 1080, "game for game jam", fullscreen=True)
        self.bloom = arcade.experimental.BloomFilter(
            self.width, self.height, 20)
        self.mouse_pos = Vec2(1, 1)
        # self.walls = [Wall(Vec2(i.x, i.y), Vec2(50, 500)) for i in l1]

        self.vig = helpers.Shader(
            "shaders/vignette.glsl", self.ctx, w=self.width, h=self.height)
        self.pix = helpers.Shader(
            "shaders/pixelation.glsl", self.ctx, w=self.width, h=self.height)
        self.bg = helpers.Shader(
            "shaders/bg.glsl", self.ctx, w=self.width, h=self.height)

        self.ammo_indicator = helpers.Shader("shaders/ammo_left.glsl", self.ctx, w=self.width, h=self.height)
        self.ammo_indicator["reload"] = 1

        self.setup_collision_handlers()

        self.vig_alp = 1.5
        self.vig["alpha"] = self.vig_alp
        self.pix["cell_size"] = 5.0
        self.vig["inner_radius"] = 0.0
        self.vig["outer_radius"] = 1.0
        # self.bg["screen_size"] = (1920, 1080)

        self.screen_size = Vec2(self.width, self.height)

        aspect_ratio = self.width/self.height
        deadzone_size = 00
        self.camera_deadzone = Vec2(
            deadzone_size*aspect_ratio, deadzone_size/aspect_ratio)
        self.setup()

        # PARTIVCLES
        self.particle_system = particles.ParticleSystem()


    def setup(self):
        global enemies, barriers
        enemies.clear()
        walls.clear()
        for sprite in list(bc.sprite_all_draw):
            if hasattr(sprite, "parent") and hasattr(sprite.parent, "die"):
                sprite.parent.die()
            else:
                sprite.remove_from_sprite_lists()

        self.test_int = InteractiveEntity(Vec2(180, 0))
        self.level = helpers.LevelLoader.load_level("level.lvl")
        self.player = Player(self.level.spawn.pos)
        self.item_2 = Item(Vec2(-200, 0), 1)
        for wall in self.level.walls:
            walls.append(Wall(wall.pos, wall.size).rect)
        
        for enemy in self.level.enemies:
            e = Enemy(enemy.pos, self.player)
            enemies.append(e)
        self.camera = arcade.Camera2D(position=self.player.pos.list)
        self.camera_pos = self.player.pos

        self.health_bar = bc.Bar(
            self.get_world_from_screen(Vec2(10, 10)),
            Vec2(300, 20),
            (255, 10, 10),
            (100, 100, 100),
            50,
            50
        )

        self.inventory_pos = Vec2(10, self.height-85)
        pos = self.get_world_from_screen(self.inventory_pos)
        items = self.player.available_weapons
        self.item_bar = bc.ItemBar(pos, items, 50, 10)

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
            bullet_sprite = sprite_from_arbiter(arbiter, 0)
            bullet_sprite.parent.die()
            enemy_sprite = sprite_from_arbiter(arbiter, 1)
            enemy_sprite.parent.health -= bullet_sprite.parent.damage
            self.particle_system.create_explosion(Vec2(*bullet_sprite.position), 50)

        def en_player_hit_handler(sprite_a, sprite_b, arbiter, space, data):
            player_sprite = sprite_from_arbiter(arbiter, 0)
            if hasattr(player_sprite, "parent"):
                player = player_sprite.parent
                enemy = sprite_from_arbiter(arbiter, 1)
                player.take_damage(enemy.parent.damage, enemy.parent)
                self.health_bar.value = player.health

        def wall_hit_handler(sprite_a, sprite_b, arbiter, space, data):
            """ Called for bullet/wall collision """
            # TODO add checks for types
            bullet_sprite = sprite_from_arbiter(arbiter, 0)
            # bullet_sprite.remove_from_sprite_lists()
            # bullet_sprite.parent.die()

        bc.phys.add_collision_handler(
            "Player",
            "Enemy",
            post_handler=en_player_hit_handler
        )
        bc.phys.add_collision_handler(
            "Bullet",
            "Enemy",
            post_handler=enemy_hit_handler
        )
        bc.phys.add_collision_handler(
            "Bullet",
            "Wall",
            post_handler=wall_hit_handler
        )

    def on_resize(self, width: int, height: int):
        self.bloom = arcade.experimental.BloomFilter(width, height, 20)
        self.pix.resize(width, height)
        self.screen_size = Vec2(width, height)
        self.ammo_indicator["start_pos"] = [10, self.height-85]

        self.vig.resize(width, height)
        # self.bg["screen_size"] = (width, height)
        self.bg.resize(width, height)
        self.ammo_indicator.resize(width, height)

        self.camera = arcade.Camera2D()

    def all_draw(self):
        bc.sprite_all_draw.draw()
        self.particle_system.draw()

    def draw_ui(self):
        self.health_bar.update_pos(self.get_world_from_screen(Vec2(10, 10)))
        self.health_bar.draw()
        for enemy in enemies:
            enemy.draw()

        name_pos = self.get_world_from_screen(Vec2(10, self.height-15))
        weapon = self.player.available_weapons[self.player.weapon_number]
        name = weapon.__repr__()
        # arcade.draw_text(f"Weapon: {name}", name_pos.x, name_pos.y)
        bullets = weapon.bul_count_now
        self.ammo_indicator["repeat_count"] = bullets
        if bullets == 0:
            self.ammo_indicator["repeat_count"] = weapon.prop.bullet_count
            reload = (time.time() - weapon.last_shot)/weapon.prop.reload_time
            self.ammo_indicator["reload"] = reload
        else:
            self.ammo_indicator["reload"] = 1
        if not self.item_2.player_entered:
            self.item_2.draw()
        # arcade.draw_text(
            # f"bullets left: {bullets}", name_pos.x, name_pos.y - 65)
        # if bullets == 0:
            # arcade.draw_text(
                # f"reload {weapon.prop.reload_time - (time.time() - weapon.last_shot):.2f}", name_pos.x, name_pos.y - 85)
        self.item_bar.bottom_left_pos = self.get_world_from_screen(self.inventory_pos)

        number = len(self.player.available_weapons)
        self.item_bar.item_count = number
        self.item_bar.active = self.player.weapon_number
        items_all = len(self.item_bar.items)
        if number >= items_all:
            for _ in range(number-items_all):
                self.item_bar.items.append(None)
        self.item_bar.draw()
        self.test_int.on_draw()

    def on_draw(self):
        self.camera.use()
        self.bg["pos"] = self.camera_pos.list
        self.pix["screen_size"] = (self.screen_size * self.camera.zoom).list
        self.vig["screen_size"] = (self.screen_size * self.camera.zoom).list
        # self.fbo.clear(color = (255, 255, 255))
        self.vig.clear()
        self.pix.clear()
        self.bg.clear()
        self.ammo_indicator.clear()
        
        with self.ammo_indicator:
            with self.vig:
                with self.pix:
                    self.bg.draw()
                    self.all_draw()
                self.pix.draw()
            self.vig.draw()
            self.draw_ui()
        self.ammo_indicator.draw()
        # self.tex.use(0)
        # self.quad_fs.render(self.pixelation)
        # self.quad_fs.render(self.vignette)

    def on_update(self, dt: float):
        bc.phys.step(1/60)
        
        self.particle_system.update(dt)

        self.player.update(dt)
        if self.player.health <= 0:
            self.setup()
        self.player.set_angle(self.mouse_pos)
        for enemy in enemies:
            if enemy.rect in bc.phys.sprites:
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
        self.camera.position = new_camera_pos.list
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

    def on_mouse_press(self, x, y, button, *_):
        if button == 1:
            self.player.shoot = True

    def on_mouse_release(self, x, y, button, *_):
        if button == 1:
            self.player.shoot = False
        # enemy = Enemy(pos, self.player)
        # enemies.append(enemy)

    def on_mouse_motion(self, x, y, *_):
        pos = self.get_world_from_screen(Vec2(x, y))
        self.mouse_pos = pos


def main():
    win = Window()
    win.run()


if __name__ == "__main__":
    main()
