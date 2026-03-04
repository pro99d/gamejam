import arcade
import base64
from PIL import Image


class ImageLoader:
    @staticmethod
    def to_file(image: Image.Image, path: str):
        data = []
        x, y = image.size
        data += [x, y] + list(image.tobytes())
        data = base64.b64encode(bytes(data))
        with open(path, "wb+") as f:
            f.write(data)

    @staticmethod
    def from_file(path):
        with open(path, "rb") as f:
            data = f.read()
        data = iter(base64.b64decode(data))
        x = int(next(data))
        y = int(next(data))
        img_raw = []
        for _ in range(x*y-1):
            img_raw.append(next(data))
        image = Image.frombytes('1', (x, y), bytes(img_raw))
        return image


if __name__ == "__main__":
    image = arcade.load_image(
        ':resources:/gui_basic_assets/checkbox/blue_check.png')
    ImageLoader.to_file(image, "image.cdt")
    print(ImageLoader.from_file("image.cdt"))
