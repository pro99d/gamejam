import arcade
from dataclasses import dataclass
import base_classes as bc
from base_classes import Vec2
import time
import math
import random
import phys

enemies = []

class Bullet(bc.Entity):
    def __init__(self, pos: Vec2, size: Vec2, vel: float, angle: float, damage: float, owner):
        color = (235, 155, 90)
        super().__init__(
            pos= pos,
            size= size,
            color= color,
            mass= 0.09
        )
        self.owner = owner
        self.damage = damage
        self.angle = angle
        angle = math.radians(-angle-90)
        self.velocity = Vec2(math.cos(angle)*vel, math.sin(angle)*vel)
        self.lifetime = 0

    def get_nearest_enemy(self, enemies):
        min_dist_sq = float("inf")
        e = None
        for enemy in enemies:
            if enemy == self.owner:
                continue
            dx = self.pos.x - enemy.pos.x
            dy = self.pos.y - enemy.pos.y
            dist_sq = dx*dx+dy*dy
            if  dist_sq <= min_dist_sq:
                min_dist_sq = dist_sq
                e = enemy 
        return e

    def update(self, dt, enemies: list):
        self.lifetime+=dt
        super().update(dt)
        hit = False
        if self.owner in enemies:
            enemies.remove(self.owner)
        en = self.get_nearest_enemy(enemies)
        if en:
            if not en.inv:
                if math.dist(self.pos.__list__(), en.pos.__list__()) <= 60:
                    en.health -= self.damage
                    hit = True
        return hit

@dataclass
class WearponData:
    reload: float
    damage: float
    spread: float
    size: Vec2
    lifetime: float
    
class Wall(bc.Entity):
    def __init__(self, pos: Vec2, size: Vec2= Vec2(50, 50)):
        super().__init__(pos, size, (100, 100, 100))
        print(size)
        a = size.__div__(2)
        b = size.__div__(-2)
        c = Vec2(size.x/2, size.y/-2)
        d = Vec2(size.x/-2, size.y/2)
        self.hitbox = phys.Hitbox([a, b, c, d])
        
l1 = [Vec2(100, 200), Vec2(200, 200)]

class Wearpon:
    def __init__(self, parent: bc.Entity):
        self.parent = parent
        self.sprite = arcade.SpriteSolidColor(10, 50, 0, 0, arcade.color.GRAY)
        bc.sprite_all_draw.append(self.sprite)
        self.prop = WearponData(
            reload= 1.0,
            damage= 15.0,
            spread= 15.0,
            size= Vec2(5, 10),
            lifetime= 5.0
        )
        self.last_shot = 0
        self.bullets = []
        self.update(0)

    def update(self, dt):
        self.sprite.center_x = self.parent.rect.center_x
        self.sprite.center_y = self.parent.rect.center_y
        self.sprite.angle = self.parent.angle
        self.pos = Vec2(self.sprite.center_x, self.sprite.center_y)
        self.angle = self.sprite.angle-90

        for bullet in self.bullets:
            bullet.update(dt, [])
            if bullet.lifetime > self.prop.lifetime:
                bullet.die()
                self.bullets.remove(bullet)


    def shoot(self):
        if time.time() - self.last_shot >= self.prop.reload:
            self.bullets.append(
                Bullet(
                    pos= self.pos,
                    size= self.prop.size,
                    vel= 1000,
                    angle= self.angle + random.uniform(-self.prop.spread/2, self.prop.spread/2)+90,
                    damage= self.prop.damage,
                    owner= self
                )
            )
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
            reload= 1.0,
            damage= 15.0,
            spread= 15.0,
            size= Vec2(5, 10),
            lifetime= 5.0
        )
    def update(self, dt):
        super().update(dt)


class Player(bc.Entity):
    def __init__(self, pos: Vec2):
        super().__init__(pos, Vec2(50, 50), (0, 255, 0))
        self.keys = set() 
        self.pistol = Pistol(self)
        self.health = 50

    def set_angle(self, mouse_pos: Vec2):

        dp = self.pos -mouse_pos
        if dp.y:
            self.angle = math.degrees(math.atan2(dp.x, dp.y))
        else:
            self.angle = 90


    def update(self, dt: float):
        self.velocity *= 0.90
        dv = Vec2(0, 0)
        acc = 60
        if arcade.key.W in self.keys:
            dv += Vec2(0, acc)
        if arcade.key.S in self.keys:
            dv += Vec2(0, -acc)
        if arcade.key.D in self.keys:
            dv += Vec2(acc, 0)
        if arcade.key.A in self.keys:
            dv += Vec2(-acc, 0)
        self.velocity += dv
        #update all childs
        self.pistol.update(dt)
        if arcade.key.SPACE in self.keys:
            self.pistol.shoot()

        return super().update(dt)
    def on_key_press(self, key):
        self.keys.add(key)
    def on_key_release(self, key):
        self.keys.remove(key)

class Window(arcade.Window):
    def __init__(self):
        super().__init__(800, 600, "game for game jam")
        self.bloom = arcade.experimental.BloomFilter(self.width, self.height, 20)
        self.player = Player(Vec2(200, 400)) 
        self.mouse_pos = Vec2(1, 1)
        self.walls = [Wall(Vec2(i.x, i.y)) for i in l1]
        self.physics_engine: phys.Engine = phys.Engine(2)
        self.physics_engine.add_ent(self.player)
        for wall in self.walls:
            self.physics_engine.add_hitbox(wall.hitbox)    

    def on_resize(self, width: int, height: int):
        self.bloom = arcade.experimental.BloomFilter(width, height, 20)

    def all_draw(self):
        bc.sprite_all_draw.draw()

    def on_draw(self):
        self.clear()
        # self.bloom.fbo.use()
        self.bloom.fbo.clear()
        # with self.bloom.fbo: 
        self.all_draw()
        self.ctx.screen.use()
        # self.bloom.draw(0, self.ctx.screen)

    def on_update(self, dt: float):
        self.physics_engine.update(dt)
        # self.player.update(dt)
        self.player.set_angle(self.mouse_pos)

    def on_key_press(self, key, *_):
        if key == arcade.key.Q:
            arcade.close_window()
        self.player.on_key_press(key)
    def on_key_release(self, key, mod):
        self.player.on_key_release(key)
    def on_mouse_motion(self, x, y, *_):
        self.mouse_pos = Vec2(x, y)


def main():
    win = Window()
    win.run()


if __name__ == "__main__":
    main()
