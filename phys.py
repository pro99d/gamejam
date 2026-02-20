from base_classes import Vec2
import math
import arcade
from base_classes import Entity
from dataclasses import dataclass

fl = Falsfl = False
def distance_point_to_line(P: Vec2, A: Vec2, B: Vec2) -> float:
    AB = B - A
    AP = P - A
    AB_magnitude = math.sqrt(AB.x**2 + AB.y**2)
    if AB_magnitude == 0:
        return math.sqrt(AP.x**2 + AP.y**2)
    projection_length = (AP.x * AB.x + AP.y * AB.y) / AB_magnitude
    projection_point = A + AB * (projection_length / AB_magnitude)
    res =  (P - projection_point)
    return math.sqrt(res.x**2 + res.y ** 2)

class Line:
    def __init__(self, a: Vec2, b: Vec2):
        self.a = a
        self.b = b
        dp = a-b
        self.norm = dp.normalize().rotate(1.5707)

@dataclass
class Hitbox:
    points: list[Vec2]
    def _is_collide(self, p: Vec2, r: float):
        for i in range(len(self.points)-1):
            a = self.points[i]
            b = self.points[i+1]
            ab = b - a
            ap = p - a
            ab_mag = ab.magnitude()
            if ab_mag == 0:
                if ap.magnitude()**2 <= r:
                    dp = a-b
                    return dp.normalize().rotate(1.5707)
            projection_length = (ap.x * ab.x + ap.y * ab.y) / ab_mag 
            projection_point = a + ab * (projection_length / ab_mag)
            res =  (p - projection_point)
            if res.x**2 + res.y ** 2 <= r:
                dp = a-b
                return dp.normalize().rotate(math.radians(90))
        return False


class Engine:
    def __init__(self, k: float):
        self.k = k
        self.entities: list[Entity] = []
        self.hitboxes: list[Hitbox] = []

    def remove_ent(self, entity: Entity):
        if entity in self.entities:
            self.entities.remove(entity)

    def add_hitbox(self, hitbox: Hitbox):
        self.hitboxes.append(hitbox)

    def add_ent(self, entity: Entity):
        self.entities.append(entity)
        entity.die_calls.append(self.remove_ent)

    def update(self, dt: float):
        for hitbox in self.hitboxes:
            for entity in self.entities:
                norm = hitbox._is_collide(entity.pos, entity.radius)
                if norm:
                    entity.velocity += self.k * norm * entity.velocity
                
        for entity in self.entities:
            entity.update(dt)


class Window(arcade.Window):
    def __init__(self):
        super().__init__(800, 600, "game for game jam")
        self.pos = Vec2(200, 400) 
        self.vel = Vec2(100, -50)
        self.r = 25    
        self.a = Vec2(500, 350)
        self.b = Vec2(180, 350)
        dp = self.a-self.b
        self.norm = dp.normalize().rotate(math.radians(90))
    
    def collide(self):
        # norm90 = self.norm.rotate(math.radians(90)).normalize()
        print(self.norm)
        # angle = self.norm.angle(self.vel)
        # new = norm90.rotate()
        # new = new.normalize()
        print(self.vel)
        self.vel += 2*self.norm* self.vel
        print(self.vel)

    def on_draw(self):
        self.clear()
        arcade.draw_circle_filled(self.pos.x, self.pos.y, self.r, arcade.color.ORANGE)
        arcade.draw_line(self.a.x, self.a.y, self.b.x, self.b.y, arcade.color.RED, 2)

    def on_update(self, dt: float):
        global fl
        self.pos += self.vel*dt
        if distance_point_to_line(self.pos, self.a, self.b) <= self.r and not fl:
            self.collide()
            fl = True

    def on_key_press(self, key, *_):
        if key == arcade.key.Q:
            arcade.close_window()

if __name__ == "__main__":
    win = Window()
    win.run()

