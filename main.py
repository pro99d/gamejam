import arcade
from dataclasses import dataclass
import base_classes as bc
from base_classes import Vec2
import time
import math
import random

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
        bc.pymunk.apply_impulse(self.rect, (self.velocity*self.mass).__list__())

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
        super().__init__(pos, size, (100, 100, 100), collision_type= arcade.PymunkPhysicsEngine.STATIC)

        
l1 = [Vec2(100, 200), Vec2(200, 200)]


class Player(bc.Entity):
    def __init__(self, pos: Vec2):
        super().__init__(pos, Vec2(50, 50), (0, 255, 0))
        self.keys = set()
        self.pistol = Pistol(self)
        self.riffle = riffle(self)
        self.shotgun = shotgun(self)
        self.crossbow = crossbow(self)
        self.sniper_riffle = sniper_riffle(self)
        self.machine_pistols = machine_pistols(self)
        self.weapon_number = weapon_number
        self.weapon_list = ['Pistol','riffle','machine_pistols','shotgun','crossbow','sniper_riffle']
    def set_angle(self, mouse_pos: Vec2):

        dp = self.pos -mouse_pos
        if dp.y:
            self.angle = math.degrees(math.atan2(dp.x, dp.y))
        else:
            self.angle = 90

    weapon_number = 1
    def update(self, dt: float):
        self.velocity *= 0.90
        dv = Vec2(0, 0)
        acc = 600
        if arcade.key.W in self.keys:
            dv += Vec2(0, acc)
        if arcade.key.S in self.keys:
            dv += Vec2(0, -acc)
        if arcade.key.D in self.keys:
            dv += Vec2(acc, 0)
        if arcade.key.A in self.keys:
            dv += Vec2(-acc, 0)
        if arcade.key.KEY_1 in self.keys:
            weapon_number = 1
        if arcade.key.KEY_2 in self.keys:
            weapon_number = 2
        if arcade.key.KEY_3 in self.keys:
            weapon_number = 3
        if arcade.key.KEY_4 in self.keys:
            weapon_number = 4
        if arcade.key.KEY_5 in self.keys:
            weapon_number = 5
        if arcade.key.KEY_6 in self.keys:
            weapon_number = 6
        self.update_vel(dv)
        #update all childs
        self.pistol.update(dt)
        if arcade.key.SPACE in self.keys:
            self.globals()[weapon_list[weapon_number]].shoot()

        return super().update(dt)
    def on_key_press(self, key):
        self.keys.add(key)
    def on_key_release(self, key):
        self.keys.remove(key)
class Window(arcade.Window):
    def __init__(self):
        super().__init__(800, 600, "game for game jam")
        self.bloom = arcade.experimental.BloomFilter(self.width, self.height, 20)
        self.player = Player(Vec2(200, 200)) 
        self.mouse_pos = Vec2(1, 1)
        self.walls = [Wall(Vec2(i.x, i.y)) for i in l1]

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
        bc.pymunk.step(1/60)
        self.player.update(dt)
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

