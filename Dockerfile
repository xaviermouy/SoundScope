# syntax=docker/dockerfile:1

FROM python:3.9-slim-buster


LABEL authors = "Michael C Ryan - spacetime.engineer@gmail.com"

# Set up working directory.
WORKDIR /home

# Houskeeping.
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
    x11-xserver-utils \
    && apt-get clean


RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir numpy pandas panel ecosound matplotlib bokeh holoviews hvplot loguru sounddevice pipenv

RUN git clone https://github.com/mryan11/PSD-PAB-SoundScope.git
RUN cd PSD-PAB-SoundScope
# Copy contents into image/container.
COPY . .


RUN rm -rf PSD-PAB-SoundScope
CMD [ "python", "soundscope.py" ]



# Docker Run Command (testing): 

#     $ docker run -it --rm -p 5006:5006 -v /tmp/.X11-unix:/tmp/.X11-unix -e DISPLAY=unix$DISPLAY soundscope

# Docker Run Command : 

#     $ docker run -it --rm -p 5006:5006 soundscope

# Docker Build Command 
    
#     $ docker build -t soundscope .



# The main problem with this dockerfile is that it is not able to run the GUI application unless I remove tkinter which I am ok with. Panel has a solution which I can implament.
# The other problem is that I need pipenv to lock down the python library versions becasue I value the purpose of the pipfile.lock/pipfile however I dont want insinuate that this can be run without docker. I just needed the version numbers.
# in reality ythe port audio library is required to run this application and it lives outside the scope of anythin pipenv can well define.

