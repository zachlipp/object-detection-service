.PHONY: build run-docker kill-docker lint build-test run-test open-docs create-cluster push deploy port-forward

build:
	docker build -t localhost:5001/detection -f docker/Dockerfile .

run: build
	docker run --rm --name detection -p 1337:1337 --name detection localhost:5001/detection

kill:
	docker kill detection

lint:
	ruff check . --fix

mypy:
	mypy src

build-test: build
	docker build -t detection-test --build-arg BASE_IMAGE=localhost:5001/detection -f docker/Dockerfile.test .

test: build-test
	docker run --rm --name detection-test detection-test

# works on mac
open-docs:
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

extract-detection-image: predict
	cat outputs/detection.json | jq -r '.image' | base64 -d > outputs/detection.png

view-detection-json: predict
	cat outputs/detection.json | jq '.image = "redacted_for_readability"'

# Kubernetes commands
create-cluster:
	./k8s/kind_with_registry.sh

push: build
	docker push localhost:5001/detection

deploy:
	kubectl apply -f k8s/deployment.yaml

port-forward:
	kubectl port-forward service/detection 1338:1337

run-actions-locally:
	act --container-architecture linux/amd64
