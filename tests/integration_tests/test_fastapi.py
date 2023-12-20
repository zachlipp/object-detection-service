from io import BytesIO

from fastapi.testclient import TestClient
from main import app
from PIL import Image


class TestGetImage:
    def test_get_valid_image(self):
        with TestClient(app) as client:
            # Test known good image
            response = client.get("/get_image/144")
            assert response.status_code == 200
            stream = BytesIO(response.content)
            # Test is valid image
            _ = Image.open(stream)

    def test_get_invalid_image(self):
        with TestClient(app) as client:
            response = client.get("/get_image/1")
            assert response.status_code == 404


class TestProcessImage:
    def test_process(self):
        with TestClient(app) as client:
            response = client.post("/process_image", json={"image_id": "144"})
            assert response.status_code == 200
            stream = BytesIO(response.content)
            # Test is valid image
            _ = Image.open(stream)

    def test_process_accepts_arg(self):
        with TestClient(app) as client:
            response = client.post(
                "/process_image", json={"image_id": "144", "scaling_factor": 0.5}
            )
            assert response.status_code == 200
            stream = BytesIO(response.content)
            # Test is valid image
            _ = Image.open(stream)

    def test_scaling_factor_out_of_bounds(self):
        with TestClient(app) as client:
            response = client.post(
                "/process_image", json={"image_id": "144", "scaling_factor": 1000}
            )
            assert response.status_code == 422

    def test_process_image_not_found(self):
        with TestClient(app) as client:
            response = client.post("/process_image", json={"image_id": "1"})
            assert response.status_code == 404


class TestRunImageObjectDetection:
    def test_image_object_detection(self):
        with TestClient(app) as client:
            # Process first, then predict
            process_response = client.post("/process_image", json={"image_id": "144"})
            assert process_response.status_code == 200
            detection_response = client.post("/predict", json={"image_id": "144"})
            assert detection_response.status_code == 200
            detection = detection_response.json()
            assert "request_id" in detection
            assert "compute_time" in detection
            assert "payload" in detection
            assert len(detection["payload"]) > 0
            assert "image" in detection
