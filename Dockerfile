# syntax=docker/dockerfile:1

FROM python:3.8-slim-buster


LABEL authors = "Michael C Ryan - spacetime.engineer@gmail.com"

RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-dev \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-setuptools \
    python3-venv \
    git \
    && apt-get clean

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir numpy pandas panel ecosound matplotlib bokeh



#TODO: Add authenitcation configuration variables to be passed as build or runtime arguments.

RUN git clone https://github.com/xaviermouy/PAM-viewer.git



#TODO: Fix WORKDIR situation. Currently, the WORKDIR is set to PAM-viewer, but the PAM-viewer.py file is not found.

WORKDIR PAM-viewer

CMD [ "python3", "PAM-viewer/PAM-viewer.py" ]


# Docker Run Command : docker run -it --rm -p 5006:5006 pam-viewer

# Docker Build Command : docker build -t pam-viewer .

# Docker Push Command : docker push pam-viewer

# Docker Pull Command : docker pull pam-viewer
