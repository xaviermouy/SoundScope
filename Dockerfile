# syntax=docker/dockerfile:1

FROM python:3.9-slim-buster


LABEL authors = "Michael C Ryan - spacetime.engineer@gmail.com"


WORKDIR /home

RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-dev \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-setuptools \
    python3-venv \
    git \
    python3-tk \
    libportaudio2 \
    && apt-get clean

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir numpy pandas panel ecosound matplotlib bokeh holoviews hvplot loguru sounddevice


RUN git clone https://github.com/mryan11/PSD-PAB-SoundScope.git
RUN cd PSD-PAB-SoundScope
# Copy contents into image/container.
COPY . .
RUN rm -rf PSD-PAB-SoundScope
CMD [ "python", "soundscope.py" ]


# Docker Run Command : docker run -it --rm -p 5006:5006 soundscope

# Docker Build Command : docker build -t soundscope .

# Docker Push Command : docker push soundscope

# Docker Pull Command : docker pull soundscope
