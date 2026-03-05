import arcade
import base_classes as bc
from base_classes import Vec2
import math

"""
enemy types:
    1. kamikaze
    2. trooper
    3. grenadier
    4. small
    5. swordsman (mini-boss)
"""

enemies = []

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
        self.type_ = 1
        self.ps = ps
        self.rect.parent = self
        self.explosion_time = 0
    
    def move_to_target(self):
        # Direct chase toward player
        dp = self.target.pos - self.pos
        if dp.magnitude > 0.01:
            at = math.atan2(dp.x, dp.y)
            self.angle = math.degrees(at)
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

    def update(self, dt):
        super().update(dt)
        if self.type_ == 1:
            self.kamikaze()
        else:
            self.move_to_target()
        if self.health <= 0:
            self.uni_die()
            return

    def draw(self):
        pass
