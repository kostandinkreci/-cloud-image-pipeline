from io import BytesIO
from PIL import Image

def make_thumbnail(image_bytes: bytes, size=(200, 200)) -> bytes:
    img = Image.open(BytesIO(image_bytes))
    img.thumbnail(size)
    out = BytesIO()
    img.convert("RGB").save(out, format="JPEG")
    return out.getvalue()
