# Python version can be changed, e.g.
# FROM python:3.8
# FROM docker.io/fnndsc/conda:python3.10.2-cuda11.6.0
FROM docker.io/python:3.11.0-slim-bullseye

LABEL org.opencontainers.image.authors="FNNDSC <dev@babyMRI.org>" \
      org.opencontainers.image.title="My ChRIS Plugin" \
      org.opencontainers.image.description="A ChRIS plugin to remove texts from image"

ARG SRCDIR=/usr/local/src/pl-image_textRemove
WORKDIR ${SRCDIR}

COPY requirements.txt .
RUN pip install -r requirements.txt
RUN apt-get update
RUN apt-get install ffmpeg libsm6 libxext6  -y

COPY . .
ARG extras_require=none

RUN pip install ".[${extras_require}]" \
    && cd / && rm -rf ${SRCDIR}
WORKDIR /

CMD ["image_textRemove"]
