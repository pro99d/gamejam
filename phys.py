from base_classes import Vec2
import math
import arcade
from base_classes import Entity
from dataclasses import dataclass

fl = Falsfl = False
def is_on_left(a, b, c):
    return (b.x - a.x) * (c.y - a.y) - (b.y - a.y) * (c.x - a.x) > 0

def line_intersection(a, b, c, d):
    return (is_on_left(a, b, c) != is_on_left(a, b, d)) and (is_on_left(c, d, a) != is_on_left(c, d, b))

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
    def get_normal(self, a: Vec2, b: Vec2):
        edge = b - a
        norm = edge.normalize().rotate(math.radians(90))
        return norm
    def _is_collide(self, entity: Entity, dt):
        l = len(self.points)

        center_inside = True
        max_signed_dist = -float('inf')
        closest_norm = None

        for i in range(l):
            a = self.points[i%l]
            b = self.points[(i+1)%l]

            norm = self.get_normal(a, b)
            to_entity = entity.pos - a
            signed_dist = to_entity.dot(norm)

            if signed_dist > 0:
                center_inside = False

            if signed_dist > max_signed_dist:
                max_signed_dist = signed_dist
                closest_norm = norm

            if line_intersection(a, b, entity.pos, entity.pos+ entity.velocity*dt):
                return closest_norm, distance_point_to_line(entity.pos + entity.velocity*dt, a, b)
        if center_inside:
            penetration = -max_signed_dist + entity.radius
        else:
            for i in range(l):
                a = self.points[i%l]
                b = self.points[(i+1)%l]

                edge = b - a
                edge_len_sq = edge.x**2 + edge.y**2
                if edge_len_sq == 0:
                    continue

                to_a = entity.pos - a
                t = max(0, min(1, to_a.dot(edge) / edge_len_sq))
                closest = a + edge * t

                to_closest = entity.pos - closest
                dist_sq = to_closest.x**2 + to_closest.y**2

                if dist_sq <= entity.radius**2:
                    dist = dist_sq**0.5 if dist_sq > 0 else 0
                    penetration = entity.radius - dist
                    if dist_sq > 0:
                        norm = to_closest.normalize()
                    else:
                        norm = edge.normalize().rotate(math.radians(90)) * -1
                    return (norm, penetration)

            return (None, 0)
        return (norm, penetration)


class Engine:
    def __init__(self):
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
                norm, penetration = hitbox._is_collide(entity, dt)

                # hp = [(p.x, p.y) for p in hitbox.points]
                # arcade.draw_line_strip(hp, arcade.color.RED, 3)
                # arcade.draw_line_strip((hp[0], hp[-1]), arcade.color.RED, 3)
                if norm:
                    vel_dot_norm = entity.velocity.dot(norm)
                    if vel_dot_norm < 0:
                        entity.velocity -= vel_dot_norm * norm
                    
                    if penetration > 0:
                        entity.pos += norm * penetration
                        entity.rect.center_x = entity.pos.x
                        entity.rect.center_y = entity.pos.y

        for entity in self.entities:
            entity.update(dt)


class Window(arcade.Window):
    def __init__(self):
        super().__init__(800, 600, "game for game jam")
        self.pos = Vec2(200, 400) 
        self.vel = Vec2(100, -50)
        self.r = 25    
        self.a = Vec2(500, 350)
        self.b = Vec2(180, 150)
        dp = self.a-self.b
        self.norm = dp.normalize().rotate(math.radians(90))
    
    def collide(self):
        # norm90 = self.norm.rotate(math.radians(90)).normalize()
        # angle = self.norm.angle(self.vel)
        # new = norm90.rotate()
        # new = new.normalize()
        print(self.vel)
        self.vel += -2*self.norm* self.vel
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

