from PIL.Image import new
import math
import json
import arcade
import arcade.gl
from arcade.pymunk_physics_engine import PymunkPhysicsEngine

sprite_all_draw = arcade.SpriteList()
waiting_list: list[arcade.SpriteSolidColor] = []

phys = PymunkPhysicsEngine((0, 0), 0.7)

class Vec2:
    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y
    def dict(self):
        return {"x":self.x, "y":self.y}

    def __add__(self, other):
        if isinstance(other, Vec2):
            return Vec2(self.x+other.x, self.y+other.y)
        elif type(other) in [int, float]:
            return Vec2(self.x+other, self.y+other)
    def magnitude(self):
        return math.sqrt(self.x**2+self.y**2)
    def rotate(self, angle):
        sin = math.sin(angle)
        cos = math.cos(angle)
        x = round(self.x*cos - self.y * sin, 15)
        y = round(self.x*sin + self.y * cos, 15)
        return Vec2(x, y)

    def normalize(self):
        mag = self.magnitude()
        x = self.x / mag
        y = self.y / mag
        return Vec2(x, y)

    def angle(self, other):
        if isinstance(other, Vec2):
            return math.acos(self.dot(other)/(self.magnitude()*other.magnitude()))
    def dot(self, other):
        if isinstance(other, Vec2):
            return self.x*other.x + self.y * other.y
    def __sub__(self, other):
        if isinstance(other, Vec2):
            return Vec2(self.x-other.x, self.y-other.y)
        elif type(other) in [int, float]:
            return Vec2(self.x-other, self.y-other)
    def __rdiv__(self, other):
        if type(other) in [int, float]:
            return Vec2(other/self.x, other/self.y)
    def __div__(self, other):
        if isinstance(other, Vec2):
            return Vec2(self.x/other.x, self.y/other.y)
        elif type(other) in [int, float]:
            return Vec2(self.x/other, self.y/other)
    def __truediv__(self, other):
        return self.__div__(other)
    def __mul__(self, other):
        if isinstance(other, Vec2):
            return Vec2(self.x*other.x, self.y*other.y)
        elif type(other) in [int, float]:
            return Vec2(self.x*other, self.y*other)
    def __repr__(self) -> str:
        return f"Vec2(x= {self.x}, y= {self.y})"
    def __list__(self):
        return [self.x, self.y]
    __rmul__ = __mul__
    __radd__ = __add__

class Rect:
    def __init__(self, pos: Vec2, size: Vec2, ctx):
        self.pos = pos
        self.ctx = ctx
        self.size = size
        self.frag = """
            #version 330
            out vec4 fragColor;
            void main()
            {
                fragColor = vec4(1.0);
            }
        """
        self.quad = arcade.gl.geometry.quad_2d(
            size=(size.x, size.y), pos=(pos.x, pos.y))
        self.update_program()
    def __setitem__(self, key, val):
        self.prog[key] = val

    def update_pos(self, pos: Vec2):
        self.quad = arcade.gl.geometry.quad_2d(
            size=(self.size.x, self.size.y), pos=(pos.x, pos.y))

    def update_program(self):
        self.prog = self.ctx.program(
            vertex_shader="""
            #version 330
            in vec2 in_vert;
            void main()
            {
                gl_Position = vec4(in_vert, 0., 1);
            }

            """,

            fragment_shader=self.frag
        )

    def draw(self):
        self.quad.render(self.prog)

class Entity:
    def __init__(self, pos: Vec2, size: Vec2, color: tuple[float, float, float], 
                 moment_of_inertia: float = PymunkPhysicsEngine.MOMENT_INF,
                 collision_type: str = None, max_velocity: float = None, type_= PymunkPhysicsEngine.DYNAMIC, friction= 0.7):
        self.pos: Vec2 = pos
        self.size = size
        self.angle = 0
        self.rect: arcade.Sprite = arcade.SpriteSolidColor(self.size.x, self.size.y, self.pos.x, self.pos.y, color, self.angle)
        sprite_all_draw.append(self.rect)
        self.velocity: Vec2 = Vec2(0.0, 0.0)
        self.color = color
        self.radius = min(size.x, size.y) / 2
        self.die_calls = []
        self.on_collide_events = []
        phys.add_sprite(self.rect,
                        friction=friction,
                        moment_of_inertia=moment_of_inertia,
                        damping=0.01,
                        collision_type=collision_type,
                        max_velocity=max_velocity,
                        body_type= type_,
                        elasticity= 0.05)

    def collide_line(self, a: Vec2, b: Vec2):
        c = self.pos
        d = abs((b.x-a.x)*(c.y-a.y) - (b.y-a.y)*(c.x-a.x))/ math.sqrt((b.x-a.x)**2 + (b.y-a.y)**2)
        return d <= self.radius

    
    def update(self, dt: float):
        self.rect.center_x += self.velocity.x*dt
        self.rect.center_y += self.velocity.y*dt
        # self.rect.center_x= self.pos.x
        # self.rect.center_y= self.pos.y
        self.pos = Vec2(self.rect.position[0], self.rect.position[1])
        self.rect.angle = self.angle
    
    def die(self):
        for call in self.die_calls:
            call(self)
        if self.rect in sprite_all_draw:
            self.rect.center_y = -1000
            self.rect.center_x = -1000
            sprite_all_draw.remove(self.rect)
        self.rect.remove_from_sprite_lists()

    def collide(self, other):
        return bool(self.rect.rect.intersection(other.rect.rect))
    def to_json(self):
        data = {
            "pos": self.pos.dict(),
            "size": self.size.dict(),
            "color": self.color,
            "velocity": self.velocity.dict(),
            "angle": self.angle
        }
        return data
    def from_json(self, d):
        data = json.loads(d)
        self.angle = data['angle']
        v = data['velocity']
        p = data['pos']
        s = data['size']
        self.velocity = Vec2(v['x'], v['y'])
        self.size = Vec2(s['x'], s['y'])
        self.pos = Vec2(p['x'], p['y'])
        self.color = data['color']
        self.rect.center_x= self.pos.x
        self.rect.center_y= self.pos.y
        self.rect.angle = self.angle

class Bar:
    def __init__(self, pos: Vec2, size: Vec2, color, bg_color, value, max_value):
        self.pos = pos
        self.size = size
        self.color = color
        self.bg_color = bg_color
        self.value = value
        self.max_value = max_value
        self.text_pos = Vec2(
            pos.x + size.x/2,
            pos.y + size.y/2 - 5,
        )

    def update_pos(self, pos):
        self.pos = pos
        self.text_pos = Vec2(
            pos.x + self.size.x/2,
            pos.y + self.size.y/2 - 5,
        )


    def draw(self):
        arcade.draw_lbwh_rectangle_filled(self.pos.x, self.pos.y, self.size.x, self.size.y, self.bg_color)
        arcade.draw_lbwh_rectangle_filled(self.pos.x, self.pos.y, self.size.x*self.value/self.max_value, self.size.y, self.color)
        arcade.draw_text(f"{round(self.value, 2)}/{round(self.max_value, 2)}", self.text_pos.x, self.text_pos.y)

if __name__ == "__main__":
    e = Entity(Vec2(0, 0), Vec2(1, 1), [0, 0, 0])
    js = e.to_json()
    e.angle = 1.0
    e.pos = Vec2(1, 2)
    e.size = Vec2(2, 3)
    e.color = [1, 2, 3]
    e.velocity = Vec2(2, 4)
    e.from_json(js) 
    print(e.to_json())
