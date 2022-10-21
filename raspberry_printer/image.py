from PIL import Image, ImageFont, ImageDraw
from raspberry_printer.config import FONT_RESOURCE, WIDTH


def generate_image(src, text, font=FONT_RESOURCE):
    """
    base function from https://github.com/j178 great thanks
    """
    if src is not None:
        img = Image.open(src)
    elif text is not None:
        # add ----- in front and end
        text = "-" * 27 + "\n" + text + "\n"
        text = text + " " * 27 * 5
        font_size = 20
        font = ImageFont.truetype(FONT_RESOURCE, font_size)
        # 1. 计算 384 的宽度一行能显示多少个 font_size 的字符：中文 13.5 个，英文 27 个
        # 2. 计算 text 需要多少行
        # 3. 计算总共的高度: 行数 * 30
        content = ""
        line_length = 0
        for i, c in enumerate(text):
            if c == "\n":
                line_length = 0
                content += "\n"
                continue
            elif ord(c) <= 256:
                l = 0.5
            else:
                l = 1
            if line_length + l > WIDTH // font_size - 2:
                content += "\n"
                line_length = 0
            line_length += l
            content += c

        line_cnt = content.count("\n") + 1
        img = Image.new("RGB", (WIDTH, (font_size + 2) * line_cnt), "white")
        draw = ImageDraw.Draw(img)
        draw.text((0, 0), str(content), fill="black", font=font)
    else:
        raise Exception("Either src or text must be provided")
    return img
