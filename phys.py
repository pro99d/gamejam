from base_classes import Vec2
import math
import arcade
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

class Window(arcade.Window):
    def __init__(self):
        super().__init__(800, 600, "game for game jam")
        self.pos = Vec2(200, 200) 
        self.vel = Vec2(100, 100)
        self.r = 25    
        self.a = Vec2(500, 350)
        self.b = Vec2(180, 350)
        self.norm = Vec2(0, -1)
    
    def collide(self):
        norm90 = pass
        angle = -self.vel.angle(Vec2(1, 0)) - self.norm.angle(Vec2(1, 0))
        
        d = math.degrees(angle)
        print(d)
        cos = math.cos(angle)
        sin = math.sin(angle)
        print(math.degrees(self.vel.angle(Vec2(1, 0))))
        self.vel.x = self.vel.x * cos + self.vel.y * sin
        self.vel.y = self.vel.x * cos - self.vel.y * sin
        print(math.degrees(self.vel.angle(Vec2(1, 0))))

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

