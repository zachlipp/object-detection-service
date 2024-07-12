<h1 align="center">Image Detection Service</h1>
<h3 align="center">Using YOLOv5 to segment COCO128 images</h3>

![](https://github.com/zachlipp/object-detection-service/blob/figs/figs/flow.png)

## 📝 Overview
This service identifies the objects in an image.

## 💥 Features
### 📸 **Image processing**
Users can scale the image up or down before providing it to the model. The `process_image` function can be extended to support arbitrary image transformations.

### 🪄 **Object detection**
The model identifies known objects in the image, and returns bounding boxes and confidence scores for each prediction.

### ⏩ **Quick startup**
The Docker image bakes the model weights and image dataset into an early build layer. This means running the image once it is built - or modifying the code - can work much faster.

## ⚡ Quick Start
- Clone this repository: `git clone https://github.com/zachlipp/object_detection_service.git`
- Build and run the server (requires `docker`, `make`): `make run`
- Process an example image: `make process_image`
- Predict bounding boxes: `make predict`
- Display the processed image and bounding boxes: `make view_detection_image`. These require the tools `curl` and `jq` (See <a href="#-contributing">Contributing</a> for details.)

## 📖 Endpoints
This service exposes port `1337` to the host with the following endpoints:
- `/docs` and `/redoc`, which display FastAPI's generated OpenAPI spec for the endpoints (the spec itself is available at `/openapi.json`)
- `/get_image`, which parses the URI from `GET` requests to show users what image from COCO they're processing, e.g. [http://localhost:1337/get_image/144](http://localhost:1337/get_image/144)
- `/process_image`, which accepts `POST` requests which indicate the image to prepare for prediction and how to process it
- `/predict`, which accepts `POST` requests which indicate the processed image to process

## 🤝 Contributing
### 🤙 Issues are preferred
I have some ideas on the future of this project. Your proposed changes may not match those ideas. Let's discuss it in an issue to see if we can align on something before you write a bunch of code.

### 🧰 Devtools
This project uses the following tools:
- docker
- make
- curl
- [pre-commit](https://pre-commit.com/)
- [act](https://github.com/nektos/act)
- jq
- kind
- kubectl

To use all of the commands in the `Makefile`, you'll need to install these tools.

Next, install the pre-commit hooks with `pre-commit install`, and install the correct versions of the developer python packages with `pip3 install -r requirements.dev.txt`. This installs Python-specific developer tools, namely `ruff` and `mypy`.

### 👷 Useful development commands
- `make test` runs unit tests and integration tests
- `make run-actions-locally` uses `act` to simulate a local run of GitHub Actions
- To run the application on a local Kubernetes cluster (using `kind`), use:
    - `make create_cluster`
    - `make push` (builds the image and pushes it to a local registry)
    - `make deploy`
    - `make port_forward` (access the service on `localhost:1338`)

## 🥁 Personal rating + reflection 🥁
<details open="">
<summary>Personal rating</summary>
<h3>❤️❤️❤️️❤️🖤 (4/5)</h3>
<h3>Reflection</h3>

<p>This is a great example of how to get value out of a pre-trained model. It's also a good reflection of a lot of my skills - creating Python servers, test suites, developer UX, and even some basic CI/CD workflows.</p>

<p>The highlight for me here is the test pipeline:
<ul>
    <li>Tests run in a container built on-top of the development container, so we get the speedup from our development cache in a reproducible environment.</li>
    <li>Tests are separated by functionality (`integration_tests`, `unit_tests`). This separates the layers of tests in an understandable way and provides clear guidance when extending the test suite.</li>
    <li>Tests "just work." Test discovery and relative imports in Python isn't always the easiest nut to crack. This is now a reference implementation for my future work.</li>
</ul>

<h3>Areas for improvement</h3>
<ul>
    <li><strong>The endpoints could be more consistent</strong>. Two return JPG byte streams, one returns a JSON payload with a b64encoded PNG. I think consistency here might be preferable (e.g. all return images by default, but the prediction JSON is available with a special payload or the like.)</li>
    <li><strong><code>/process_image</code> doesn't do much for now</strong>. This is more of a placeholder than a useful part of the pipeline. Extending it with more options would make it feel more essential.</li>
    <li><strong>The Python functions could use more docstrings</strong>. I focused on this README, tests, and type annotations instead; but docstrings are still valuable in a codebase.</li>
</ul>
</details>

## 🤗 Kudos
- The Ultralytics team for publishing the [YOLOv5 model](https://github.com/ultralytics/yolov5) (and Docker images for it!)
