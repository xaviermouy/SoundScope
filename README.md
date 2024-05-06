# PAM-viewer

To run development build just clone and run the python3 implementation.

    $ git clone https://github.com/xaviermouy/SoundScope.git


Navigate to repo directory :

    $ cd soundscope-master


Run soundscope:

    $ panel serve soundscope.py --show --autoreload

or

    $ python soundscope.py


Generate Binaires:

    $ pip install pyinstaller

    $ pyinstaller --collect-all holoviews --collect-all param .\soundscope.py