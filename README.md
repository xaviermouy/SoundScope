# SoundScope

### Warning
To build a development environment there are a few things to consider. First. There are apt-get packages that are required and so only binaries or docker seem to be worthwhile deployment options.

I built with anaconda and it worked but pipenv seems to lock my environment up so much that I cant accsess apt-get packages. This may be a user confiuration problem but in any event I will need to solve this ifn we want pipenv to be useful.

pipenv has only been useful for freezing a pipfile.lock and using it to make a requirements.txt. Other than that it serves no purpose yet.





### Build development environment with anaconda:


- If using anaconda, create a python 3.9 environment and from a vscode instance you can execute code from that environment by pressing ctrl-shift-p




### Clone SoundScope

- To run development build just clone and run the python3 implementation.

    $ git clone https://github.com/mryan11/PSD-PAB-SoundScope.git


- Navigate to repo directory :

    $ cd soundscope


### Run SoundScope

- Run soundscope:

    $ panel serve soundscope.py --show --autoreload

- or just..

    $ python soundscope.py


### Build development environment with requirements.txt:


    $ pip install -r requirements.txt


To build and run binaires:

- Make sure to work with the binary branch which contains extra code to optimize the binaries.

1.) First, install pyinstaller:

    $ pip install pyinstaller

2.) Next, run this command to generate a dist directory where the exe will be provided 

- If using Windows Powershell:

    $ pyinstaller -i  images\SoundScopeLogo.png --collect-all holoviews --collect-all param .\soundscope.py

- If using Linux (Unstable Incomplete testing):

    $ pyinstaller -i  images\SoundScopeLogo.png --collect-all holoviews --collect-all param soundscope.py

3.) Copy over the images directory to the dist folder.

    $ mv images dist/images





To build and run with Docker:

1.) Build image:

    $ docker build -t soundscope .

2.) Run container

    $ docker run -it --rm -p 5006:5006 -v /tmp/.X11-unix:/tmp/.X11-unix -e DISPLAY=unix$DISPLAY soundscope
