.PHONY: build run_docker kill lint mypy build_test test open_docs create_cluster push deploy port_forward get_image view_image process_image predict view_detection_image view_detection_json run_actions_locally

# For windows support, use WSL :)
PROCESSOR=$(shell uname -p)
ifeq (${PROCESSOR}, arm)
	ARCH=arm64
else
	ARCH=cpu
endif

build:
	docker build --build-arg ARCH=${ARCH} -t localhost:5001/detection -f docker/Dockerfile .

run: build
	docker run -d --rm --name detection -p 1337:1337 --name detection localhost:5001/detection

kill:
	docker kill detection

lint:
	ruff check . --fix

mypy:
	mypy src

build_test: build
	docker build -t detection-test --build-arg BASE_IMAGE=localhost:5001/detection -f docker/Dockerfile.test .

test: build_test
	docker run --rm --name detection-test detection-test

# works on mac
open_docs:
	open http://localhost:1337/docs

# Interactive usage once docker is running
get_image:
	curl localhost:1337/get_image/144 -o outputs/raw.jpg

view_image:
	open http://localhost:1337/get_image/144

process_image:
	curl -X POST localhost:1337/process_image -d '{"image_id": "144", "scaling_factor": 0.5}' -H 'Content-Type: application/json' -o outputs/processed.jpg

predict:
	curl -X POST localhost:1337/predict -d '{"image_id": "144"}' -H 'Content-Type: application/json' > outputs/detection.json

view_detection_image: predict
	cat outputs/detection.json | jq -r '.image' | base64 -d > outputs/detection.png
	open outputs/detection.png

view_detection_json: predict
	cat outputs/detection.json | jq '.image = "redacted_for_readability"'

# Kubernetes commands
create_cluster:
	./k8s/kind_with_registry.sh

push: build
	docker push localhost:5001/detection

deploy:
	kubectl apply -f k8s/deployment.yaml

port_forward:
	kubectl port-forward service/detection 1338:1337

run_actions_locally:
	act --container-architecture linux/amd64
