import base64
import io
from PIL import Image, ImageTk

photos = list()

def load(base64data, size, **kw):
    msg = base64data
    msg = base64.b64decode(msg)
    buf = io.BytesIO(msg)
    img = Image.open(buf).resize(size)
    photo = ImageTk.PhotoImage(img, **kw)
    photos.append(photo)
    return photo