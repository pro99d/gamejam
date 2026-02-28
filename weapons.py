from dataclasses import dataclass
import base_classes as bc
from base_classes import Vec2
import time
import math
import arcade
import random

class Bullet(bc.Entity):
    def __init__(
        self, pos: Vec2, size: Vec2, vel: float, angle: float, damage: float, owner
    ):
        color = (235, 155, 90)



        angle = -90-angle
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
        self.died = False
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
        if self.died:
            return
        vel = bc.phys.get_physics_object(self.rect).body.velocity
        vel = Vec2(*vel).magnitude()
        # vel = self.rect.rescale_xy_relative_to_point
        if 0<vel < 200:
            self.die()

    def die(self):
        self.died = True
        if self.rect in bc.phys.sprites:
            bc.phys.remove_sprite(self.rect)
        for call in self.die_calls:
            call(self)
        if self.rect in bc.sprite_all_draw:
            bc.sprite_all_draw.remove(self.rect)
        # self.rect.kill()
        # self.owner.bullets.remove(self)

@dataclass
class WearponData:
    reload_time: float
    bullet_count: int
    reload: float
    damage: float
    spread: float
    size: Vec2
    lifetime: float


class Wearpon:
    def __init__(self, parent: bc.Entity):
        self.parent = parent
        self.sprite = arcade.SpriteSolidColor(10, 50, 0, 0, arcade.color.GRAY)
        bc.sprite_all_draw.append(self.sprite)
        self.prop = WearponData(
            bullet_count = 6,
            reload= 0.1,
            damage= 15.0,
            spread= 15.0,
            size= Vec2(5, 10),
            lifetime= 5.0,
            reload_time=1
        )
        self.bul_count_now = self.prop.bullet_count
        self.last_shot = 0
        self.bullets = []
        self.update(0)
    def __repr__(self):
        return self.__class__.__name__

    def update(self, dt):
        self.sprite.center_x = self.parent.rect.center_x
        self.sprite.center_y = self.parent.rect.center_y
        self.sprite.angle = self.parent.angle
        self.pos = Vec2(self.sprite.center_x, self.sprite.center_y)
        self.angle = self.sprite.angle-90

        for bullet in self.bullets:
            bullet.update(dt)
            if bullet.lifetime > self.prop.lifetime:
                bullet.die()
                if bullet in self.bullets:
                    self.bullets.remove(bullet)
        if time.time() - self.last_shot >= self.prop.reload_time and self.bul_count_now == 0:
            self.bul_count_now = self.prop.bullet_count

    def shoot(self):
        if (time.time() - self.last_shot >= self.prop.reload) and self.bul_count_now > 0:
            bullet = Bullet(

                    pos= self.pos,
                    size= self.prop.size,
                    vel= 1000,
                    angle= self.angle + random.uniform(-self.prop.spread/2, self.prop.spread/2)+90,
                    damage= self.prop.damage,
                    owner= self.parent
                )
            bullet.die_calls.append(lambda _: self.bullets.remove(bullet))
            self.bullets.append(bullet)
            self.last_shot = time.time()
            self.bul_count_now -= 1


    def die(self):
        bc.sprite_all_draw.remove(self.sprite)
        for bullet in self.bullets:
            bullet.die()

class Pistol(Wearpon):
    def __init__(self, parent):
        super().__init__(parent)
        self.prop = WearponData(
            reload_time = 1.5,
            bullet_count = 12,
            reload= 0.3,
            damage= 15.0,
            spread= 15.0,
            size= Vec2(5, 10),
            lifetime= 5.0
        )
        self.bul_count_now = self.prop.bullet_count
    def update(self, dt):
        super().update(dt)

class Riffle(Wearpon):
    def __init__(self, parent):
        super().__init__(parent)
        self.prod = WearponData(
            reload_time=2,
            bullet_count = 5,
            reload = 0.6,
            damage = 35.0,
            spread = 3.0,
            size= Vec2(8,15),
            lifetime=8.8,
        )
        self.bul_count_now = self.prop.bullet_count
    def update(self, dt):
        super().update(dt)

class MachinePistols(Wearpon):
    def __init__(self, parent):
        super().__init__(parent)
        self.prop = WearponData(
            reload_time=3,
            bullet_count=60,
            reload = 0.08,
            damage = 5,
            spread = 20,
            size = Vec2(3,7),
            lifetime = 4.0,
        )
        self.bul_count_now = self.prop.bullet_count
    def shoot(self):
        for _ in range(2):
            super().shoot()
        
    def update(self, dt):
        super().update(dt)

class Shotgun(Wearpon):
    def __init__(self,parent):
        super().__init__(parent)
        self.prop = WearponData(
            reload_time=3,
            bullet_count=5,
            reload = 0.5,
            damage = 8,
            spread = 20,
            size = Vec2(3,7),
            lifetime = 4.0,
        )
        self.bul_count_now = self.prop.bullet_count
    def shoot(self):
        if (time.time() - self.last_shot >= self.prop.reload) and (self.bul_count_now > 0 or  time.time() - self.last_shot >= self.prop.reload_time):
            for _ in range(6):
                self.bullets.append(
                    Bullet(

                        pos= self.pos,
                        size= self.prop.size,
                        vel= 1000,
                        angle= self.angle + random.uniform(-self.prop.spread/2, self.prop.spread/2)+90,
                        damage= self.prop.damage,
                        owner= self.parent
                    )
                )
            self.last_shot = time.time()
            self.bul_count_now -= 1
    def update(self, dt):
        super().update(dt)
        
class Crossbow(Wearpon):
    def __init__(self,parent):
        super().__init__(parent)
        self.prop = WearponData(
            reload_time=1.5,
            bullet_count=1,
            reload = 1.5,
            damage = 60,
            spread = 0.01,
            size = Vec2(4,12),
            lifetime = 20.0,
        )
        self.bul_count_now = self.prop.bullet_count
    def update(self, dt):
        super().update(dt)

class SniperRiffle(Wearpon):
    def __init__(self,parent):
        super().__init__(parent)
        self.prop = WearponData(
            reload_time=2.0,
            bullet_count=1,
            reload = 2.0,
            damage = 80,
            spread = 0.001,
            size = Vec2(3,10),
            lifetime = 20.0,
        )
        self.bul_count_now = self.prop.bullet_count
    def update(self, dt):
        super().update(dt)    
