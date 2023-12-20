import os
from contextlib import asynccontextmanager

import torch
from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse

from image_processing import get_all_images, pad_image_id, predict, process_image
from pydantic_models import DetectionRequest, ProcessRequest

loaded_at_startup = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the pre-downloaded model from disk
    loaded_at_startup["model"] = torch.hub.load(
        os.getcwd(), "yolov5s", source="local", device="cpu"
    )
    image_dir = "coco128/images/train2017"
    loaded_at_startup["raw_images"] = get_all_images(image_dir)
    loaded_at_startup["raw_image_dir"] = image_dir
    loaded_at_startup["processed_images"] = set()
    yield
    loaded_at_startup.clear()


app = FastAPI(lifespan=lifespan)


@app.get("/get_image/{image_id}")
async def handle_get_image(image_id: str):
    image_id = pad_image_id(image_id)
    if image_id not in loaded_at_startup["raw_images"]:
        return JSONResponse(status_code=404, content={"message": "Item not found"})
    else:
        image_path = f"{loaded_at_startup['raw_image_dir']}/{image_id}.jpg"
        return FileResponse(image_path)


@app.post("/process_image")
async def handle_process_image(process_request: ProcessRequest):
    image_id = pad_image_id(process_request.image_id)
    if image_id not in loaded_at_startup["raw_images"]:
        return JSONResponse(status_code=404, content={"message": "Item not found"})
    else:
        image_path = f"{loaded_at_startup['raw_image_dir']}/{image_id}.jpg"
        new_file = process_image(image_path, process_request.scaling_factor)
        loaded_at_startup["processed_images"].add(image_id)
        return FileResponse(new_file)


@app.post("/predict")
async def handle_object_detection(detection_request: DetectionRequest):
    image_id = detection_request.image_id
    image_id = pad_image_id(image_id)
    if image_id not in loaded_at_startup["processed_images"]:
        return JSONResponse(
            status_code=404,
            content={"message": f"{image_id} not found in processed images"},
        )
    else:
        results = predict(loaded_at_startup["model"], image_id)
        return results
