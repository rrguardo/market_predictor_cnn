
import PIL
from PIL import Image


def encode_data(data):
    img = PIL.Image.new('RGB', (100, 100), color=0)
    img.putdata(data=data)
    img.show()
