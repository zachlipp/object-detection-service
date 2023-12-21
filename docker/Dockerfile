ARG ARCH

FROM ultralytics/yolov5:v7.0-${ARCH}

RUN apt-get update && \
  apt-get install -y unzip

RUN curl -L -o yolov5s.pt \
  https://github.com/ultralytics/yolov5/releases/download/v7.0/yolov5s.pt

RUN curl -L -o coco.zip \
  https://ultralytics.com/assets/coco128.zip \
  && unzip coco.zip

RUN mkdir processed

COPY requirements.txt .

RUN pip3 install -r requirements.txt --extra-index-url https://download.pytorch.org/whl/cpu

COPY src .

ENTRYPOINT uvicorn --host 0.0.0.0 --port 1337 main:app
