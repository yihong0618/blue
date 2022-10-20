from PIL import Image, ImageFont, ImageDraw

from raspberry_printer.config import DITHERBRIGHTNESS, DITHERCONTRAST


class DitherApply:
    def __init__(self, size, pixels):
        self.size = size
        self.pixels = pixels

    def get_value(self, y, x):
        return int(
            (self.pixels[x, y][0] + self.pixels[x, y][1] + self.pixels[x, y][2]) / 3
        )

    def set_value(self, y, x, v):
        self.pixels[x, y] = (v, v, v)

    def nudge_value(self, y, x, v):
        v = int(v)
        self.pixels[x, y] = (
            self.pixels[x, y][0] + v,
            self.pixels[x, y][1] + v,
            self.pixels[x, y][2] + v,
        )

    def _make_apply(self):
        w, h = self.size
        brightness = float(DITHERBRIGHTNESS)
        contrast = float(DITHERCONTRAST) ** 2
        for y in range(h):
            for x in range(w):
                for i in range(3):
                    r, g, b = self.pixels[x, y]
                    arr = [r, g, b]
                    arr[i] += (brightness - 0.5) * 256
                    arr[i] = (arr[i] - 128) * contrast + 128
                    arr[i] = int(min(max(arr[i], 0), 255))
                    self.pixels[x, y] = (arr[0], arr[1], arr[2])

        for y in range(h):
            BOTTOM_ROW = y == h - 1
            for x in range(w):
                LEFT_EDGE = x == 0
                RIGHT_EDGE = x == w - 1
                i = (y * w + x) * 4
                level = self.get_value(y, x)
                new_level = (level < 128) * 0 + (level >= 128) * 255
                self.set_value(y, x, new_level)
                error = level - new_level
                if not RIGHT_EDGE:
                    self.nudge_value(y, x + 1, error * 7 / 16)
                if not BOTTOM_ROW and not LEFT_EDGE:
                    self.nudge_value(y + 1, x - 1, error * 3 / 16)
                if not BOTTOM_ROW:
                    self.nudge_value(y + 1, x, error * 5 / 16)
                if not BOTTOM_ROW and not RIGHT_EDGE:
                    self.nudge_value(y + 1, x + 1, error * 1 / 16)
        return self.pixels

    def make_image_hex_str(self):
        self._make_apply()
        size_x, size_y = self.size
        img_bin_str = ""

        for y in range(size_y):
            for x in range(size_x):
                r, g, b = self.pixels[x, y]
                if r + g + b > 600:
                    img_bin_str += "0"
                else:
                    img_bin_str += "1"

        # start bits
        img_bin_str = "1" + "0" * 318 + img_bin_str
        # convert to hex
        return hex(int(img_bin_str, 2))[2:]
