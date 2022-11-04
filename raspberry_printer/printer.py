from PIL import Image, ImageFont, ImageDraw
from datetime import datetime
import subprocess

from raspberry_printer.dither import DitherApply
from raspberry_printer.utils import set_bluetooth_config
from raspberry_printer.image import generate_image
from raspberry_printer.ci_chang import make_kai_xin_learning_text


def call_printer(src, text, is_github_type=False, github_type="Issue"):
    img = generate_image(src, text)
    d = DitherApply(img.size, img.load())
    imgHexStr = d.make_image_hex_str()
    data = ""
    print("Starting print")
    ser = set_bluetooth_config("/dev/rfcomm1")
    hexlen = hex(int(len(imgHexStr) / 96) + 3)[2:]
    # little-endian for the length of hex lines
    fronthex = hexlen
    endhex = "0"
    if len(hexlen) > 2:
        fronthex = hexlen[1:3]
        endhex += hexlen[0:1]
    else:
        endhex += "0"
    # start command with data length
    ser.write(
        bytes.fromhex(
            ("1D7630003000" + fronthex + endhex).ljust(32, "0") + imgHexStr[0:224]
        )
    )
    ########## CALL SPEAKER ###########
    now = datetime.now()
    if is_github_type and now.hour > 8 and now.hour < 21: # if I am sleeping do not call SPEAKER
        try:
           subprocess.check_output(['micli', '5-3', f"哈哈哈哈哈，您有新的{github_type}请注意查收"]) 
        except Exception as e:
            print(f"Wrong call the speaker {str(e)}")
    # send the image data in chunks
    for i in range(32 * 7, len(imgHexStr), 256):
        str = imgHexStr[i : i + 256]
        if len(str) < 256:
            str = str.ljust(256, "0")
        ser.write(bytes.fromhex(str))
    print("Print is over")


if __name__ == "__main__":
    text = make_kai_xin_learning_text([49, 50, 51])
    call_printer(None, text)
