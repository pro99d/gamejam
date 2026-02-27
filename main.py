import arcade
from dataclasses import dataclass
import base_classes as bc
from base_classes import Vec2
import time
import math
import random

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
        self.rect = arcade.SpriteSolidColor(size.x, size.y, self.pos.x, self.pos.y, color, angle)
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

    def die(self):
        for call in self.die_calls:
            call(self)
        if self.rect in bc.sprite_all_draw:
            bc.sprite_all_draw.remove(self.rect)

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


l1 = [Vec2(100, 200), Vec2(200, 200)]


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
        super().__init__(800, 600, "game for game jam")
        self.bloom = arcade.experimental.BloomFilter(
            self.width, self.height, 20)
        self.player = Player(Vec2(400, 400))
        self.mouse_pos = Vec2(1, 1)
        self.walls = [Wall(Vec2(i.x, i.y), Vec2(50, 500)) for i in l1]

        # for wall in self.walls:
        # physics_engine.add_hitbox(wall.hitbox)
        self.quad_fs = arcade.gl.geometry.quad_2d_fs()
        # Create texture and FBO
        self.tex = self.ctx.texture((self.width, self.height))
        self.fbo = self.ctx.framebuffer(color_attachments=[self.tex])
        # Put something in the framebuffer to start
        self.fbo.clear(color=arcade.color.ALMOND)
        self.setup_collision_handlers()
        self.init_pixelaion_shader()
        self.init_vignette_shader()
        self.camera = arcade.Camera2D()


    def setup_collision_handlers(self):

        def enemy_hit_handler(sprite_a, sprite_b, arbiter, space, data):
            """ Called for bullet/enemy collision """
            # TODO add checks for types
            bullet_shape = arbiter.shapes[0]
            # arbiter.ignore = True
            bullet_sprite = bc.phys.get_sprite_for_shape(bullet_shape)
            # bullet_sprite.remove_from_sprite_lists()
            # bullet_sprite.parent.die()


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


    def init_vignette_shader(self):
        with open("shaders/vignette.glsl") as f:
            frag = f.read()
        self.vignette = self.ctx.program(
            vertex_shader="""
                #version 330
                in vec2 in_vert;
                void main(){
                    gl_Position = vec4(in_vert, 0., 1.);
                }
                """,
            fragment_shader=frag,
        )
        self.vignette["t0"] = 0
        self.vignette["screen_size"] = (self.width, self.height)
    def init_pixelaion_shader(self):

        with open("shaders/pixelation.glsl") as f:
            frag = f.read()
        self.pixelation = self.ctx.program(
            vertex_shader="""
                #version 330
                in vec2 in_vert;
                void main(){
                    gl_Position = vec4(in_vert, 0., 1.);
                }
                """,
            fragment_shader=frag,
        )
        self.pixelation["t0"] = 0
        self.pixelation["cell_size"] = 3
        self.pixelation["screen_size"] = (self.width, self.height)

    def on_resize(self, width: int, height: int):
        self.bloom = arcade.experimental.BloomFilter(width, height, 20)
        self.tex = self.ctx.texture((width, height))
        self.fbo = self.ctx.framebuffer(color_attachments=[self.tex])
        self.pixelation["screen_size"] = (width, height)

    def all_draw(self):
        bc.sprite_all_draw.draw()

    def on_draw(self):
        self.clear()
        self.camera.use()
        self.fbo.clear(color = (255, 255, 255))
        with self.fbo:
            self.all_draw()
        self.tex.use(0)
        self.quad_fs.render(self.pixelation)
        self.quad_fs.render(self.vignette)

    def on_update(self, dt: float):
        bc.phys.step(1/60)
        self.player.update(dt)
        self.player.set_angle(self.mouse_pos)
        for enemy in enemies:
            enemy.update(dt)

    def on_key_press(self, key, *_):
        if key == arcade.key.Q:
            arcade.close_window()
        self.player.on_key_press(key)

    def on_key_release(self, key, mod):
        self.player.on_key_release(key)

    def on_mouse_press(self, x, y, *_):
        enemy = Enemy(Vec2(x, y), self.player)
        enemies.append(enemy)

    def on_mouse_motion(self, x, y, *_):
        self.mouse_pos = Vec2(x, y)


def main():
    win = Window()
    win.run()


if __name__ == "__main__":
    main()
