# PAM-viewer

To run development build just clone and run the python3 implementation.

    $ git clone https://github.com/xaviermouy/SoundScope.git


Navigate to repo directory :

    $ cd soundscope-master


Run soundscope:

    $ panel serve soundscope.py --show --autoreload

or

    $ python soundscope.py



To Generate Binaires:

- Make sure to work with the binary branch which contains extra code to optimize the binaries.

1.) First, install pyinstaller:

    $ pip install pyinstaller

2.) Next, run this command to generate a dist directory where the exe will be provided.

    $ pyinstaller -i  images\SoundScopeLogo.png --collect-all holoviews --collect-all param .\soundscope.py

3.) Copy over the images directory to the dist folder.