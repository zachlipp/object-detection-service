import glob
import os
import time
from base64 import b64encode
from io import BytesIO
from typing import Any, Callable, Dict, List, Optional, Set
from uuid import uuid4

from PIL import Image

from yolo_stubs import Detections


def postprocess_yolo_outputs(detections: Detections) -> List[Dict[str, Any]]:
    """The default outputs from YOLO models are very peculiar

    In particular, this project prefers to return bounding box
    predictions in the form:

    {
        "bbox": {
            "origin": [x, y],
            "size": [width, height],
        },
        "class": predicted_class,
        "score": score
    }

    This function does the work to convert from yolo to this format; however, it would
    be much better to just output the desired format from the model itself
    """
    df = detections.pandas().xyxy[0]
    df["width"] = df["xmax"] - df["xmin"]
    df["height"] = df["ymax"] - df["ymin"]
    df["origin_x"] = df["xmin"] + 0.5 * df["width"]
    df["origin_y"] = df["ymin"] + 0.5 * df["height"]
    records = df.to_dict(orient="records")
    payload = [
        {
            "bbox": {
                "origin": [r["origin_x"], r["origin_y"]],
                "size": [r["width"], r["height"]],
            },
            "class": r["name"],
            "score": r["confidence"],
        }
        for r in records
    ]
    return payload


def predict(model: Callable, image_id: str):
    with Image.open(f"processed/{image_id}.jpg") as image:
        start = time.time()
        results = model(image)
        b64results = encode_rendered_image(results)
        # Time all of the model and data manipulation
        end = time.time()
        request_id = str(uuid4())
        compute_time = end - start
        return {
            "request_id": request_id,
            "compute_time": compute_time,
            "image": b64results,
            "payload": postprocess_yolo_outputs(results),
        }


def encode_rendered_image(detections: Detections) -> bytes:
    stream = BytesIO()
    rendered = Image.fromarray(detections.render()[0])
    rendered.save(stream, format="PNG")
    encoded = b64encode(stream.getvalue())
    return encoded


def get_all_images(image_dir: str) -> Set[str]:
    image_paths = glob.glob(f"{image_dir}/*.jpg")
    # Two passes here isn't necessary, but gives us some clarity
    image_filenames = [os.path.basename(x) for x in image_paths]
    image_ids = [os.path.splitext(x)[0] for x in image_filenames]
    return set(image_ids)


def pad_image_id(image_id: str) -> str:
    """Fills the left digits of the ID with 0s.
    This implementation requires all images to
    have twelve-character filenames"""
    return image_id.rjust(12, "0")


def process_image(
    image_path: str, scaling_factor: Optional[float] = None, **kwargs
) -> str:
    with Image.open(image_path, "r") as image:
        processed = image
        if scaling_factor:
            new_dims = (
                int(image.width * scaling_factor),
                int(image.height * scaling_factor),
            )
            processed = image.resize(size=new_dims)
        image_id = os.path.splitext(os.path.basename(image_path))[0]
        processed.save(f"processed/{image_id}.jpg")
        return f"processed/{image_id}.jpg"
