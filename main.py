import arcade
from dataclasses import dataclass
import base_classes as bc
from base_classes import Vec2
import time
import math
import random
import helpers

enemies = []


class Bullet(bc.Entity):
    def __init__(
        self, pos: Vec2, size: Vec2, vel: float, angle: float, damage: float, owner
    ):
        color = (235, 155, 90)



        angle = -angle
        ra = math.radians(angle)
        self.pos = pos
        dir = Vec2(math.cos(ra)/2, math.sin(ra))
        size_p = max(owner.rect.width, owner.rect.height)
        self.pos += size_p * dir
        self.rect = arcade.SpriteSolidColor(size.y, size.x, self.pos.x, self.pos.y, color, angle)
        self.rect.parent = self
        bc.sprite_all_draw.append(self.rect)
        bc.phys.add_sprite(self.rect, 0.09, collision_type= "Bullet", elasticity= 0.1)
        bc.phys.update_sprite(self.rect)
        self.owner = owner
        self.damage = damage
        self.angle = angle
        self.lifetime = 0
        self.die_calls = []
        # Calculate force based on angle and velocity
        # force = (Vec2(1, -1) * 2500).__list__()
        # print(force)
        bc.phys.apply_force(self.rect, [5500, 0])

        self.pos = Vec2(
                self.rect.center_x,
                self.rect.center_y,
                )
        # self.update(0)

    def update(self, dt):
        self.lifetime += dt
        vel = bc.phys.get_physics_object(self.rect).body.velocity
        vel = Vec2(*vel).magnitude()
        # vel = self.rect.rescale_xy_relative_to_point
        if 0<vel < 200:
            self.die()

    def die(self):
        for call in self.die_calls:
            call(self)
        if self.rect in bc.sprite_all_draw:
            bc.sprite_all_draw.remove(self.rect)
        # self.rect.kill()
        # self.owner.bullets.remove(self)

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


l1 = [Vec2(90, 200), Vec2(200, 200)]


class Wearpon:
    def __init__(self, parent: bc.Entity):
        self.parent = parent
        self.sprite = arcade.SpriteSolidColor(10, 50, 0, 0, arcade.color.GRAY)
        bc.sprite_all_draw.append(self.sprite)
        self.prop = WearponData(
            reload=1.0, damage=15.0, spread=15.0, size=Vec2(5, 10), lifetime=5.0
        )
        self.last_shot = 0
        self.bullets = []
        self.update(0)

    def update(self, dt):
        self.sprite.center_x = self.parent.rect.center_x
        self.sprite.center_y = self.parent.rect.center_y
        self.sprite.angle = self.parent.angle + 90
        self.pos = Vec2(self.sprite.center_x, self.sprite.center_y)
        self.angle = self.sprite.angle

        for bullet in self.bullets:
            bullet.update(dt)
            if bullet.lifetime > self.prop.lifetime:
                bullet.die()
                self.bullets.remove(bullet)

    def shoot(self):
        if time.time() - self.last_shot >= self.prop.reload:
            f = Vec2(math.cos(math.radians(90+self.angle)), math.sin(math.radians(self.angle+90)))
            r = max(self.parent.rect.width, self.parent.rect.height) / 2
            f*=r

            bullet = Bullet(
                    pos=self.pos + f,
                    size=self.prop.size,
                    vel=1000,
                    angle=self.angle
                    + random.uniform(-self.prop.spread / 2,
                                     self.prop.spread / 2)
                    + 90,
                    damage=self.prop.damage,
                    owner=self.parent,
                )
            self.bullets.append(bullet)
            self.last_shot = time.time()

    def die(self):
        bc.sprite_all_draw.remove(self.sprite)
        for bullet in self.bullets:
            bullet.die()


class Pistol(Wearpon):
    def __init__(self, parent):
        self.bullets = []
        super().__init__(parent)
        self.prop = WearponData(
            reload=0.1, damage=15.0, spread=15.0, size=Vec2(5, 10), lifetime=5.0
        )

    def update(self, dt):
        super().update(dt)


class Enemy(bc.Entity):
    def __init__(self, pos: Vec2, target: bc.Entity):
        super().__init__(
            pos, Vec2(50, 50), (255, 0, 0),
            collision_type="Enemy",
        )
        self.target = target
        self.health = 100
        self.inv = False

    def update(self, dt):
        super().update(dt)

        dp = self.target.pos - self.pos
        self.angle = math.degrees(math.atan2(dp.x, dp.y))
        speed = 300
        self.velocity = dp.normalize()*speed
        bc.phys.apply_force(self.rect, self.velocity.__list__())


class Player(bc.Entity):
    def __init__(self, pos: Vec2):
        super().__init__(pos, Vec2(50, 50), (0, 255, 0),
                        moment_of_inertia=bc.PymunkPhysicsEngine.MOMENT_INF,
                        collision_type="player",
                        max_velocity=400)
        self.keys = set()
        self.pistol = Pistol(self)
        self.health = 50

    def set_angle(self, mouse_pos: Vec2):

        dp = mouse_pos - self.pos
        self.angle = math.degrees(math.atan2(dp.x, dp.y)) + 90

    def update(self, dt: float):
        self.velocity *= 0.90
        dv = Vec2(0, 0)
        acc = 4000
        if arcade.key.W in self.keys:
            dv += Vec2(0, acc)
        if arcade.key.S in self.keys:
            dv += Vec2(0, -acc)
        if arcade.key.D in self.keys:
            dv += Vec2(acc, 0)
        if arcade.key.A in self.keys:
            dv += Vec2(-acc, 0)
        bc.phys.apply_force(self.rect, dv.__list__())
        # if self.velocity.magnitude() < acc * 10:
            # self.velocity += dv
        # update all childs
        self.pistol.update(dt)
        if arcade.key.SPACE in self.keys:
            self.pistol.shoot()
        self.pos.x = self.rect.center_x
        self.pos.y = self.rect.center_y
        self.pistol.update(dt)
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
        self.player = Player(Vec2(400, 400))
        self.mouse_pos = Vec2(1, 1)
        self.walls = [Wall(Vec2(i.x, i.y), Vec2(50, 500)) for i in l1]

        self.vig = helpers.Shader("shaders/vignette.glsl", self.ctx, w= self.width, h= self.height)
        self.pix = helpers.Shader("shaders/pixelation.glsl", self.ctx, w= self.width, h= self.height)
        self.bg = helpers.Shader("shaders/bg.glsl", self.ctx, w= self.width, h= self.height)


        self.setup_collision_handlers()
        self.camera = arcade.Camera2D(position= self.player.pos.__list__())
        self.camera_pos = self.player.pos

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

        def enemy_hit_handler(sprite_a, sprite_b, arbiter, space, data):
            """ Called for bullet/enemy collision """
            # TODO add checks for types
            bullet_shape = arbiter.shapes[0]
            bullet_sprite = bc.phys.get_sprite_for_shape(bullet_shape)
            bullet_sprite.remove_from_sprite_lists()
            bullet_sprite.parent.die()


        def wall_hit_handler(sprite_a, sprite_b, arbiter, space, data):
            """ Called for bullet/wall collision """
            # TODO add checks for types
            bullet_shape = arbiter.shapes[0]
            bullet_sprite = bc.phys.get_sprite_for_shape(bullet_shape)
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

