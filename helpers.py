from base_classes import Vec2
from dataclasses import dataclass
import base64
import arcade

class Shader:
    def __init__(self, frag: str, ctx, vert: str | None= None, w: int= 1920, h: int= 1080):
        self.ctx = ctx
        self.quad_fs = arcade.gl.geometry.quad_2d_fs()
        self.w = w
        self.h = h
        self.tex = self.ctx.texture((w, h))
        self.fbo = self.ctx.framebuffer(color_attachments=[self.tex])

        self.fbo.clear()

        if not vert:
            vert_sh = """
                #version 330
                in vec2 in_vert;
                void main(){
                    gl_Position = vec4(in_vert, 0., 1.);
                }
            """
        else:
            with open(vert) as f:
                vert_sh = f.read()
        with open(frag) as f:
            frag_sh = f.read()
        self.prog = self.ctx.program(
                vertex_shader= vert_sh,
                fragment_shader= frag_sh,
                )
    def resize(self, w, h):
        self.tex = self.ctx.texture((w, h))
        self.fbo = self.ctx.framebuffer(color_attachments=[self.tex])
    def __enter__(self):
        self.fbo.__enter__()

    def __exit__(self, *_, **__):
        self.fbo.__exit__(*_, **__)

    def draw(self):
        self.tex.use(0)
        self.quad_fs.render(self.prog)

    def clear(self, color= (0, 0, 0)):
        self.fbo.clear(color= color)

    
    def __setitem__(self, key, value):
        self.prog[key] = value

@dataclass
class EnemyData:
    pos: Vec2
    type_: int

@dataclass
class WallData:
    pos: Vec2
    size: Vec2
@dataclass
class Spawn:
    pos: Vec2

class Level:
    def __init__(self):
        self.walls: list[WallData] = []
        self.enemies: list[EnemyData] = []
        self.spawn: Spawn= Spawn(Vec2(0, 0))

class LevelLoader:
    @staticmethod
    def from_str(string: bytes) -> Level:
        level = base64.b64decode(string).decode()
        """
        format:
            type/type data
        types:
            spawn:
                type data:
                    posx/posy
            wall:
                type data:
                    posx/posy/sizex/sizey
            enemy:
                type data:
                    posx/posy/enemy type
        """
        content = Level()
        level = level.split("/")
        pointer = 0
        while True:
            dtype = level[pointer]
            pointer += 1
            if dtype == "":
                break
            dtype = int(dtype)
            match dtype:
                case 0: # spawn point
                    if pointer +1 >= len(level):
                        raise ValueError("Wrong level format!")
                    x = float(level[pointer])
                    pointer += 1
                    y = float(level[pointer])
                    pointer += 1
                    content.spawn = Spawn(Vec2(x, y))

                case 1: # wall
                    if pointer+3 >= len(level):
                        raise ValueError("Wrong level format!")
                    x = float(level[pointer])
                    pointer += 1
                    y = float(level[pointer])
                    pointer += 1
                    size_x = float(level[pointer])
                    pointer += 1
                    size_y = float(level[pointer])
                    pointer += 1
                    wd = WallData(Vec2(x, y), Vec2(size_x, size_y))
                    content.walls.append(wd)
                case 2: # enemy
                    if pointer+2 >= len(level):
                        raise ValueError("Wrong level format!")
                    x = float(level[pointer])
                    pointer += 1
                    y = float(level[pointer])
                    pointer += 1
                    type_ = int(level[pointer])
                    pointer += 1
                    ed = EnemyData(Vec2(x, y), type_)
                    content.enemies.append(ed)
                case _:
                    raise ValueError("Wrong level format!")
        return content
    @staticmethod
    def to_str(content: Level) -> bytes:
        level = ""
        level += "0/"
        level += f"{content.spawn.pos.x}/"
        level += f"{content.spawn.pos.y}/"
        for item in content.walls:
            level += "1/"
            level += f"{item.pos.x}/"
            level += f"{item.pos.y}/"
            level += f"{item.size.x}/"
            level += f"{item.size.y}/"
        for item in content.enemies:
            level += "2/"
            level += f"{item.pos.x}/"
            level += f"{item.pos.y}/"
            level += f"{item.type_}/"
        level = level.encode()
        level = base64.b64encode(level)
        return level

    @staticmethod
    def load_level(path: str) -> Level:
        with open(path, 'rb') as file:
            content = file.read()
        return LevelLoader.from_str(content)
    @staticmethod
    def save_level(path: str, level: Level):
        lvl_string = LevelLoader.to_str(level)
        with open(path, 'wb') as file:
            file.write(lvl_string)

if __name__ == "__main__":
    # level.spawn = Spawn(Vec2(100, 100))
    # level.walls.append(WallData(Vec2(200, 200), Vec2(50, 50)))
    level = LevelLoader.load_level("level")
    print(level.walls)
    print(level.spawn)
