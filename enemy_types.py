import arcade
import base_classes as bc
from base_classes import Vec2
import math
from weapons import Weapon, WeaponData

"""
enemy types:
    1. kamikaze
    2. trooper
    3. grenadier
    4. small
    5. swordsman (mini-boss)
"""

enemies = []

class Bullet(bc.Entity):
    def __init__(
        self, pos: Vec2, size: Vec2, vel: float, angle: float, damage: float, owner
    ):
        color = (235, 155, 90)

        angle = -angle + 90
        ra = math.radians(angle)
        self.pos = pos
        dir = Vec2(math.cos(ra)/2, math.sin(ra))
        size_p = max(owner.rect.width, owner.rect.height)
        self.pos += size_p * dir
        self.rect = arcade.SpriteSolidColor(
            size.y, size.x, self.pos.x, self.pos.y, color, angle)
        self.rect.parent = self
        bc.sprite_all_draw.append(self.rect)
        bc.phys.add_sprite(
            self.rect, 0.09, collision_type="EnemyBullet", elasticity=0.1)
        bc.phys.update_sprite(self.rect)
        self.owner = owner
        self.damage = damage
        self.angle = angle
        self.lifetime = 0
        self.die_calls = []
        self.died = False
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
        vel = Vec2(*vel).magnitude
        # vel = self.rect.rescale_xy_relative_to_point
        if 0 < vel < 200:
            self.die()

    def die(self):
        self.died = True
        if self.rect in bc.phys.sprites:
            bc.phys.remove_sprite(self.rect)
        for call in self.die_calls:
            call(self)
        if self.rect in bc.sprite_all_draw:
            bc.sprite_all_draw.remove(self.rect)
class TrooperRifle(Weapon):
    def __init__(self, parent):
        super().__init__(parent)
        self.prop = WeaponData(
                0.1,
                25,
                1,
                15,
                15,
                Vec2(5, 10),
                15
                )
        self.bul_class = Bullet

class Enemy(bc.Entity):
    def __init__(self, pos: Vec2, target: bc.Entity, ps):
        super().__init__(
            pos, Vec2(45, 45), (155, 0, 0),
            collision_type="Enemy",
            friction=0.3
        )
        self.target = target
        self.health = 100
        self.inv = False
        self.damage = 25
        self.type_ = 2
        self.ps = ps
        self.rect.parent = self
        self.explosion_time = 0
        if self.type_ == 2:
            self.weapon = TrooperRifle(self)
            self.damage = self.weapon.prop.damage
        # elif self.type
    
    def move_to_target(self):
        # Direct chase toward player
        dp = self.target.pos - self.pos
        if dp.magnitude > 0.01:
            at = math.atan2(dp.x, dp.y)
            speed = 1300
            self.velocity = 1*Vec2(math.sin(at), math.cos(at)) * speed
            bc.phys.apply_force(self.rect, self.velocity.list)

    def uni_die(self):
        self.die()
        enemies.remove(self)

    def kamikaze(self):
        if (self.target.pos - self.pos).magnitude < 500:
            self.move_to_target()
            if (self.pos - self.target.pos).magnitude < 65:
                self.ps.create_explosion(self.pos)
                bc.DamageZone(self.pos, 0.25, 1000, 80)
                self.uni_die()
    def trooper(self):
        dist = (self.target.pos - self.pos).magnitude
        if dist < 500:
            if dist > 200:
                self.move_to_target()
            self.weapon.shoot()

    def update(self, dt):
        super().update(dt)

        dp = self.target.pos - self.pos
        if dp.magnitude > 0.01:
            at = math.atan2(dp.x, dp.y)
            self.angle = math.degrees(at)
        if self.type_ == 1:
            self.kamikaze()
        elif self.type_ == 2:
            self.trooper()
        else:
            self.move_to_target()
        if self.health <= 0:
            self.uni_die()
            return
        self.weapon.update(dt)

    def draw(self):
        pass
