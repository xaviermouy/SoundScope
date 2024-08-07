<p align="center">
	<img src="/images/SoundScopeWelcome.png" width="300" />
</p>

# What is SoundScope ?
SoundScope is a python-based software that facilitates the visualization and manual verification of detections from automatic whale and fish sound detectors (or any other sound detectors). 
It allows to display and navigate through detections time series, filter and sort by classification confidence, and dynamically produce spectrograms of the detections. SoundScope was initially
created in the [Juanes Lab](https://juaneslab.weebly.com/) at the University of Victoria and is currently being developped at the [Passive Acoustic Branch of NOAA's Northeast Fisheries Science Center](https://www.fisheries.noaa.gov/new-england-mid-atlantic/endangered-species-conservation/passive-acoustic-research-northeast#:~:text=We%20use%20passive%20acoustic%20technologies,affected%20by%20human%2Dmade%20sounds). 

SoundScope is still under heavy development. Please don't hesitate to reach out if you want to use it or want to help with the development. 

[![Youtube link](https://img.youtube.com/vi/80ZeSBCuZ4U/0.jpg)](https://www.youtube.com/watch?v=80ZeSBCuZ4U)

# How to use it ?

There are 2 ways to use SoundScope:

### Download the latest binary 
This is the easiest way as it does not require to install anything. The binaries are uploaded in this Google folder: [SoundScope binaries](https://drive.google.com/drive/folders/1QbgE7wPl62MbmT1tnLElolxzb44AaAhy?usp=sharing)
Download the latest zip file, unzip it, and double click on soundscope.exe to launch the application.

### Clone the Github repository
This is more involved as it requires to install python and required python libraries. For instructions see the "Development notes" section below. 

# Input data format:
Currently, SoundScope uses netCDF files as input. The data format in the ndtCDF files follows the structure of the [Annotation](https://github.com/xaviermouy/ecosound/blob/master/ecosound/core/annotation.py) and [Measurement](https://github.com/xaviermouy/ecosound/blob/master/ecosound/core/measurement.py) objects defined by the [ecosound](https://github.com/xaviermouy/ecosound) library. 
More documentation describing how to create these netCDF files will be added in the near future. In the meantime, you can have a look at the script [convert_acodet2netcdf.py](https://github.com/xaviermouy/SoundScope/blob/main/utils/convert_acodet2netcdf.py) in the "utils" folder which converts outputs from the [ACODET detector](https://github.com/vskode/acodet) to the SoundScope format.

An example of netCDF file can be found in the folder [here](https://drive.google.com/drive/folders/1UCbsveXWZnqgaYKTtJ3XdINJCT15SGun?usp=drive_link). 
You can open it directly in SoundScope. Note that it will allow you to play around with the detection plots, but will not be able to display the spectrogram of selected detections because it won't have access to the original audio data.

To examine the structure of the netCDF file you can open it in python with ecosound:

```python
from ecosound.core.annotation import Annotation

annot = Annotation()
annot.from_netcdf(r'.\SoundScope_data_examples\SoundScape_detections_example.nc')

# all the detection data and metadate are in the pandas dataframe in annot.data
print(annot.data)

``` 
The code above requires to have ecosound installed. To install ecosound use the command: **pip install ecosound**

# Found a bug or want new features?

### Bugs:
If you found a bug please add an entry to the [issues list](https://github.com/xaviermouy/SoundScope/issues) with the label "**bug**". Please include as much information as possible.

### New features:
If you want new functionalities to be added to SoundScope, add an entry to the [issues list](https://github.com/xaviermouy/SoundScope/issues) with the label "**enhancement**". Use the
thumbs-up emoji (👍) to boost the priority of a new features.

# Development notes

This application was developed with a conda-python3.9 enviornment. The build directions are coming soon. For now refer to the Dockerfile. It utilizes the panel/holoviz library to operate on Annotation objects.  


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

    $ ddocker build -t soundscope .

2.) Run container

    $ docker run -it --rm -p 5006:5006 -v /tmp/.X11-unix:/tmp/.X11-unix -e DISPLAY=unix$DISPLAY soundscope
