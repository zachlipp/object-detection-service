import base64
from io import BytesIO

import numpy as np
from PIL import Image

from image_processing import encode_rendered_image, pad_image_id


def test_pad_image_id():
    res = pad_image_id("1")
    assert len(res) == 12
    assert res == "0" * 11 + "1"


class FakeDetections:
    # Returns a mock 4-pixel image
    def render(self):
        return [np.array([[12, 240], [240, 12]]).astype(np.uint8)]


def test_encode_rendered_image():
    detections = FakeDetections()
    arr = detections.render()[0]
    b64enc = encode_rendered_image(detections)
    b64dec = base64.b64decode(b64enc)
    stream = BytesIO(b64dec)
    im0 = Image.fromarray(arr)
    im1 = Image.open(stream)
    assert np.allclose(np.array(im0), np.array(im1))
