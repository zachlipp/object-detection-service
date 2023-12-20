# Image detection service

This repository implements an image detection service leveraging ultralytics' YOLOv5 model. I produced it to demonstrate how to build a machine learning web service, including unit and integration tests, containerized building and serving, dependency management, and static analysis (including type checking). I originally developed this project for an interview.

## Developer tools
- docker
- kubectl
- [pre-commit](https://pre-commit.com/)
- [act](https://github.com/nektos/act)
- kind
- jq

To contribute, install these tools. Then install the pre-commit hooks with `pre-commit install`, and install the correct versions of the developer python packages with `pip3 install -r requirements.dev.txt`.

## The service

This repository manages an image detection web service that exposes three endpoints:
- `get_image`, which returns the COCO image corresponding to the provided ID
- `process_image`, which accepts an optional argument `scaling_factor` to scale the image. The goal for this endpoint was to demonstrate how to accept optional arguments.
- `predict`, which returns predicted object segmentations for the provided image. **Images must be processed before they can be predicted.**

Because this web server is built using FastAPI, an OpenAPI schema is automatically available at `/openapi.json`, with rendered specifications at `/redoc` and `/docs`. View them with `make run` and then open `http://localhost:1337/docs`.

I leverage the COCO128 image detection dataset and the YOLOv5s model. There's a tradeoff between Docker image size and startup time, I opt for a larger image with a quicker start by pre-downloading the image dataset and model at build time. As well, I start with ultralytics' own docker image as my base image to save time managing dependencies.

### Using the service

Once the container is running (`make run`), use `curl` through the `Makefile` to actually run requests through the model:
- `make get_image`
- `make process_image`
- `make predict`
- You may want to use `make save-detection-image` and `make view-detection-json` to simplify seeing the results of `make predict`. These require the tool `jq`.

## Testing

This repository contains some unit test and integration tests for the service. They are run in Docker with `make test`. This docker image is built on top of the development image, meaning we get to keep our build cache from before - this greatly speeds up build times.

## CI Pipeline

This repository contains Github Actions for linting, testing, and building. Moreover, it also supports running these locally with `make-run-actions-locally`.

## Kubernetes

As a part of this project, I wanted to produce a simple example of how to deploy this service in Kubernetes. I wrote a script to create a Kubernetes cluster with kind, running a local docker image registry, and using that registry in the local cluster to run images. Run with `make create-cluster`, then `make push`, `make deploy`, and `make port-forward` to explore the Kubernet-ized service at `localhost:1338`.

## Gotchas
- I haven't tested this service on an Intel CPU, and as of now it only supports ARM for Apple Silicon. Intel support should just require changing the base ultralytics image and altering the `make run-actions-locally` command.
- The endpoints are a bit of a mess. Two return JPG byte streams, one returns a JSON payload with a b64encoded PNG. This should be rectified. The byte streams are nice because you can actually view the image in your browser, though.
- I could expose more options in `process_image`; I just wanted to show the pattern for how to do it.
- The CI pipelines need some love. For example, we probably want to build less often than each push...especially if we're also testing on each push, which necessarily builds the image, too.
- There are very few docstrings. I compromised and focused on type annotations instead.
