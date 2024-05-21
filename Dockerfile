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
    && apt-get clean

# Install package manager and required python libraries. 
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir numpy pandas panel ecosound matplotlib loguru bokeh tk

# Untested after ths line ; We will need to download/unzip repo and navigate to application directory.
# Next we just run the file with python.
RUN git clone https://github.com/xaviermouy/SoundScope.git 
RUN cd SoundScope-master

CMD [ "python", "soundscope.py" ]


# Docker Run Command

#    $ docker run -it --rm -p 5006:5006 soundscope

# Docker Build Command 
    
#     $ docker build -t soundscope .

# Docker Push Command
    
#    $ docker push soundscope

# Docker Pull Command 
    
#    $ docker pull soundscope
