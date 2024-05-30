# syntax=docker/dockerfile:1

# This Dockerfile is used to create a Docker image that runs the SoundScope application.
FROM python:3.9-slim-buster

# Metadata
LABEL authors = "Michael C Ryan - spacetime.engineer@gmail.com, michael.c.ryan@noaa.gov"

# Set the working directory to /soundscope
WORKDIR /soundscope

# Install required libraries.
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


# Upgrade pip to the latest version.
RUN pip install --no-cache-dir --upgrade pip

# Clone the PSD-PAB-SoundScope repository.
RUN git clone https://github.com/mryan11/PSD-PAB-SoundScope.git

# Change directory to the recently cloned PSD-PAB-SoundScope.
RUN cd PSD-PAB-SoundScope

# Copy contents of PSD-PAB-SoundScope into WORKDIR
COPY . .

# Install all required libraries. Note: These version numbers were aquired from a $ pip freeze command (FYI).
RUN pip install -r requirements.txt

# Remove the PSD-PAB-SoundScope directory because it is no longer needed.
# RUN rm -rf PSD-PAB-SoundScope

# Run the application.
CMD [ "python", "soundscope.py" ]


# To build and run with Docker use the following commands (Testing purposes only): 

#     Build image : $ docker build -t soundscope .
#     Run container : $ docker run -it --rm -p 5006:5006 -v /tmp/.X11-unix:/tmp/.X11-unix -e DISPLAY=unix$DISPLAY soundscope