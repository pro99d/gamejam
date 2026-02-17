from dataclasses import dataclass
import base_classes as bc
from base_classes import Vec2
import time
import math
import arcade
import random

@dataclass
class WearponData:
    reload_time: float
    bullet_count: int
    reload: float
    damage: float
    spread: float
    size: Vec2
    lifetime: float
    
class Wall(bc.Entity):
    def __init__(self, pos: Vec2, size: Vec2= Vec2(50, 50)):
        super().__init__(pos, size, (100, 100, 100), collision_type= arcade.PymunkPhysicsEngine.STATIC)

        
l1 = [Vec2(100, 200), Vec2(200, 200)]

class Wearpon:
    def __init__(self, parent: bc.Entity):
        self.parent = parent
        self.sprite = arcade.SpriteSolidColor(10, 50, 0, 0, arcade.color.GRAY)
        self.bul_count_now = self.prop.bullet_count
        bc.sprite_all_draw.append(self.sprite)
        self.prop = WearponData(
            bullet_count = 6
            reload= 0.1,
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
        if (time.time() - self.last_shot >= self.prop.reload) and (self.bul_count_now > 0 or  time.time() - self.last_shot >= self.prop.reload_time):
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
            self.bul_count_now -= 1
        elif self.bul_count_now == 0 and time.time() - self.last_shot >:
            
    def die(self):
        bc.sprite_all_draw.remove(self.sprite)
        for bullet in self.bullets:
            bullet.die()

class Pistol(Wearpon):
    def __init__(self, parent):
        self.bullets = []
        super().__init__(parent)
        self.prop = WearponData(
            reload_time = 1.5,
            bullet_count = 6,
            reload= 0.3,
            damage= 15.0,
            spread= 15.0,
            size= Vec2(5, 10),
            lifetime= 5.0
        )
    
    def update(self, dt):
        super().update(dt)

class riffle(Wearpon):
    def __init__(self, parent):
        super().__init__(parent)
        self.bullets = []
        self.prod = WearponData(
            reload_time=2,
            reload = 0.6,
            damage = 35.0,
            spread = 3.0,
            size= Vec2(8,15),
            lifetime=8.8,
        )
    def update(self, dt):
        super().update(dt)
        